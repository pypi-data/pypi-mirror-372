# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Highest level tests for GitLab hook support.

These tests instantiate `Hook` and thus need a real repository.
Some use the API like in the hg-git wrapper, and thus need to monkey patch
a request recorder in.
"""
import io
import json
import pytest
import requests
import urllib3

from heptapod.testhelpers import (
    RepoWrapper,
    as_bytes,
)
from ..hooks import (
    Hook,
    PreReceive,
    PostReceive,
)
from .. import prune_reasons

ZERO_SHA = b"0" * 20

parametrize = pytest.mark.parametrize


def make_repo(base_dir, name):
    secret = base_dir.join('secret')
    secret.write("TEHTOKEN")
    wrapper = RepoWrapper.init(
        base_dir.join(name),
        config=dict(heptapod={'gitlab-shell': str(base_dir),
                              'gitlab-internal-api-secret-file': str(secret),
                              }),
    )
    # by default, ui.environ IS os.environ (shared) but that isn't true
    # in WSGI contexts. In that case, it is a plain dict, the WSGI environment
    # indeed. For these tests, we need them to be independent.
    wrapper.repo.ui.environ = {}
    return wrapper


def request_recorder(records, responses):
    """Record sent requests and treat each from the given responses.

    :param responses: a list of :class:`request.Response` instances or
                      :class:`Exception` instances. In the latter case,
                      the exception is raised instead of returning the
                      response.
    :param records: list to which the recorder appends the request that is
                    being sent.
    """
    def request(hook, meth, subpath, params, **kwargs):
        records.append((meth, subpath, params, kwargs))
        resp = responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp

    return request


def make_response(status_code, body):
    """Create a :class:`request.Response` instance.

    :param body: must be `bytes`.
    """
    resp = requests.models.Response()
    resp.status_code = status_code
    resp.raw = io.BytesIO(body)
    return resp


def make_json_response(obj, status_code=200):
    return make_response(status_code, json.dumps(obj).encode())


def update_environ(repo, **kwargs):
    repo.ui.environ.update((as_bytes(k), as_bytes(v))
                           for k, v in kwargs.items())


@parametrize('user_key', ('numeric', 'gl_id'))
def test_post_receive_params(tmpdir, user_key):
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    update_environ(
        repo,
        GL_REPOSITORY='project-1024',
    )
    if user_key == 'numeric':
        update_environ(repo, HEPTAPOD_USERINFO_ID='23')
    else:
        update_environ(repo, HEPTAPOD_USERINFO_GL_ID='user-23')

    changes = {}, {
        b'branch/newbr': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
        b'topic/default/zz': (b"23cafe45" + b"0" * 12, b"1234" + b"b" * 16),
    }

    params = hook.params(changes)
    assert params['identifier'] == 'user-23'
    assert set(params['changes'].splitlines()) == {
        b'23cafe45000000000000 1234bbbbbbbbbbbbbbbb topic/default/zz',
        b'00000000000000000000 beef1234deadaaaaaaaa branch/newbr'}
    assert params['gl_repository'] == 'project-1024'


@parametrize('with_mr', ('with-mr', 'no-mr'))
def test_pre_receive_params(tmpdir, with_mr):
    # string value was neat for pytest output, prefering a bool from now on
    with_mr = with_mr == 'with-mr'
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PreReceive(repo)

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='2',
        GL_REPOSITORY='project-3145926',
    )
    if with_mr:
        update_environ(repo, HEPTAPOD_ACCEPT_MR_IID='123')

    changes = 'prune-reasons-are-ignored', {
        b'topic/default/with-a-dash': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
        b'branch/default': (b"23cafe45" + b"0" * 12, b"1234" + b"b" * 16),
    }
    params = hook.params(changes)

    assert params['user_id'] == '2'
    assert set(params['changes'].splitlines()) == {
        b'23cafe45000000000000 1234bbbbbbbbbbbbbbbb branch/default',
        b'00000000000000000000 beef1234deadaaaaaaaa topic/default/with-a-dash'}
    assert params['gl_repository'] == 'project-3145926'
    assert params['project'].encode() == repo.root
    if with_mr:
        assert params['accept_mr_iid'] == 123
    else:
        assert 'accept_mr_iid' not in params


def test_post_receive_params_prune(tmpdir):
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='2',
        GL_REPOSITORY='project-3145926',
    )
    pruned = {
        b'topic/default/mytop': prune_reasons.TopicPublished(b'cafe5678'),
        b'master': prune_reasons.BookmarkRemoved(b'1234'),
        b'branch/other': prune_reasons.BranchClosed([
            (b'239acf', [b'968de76'])
        ])
    }
    git_changes = {
        b'topic/default/with-a-dash': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
        b'branch/default': (b"23cafe45" + b"0" * 12, b"1234" + b"b" * 16),
    }
    params = hook.params((pruned, git_changes))

    assert params['identifier'] == 'user-2'
    assert set(params['changes'].splitlines()) == {
        b'23cafe45000000000000 1234bbbbbbbbbbbbbbbb branch/default',
        b'00000000000000000000 beef1234deadaaaaaaaa topic/default/with-a-dash'}
    assert params['gl_repository'] == 'project-3145926'

    # GitLab branches are serialized in base64, since have unknown encoding
    assert json.loads(params['hg_prunes']) == {
        'topic_published': {'dG9waWMvZGVmYXVsdC9teXRvcA==': 'cafe5678'},
        'bookmark_removed': {'bWFzdGVy': '1234'},
        'branch_closed': {'YnJhbmNoL290aGVy': [['239acf', ['968de76']]]},
    }


def test_post_receive_params_push_opts(tmpdir):
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='2',
        GL_REPOSITORY='project-3145926',
    )
    git_changes = {
        b'topic/default/with-a-dash': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
    }
    params = hook.params(({}, git_changes,
                          {'ci.skip': '', 'ci.variable': 'something'}))

    assert params['identifier'] == 'user-2'
    assert set(params['changes'].splitlines()) == {
        b'00000000000000000000 beef1234deadaaaaaaaa topic/default/with-a-dash'}
    assert params['gl_repository'] == 'project-3145926'

    assert json.loads(params['push_options']) == [
        'ci.skip', 'ci.variable=something']


def test_post_receive_handle_response_gl_12_2(tmpdir):
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    out = hook.handle_response(
        200,
        # example taken from the functional tests
        {u'broadcast_message': None,
         u'reference_counter_decreased': True,
         u'merge_request_urls': [
             {u'url': u'http://localhost:3000/root/'
              'test_project_1583330760_9216309/merge_requests/1',
              u'branch_name': u'topic/default/antelope',
              u'new_merge_request': False}
         ]})[1]
    out = [l.strip() for l in out.splitlines() if l.strip()]
    assert out == [
        b'View merge request for topic/default/antelope:',
        b'http://localhost:3000/root/test_project_1583330760_9216309/'
        b'merge_requests/1']

    broadcast = "Check out the new tutorial"
    out = hook.handle_response(
        200,
        {u'broadcast_message': broadcast,
         u'reference_counter_decreased': True,
         })[1]
    out = (l.strip() for l in out.splitlines() if l.strip())
    assert any(broadcast.encode() in l for l in out)

    project_created = "Congrats!"
    out = hook.handle_response(
        200,
        {u'project_created_message': project_created,
         u'reference_counter_decreased': True,
         })[1]
    out = (l.strip() for l in out.splitlines() if l.strip())
    assert any(project_created.encode() in l for l in out)

    # GitLab internal API gives warnings as a unique string
    # see lib/api/helpers/internal_helpers.rb
    warnings = "You probably shouldn't have"
    out = hook.handle_response(
        200,
        {u'warnings': warnings,
         u'reference_counter_decreased': True,
         })[1]
    out = (l.strip() for l in out.splitlines() if l.strip())
    assert any(warnings.encode() in l for l in out)


def test_post_receive_handle_response_gl_12_3(tmpdir):
    wrapper = make_repo(tmpdir, 'proj.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    out = hook.handle_response(
        200,
        # example taken from the functional tests
        {u'messages': [
            {u'message': (
                u'To create a merge request '
                u'for topic/default/ant, visit:\n'
                u'http://localhost:3000/root/test_project/merge_requests/new'
                u'?merge_request%5Bsource_branch%5D=topic%2Fdefault%2Fant'),
             u'type': u'basic',
             },
            {u'message': u'This is a TESTING SERVER',
             u'type': u'alert',
             },
        ]})[1]
    out = [l.strip() for l in out.splitlines() if l.strip()]
    assert out == [
        b'To create a merge request for topic/default/ant, visit:',
        b'http://localhost:3000/root/test_project/merge_requests/new'
        b'?merge_request%5Bsource_branch%5D=topic%2Fdefault%2Fant',
        b'=' * 72,
        b'This is a TESTING SERVER',
        b'=' * 72,
    ]


def test_integration_post_receive(tmpdir, monkeypatch):
    records = []
    responses = [
        make_json_response(
            {u'broadcast_message': None,
             u'reference_counter_decreased': True,
             u'merge_request_urls': [
                 {u'url': u'http://localhost:3000/root/'
                  'test_project_1583330760_9216309/merge_requests/1',
                  u'branch_name': u'topic/default/antelope',
                  u'new_merge_request': False}
             ]}),
        requests.exceptions.Timeout("1 ns is too much ;-)"),
    ]

    monkeypatch.setattr(Hook, 'gitlab_internal_api_request',
                        request_recorder(records, responses))

    repo_wrapper = make_repo(tmpdir, 'repo.hg')
    repo = repo_wrapper.repo

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='23',
        GL_REPOSITORY='project-1024',
    )

    hook = PostReceive(repo_wrapper.repo)
    changes = {}, {
        b'branch/newbr': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
        b'topic/default/zz': (b"23cafe45" + b"0" * 12, b"1234" + b"b" * 16),
    }

    return_code, out, err = hook(changes)
    assert return_code == 0
    out = [l.strip() for l in out.splitlines() if l.strip()]
    assert out == [
        b'View merge request for topic/default/antelope:',
        b'http://localhost:3000/root/test_project_1583330760_9216309/'
        b'merge_requests/1']

    return_code, out, err = hook(changes)
    assert return_code == 1
    assert err == 'GitLab is unreachable'


def test_integration_unix_socket(tmpdir):
    repo_wrapper = make_repo(tmpdir, 'repo.hg')
    repo = repo_wrapper.repo

    repo.ui.setconfig(b'heptapod', b'gitlab-internal-api-url',
                      b'http+unix://nosuch.socket')

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='23',
        GL_REPOSITORY='project-1024',
    )
    hook = PreReceive(repo_wrapper.repo)

    with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
        # cannot use hook() because it would treat exceptions uniformly,
        # to return an error message without crashing, let's go lower level:
        hook.gitlab_internal_api_request('GET', subpath=hook.api_endpoint,
                                         params={})

    inner_exc = exc_info.value.args[0]
    assert inner_exc.__class__ == urllib3.exceptions.ProtocolError
    inner_inner_exc = inner_exc.args[1]

    # If FileNotFoundError is raised, it means that the request
    # was actually fired down the requests/urllib3 stack, and hence many
    # API compatibilities have not happened. This covers in particular
    # the compat problem between urllib3 and requests-unixsockets <= 0.3.0
    # raises a Type error much earlier (about the `chunked` kwarg).
    # This is still not a proof that it actually works, we'd need to spawn
    # a server to do that (perhaps `nc` could do it).
    assert inner_inner_exc.__class__ == FileNotFoundError


def test_integration_pre_receive(tmpdir, monkeypatch):
    records = []
    responses = [make_json_response({u'message': "yes, granted!",
                                     u'status': True,
                                     },
                                    status_code=200),
                 make_json_response({u'status': True},
                                    status_code=200),
                 make_json_response({u'message': "go away!",
                                     u'status': False,
                                     },
                                    status_code=401),
                 make_response(504, b"Bad gateway :-("),
                 requests.exceptions.ConnectionError("Failed"),
                 ]
    monkeypatch.setattr(Hook, 'gitlab_internal_api_request',
                        request_recorder(records, responses))

    repo_wrapper = make_repo(tmpdir, 'repo.hg')
    repo = repo_wrapper.repo

    update_environ(
        repo,
        HEPTAPOD_USERINFO_ID='23',
        GL_REPOSITORY='project-1024',
    )

    hook = PreReceive(repo_wrapper.repo)
    changes = {}, {
        b'branch/newbr': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
        b'topic/default/zz': (b"23cafe45" + b"0" * 12, b"1234" + b"b" * 16),
    }

    return_code, out, err = hook(changes)
    assert return_code == 0
    assert out == b'yes, granted!'

    return_code, out, err = hook(changes)
    assert return_code == 0
    assert out == b''

    return_code, out, err = hook(changes)
    assert return_code == 1
    assert err == 'go away!'

    return_code, out, err = hook(changes)
    assert return_code == 1
    assert err == 'API is not accessible'

    return_code, out, err = hook(changes)
    assert return_code == 1
    assert err == 'GitLab is unreachable'


def test_empty_changes(tmpdir):
    hook = PostReceive(make_repo(tmpdir, 'repo.hg').repo)
    code, out, err = hook(())
    assert code == 0
    assert not out
    assert not err


def test_str_bytes(tmpdir):
    # these are used in various messages
    hook = PostReceive(make_repo(tmpdir, 'repo.hg').repo)
    assert b'post-receive' in hook.__bytes__()
    assert 'post-receive' in str(hook)


def test_missing_secret(tmpdir):
    repo = RepoWrapper.init(tmpdir).repo
    shell = tmpdir.join('heptapod-shell').ensure(dir=True)
    repo.ui.setconfig(b'heptapod', b'gitlab-shell', str(shell).encode())
    with pytest.raises(RuntimeError) as exc_info:
        PostReceive(repo)
    assert "secret-file" in exc_info.value.args[0]

    # defaulting to gitlab-shell secret if available
    shell.join('.gitlab_shell_secret').write('myseekret\n')
    hook = PostReceive(repo)
    assert hook.gitlab_secret == 'myseekret'


def test_hook_missing_user(tmpdir):
    wrapper = make_repo(tmpdir, 'proj2.hg')
    repo = wrapper.repo
    hook = PreReceive(repo)

    repo.ui.environ[b'GL_REPOSITORY'] = b'project-1024'
    with pytest.raises(ValueError) as exc_info:
        hook.environ()
    assert 'User id' in exc_info.value.args[0]

    # and that gets catched, does not break the process
    code, out, err = hook(dict(master=(0, 1)))
    assert code != 0


def test_hook_missing_project(tmpdir):
    wrapper = make_repo(tmpdir, 'proj2.hg')
    repo = wrapper.repo
    hook = PostReceive(repo)

    repo.ui.environ[b'HEPTAPOD_USERINFO_ID'] = b'3'
    with pytest.raises(ValueError) as exc_info:
        hook.environ()
    assert 'GL_REPOSITORY' in exc_info.value.args[0]

    # and that gets catched, does not break the process
    code, out, err = hook(dict(master=(0, 1)))
    assert code != 0


def test_hook_skip(tmpdir):
    wrapper = make_repo(tmpdir, 'proj2.hg')
    repo = wrapper.repo
    repo.ui.environ[b'HEPTAPOD_SKIP_GITLAB_HOOK'] = b'pre-receive'
    hook = PreReceive(repo)
    assert hook(dict(master=(0, 1))) == (0, b'', '')

    repo.ui.environ[b'HEPTAPOD_SKIP_GITLAB_HOOK'] = b'post-receive'
    hook = PostReceive(repo)
    assert hook(dict(master=(0, 1))) == (0, b'', '')


def test_hook_skip_all(tmpdir):
    wrapper = make_repo(tmpdir, 'proj2.hg')
    repo = wrapper.repo
    repo.ui.environ[b'HEPTAPOD_SKIP_ALL_GITLAB_HOOKS'] = b'no'
    hook = PreReceive(repo)
    # it's been called and failed because of lack of User id
    assert hook(dict(master=(0, 1)))[0] == 1

    repo.ui.environ[b'HEPTAPOD_SKIP_ALL_GITLAB_HOOKS'] = b'yes'
    hook = PreReceive(repo)
    assert hook(dict(master=(0, 1))) == (0, b'', '')
