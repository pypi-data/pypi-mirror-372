# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import pytest
from mercurial import (
    error,
)
from mercurial.hgweb.common import (
    ErrorResponse,
)

from ..wsgi import HgServe
from ..testhelpers import (
    as_bytes,
    RepoWrapper,
    make_ui,
)

parametrize = pytest.mark.parametrize


def test_missing_repositories_root(tmpdir):
    hgrc_path = tmpdir.join('heptapod.hgrc')
    hgrc_path.write('\n'.join(("[extensions]", "evolve=", "topic=", "")))

    with pytest.raises(ValueError) as exc_info:
        HgServe(conf_path=str(hgrc_path))

    assert 'heptapod.repositories-root' in exc_info.value.args[0]


def test_missing_conf_file(tmpdir):
    hgrc_path = tmpdir.join('heptapod.hgrc')
    hgrc_path.write('\n'.join(("[extensions]", "evolve=", "topic=", "")))

    with pytest.raises(error.Abort) as exc_info:
        HgServe(conf_path=str(tmpdir.join('does-not-exist')))

    assert b'not found' in exc_info.value.args[0]


def test_missing_secondary_conf_file(tmpdir):
    """Only the first HGRC in path is required."""
    hgrc = tmpdir.join('hgrc')
    repos = tmpdir.join('repositories')
    hgrc.write('\n'.join(('[heptapod]\n',
                          'repositories-root=' + str(repos),
                          )))
    hgs = HgServe(conf_path=':'.join((
        str(hgrc),
        str(tmpdir.join('does-not-exist'))
    )))
    assert hgs.repos_root == as_bytes(repos)


def make_hgserve(repo_root, **config):
    """Return a minimal instance of Hgserve for given repository root.

    :param **conf: allows to pass other settings.
    """
    config.setdefault('heptapod', {})['repositories-root'] = str(repo_root)
    base_ui = make_ui(None, config=config)
    return HgServe(baseui=base_ui)


def test_repositories_root(tmpdir):
    hgs = make_hgserve(tmpdir)
    assert hgs.repos_root == as_bytes(tmpdir)


@parametrize('rate', (0, 2))
def test_gc_rate(tmpdir, rate):
    hgs = make_hgserve(tmpdir,
                       experimental={'web.full-garbage-collection-rate': rate})

    def fake_run(*a):
        return []

    hgs._runwsgi = fake_run

    def process_requests(number):
        for _ in range(number):
            # all we need is to call the server, it doesn't matter how
            [chunk for chunk in hgs({}, None)]

    process_requests(5)
    assert hgs.requests_count == 5

    collections = hgs.gc_full_collections_done
    if rate == 2:
        assert collections == 2
    if rate == 0:
        assert collections == 0


def test_config_from_environ(tmpdir):
    assert 'HEPTAPOD_HGRC' not in os.environ  # checking our premises
    hgrc = tmpdir.join('hgrc')
    repos = tmpdir.join('repositories')
    hgrc.write('\n'.join(('[heptapod]\n',
                          'repositories-root=' + str(repos),
                          )))
    try:
        os.environ['HEPTAPOD_HGRC'] = str(hgrc)
        hgs = HgServe.default_app()
        assert hgs.repos_root == as_bytes(repos)
    finally:
        del os.environ['HEPTAPOD_HGRC']

    # really make sure we won't pollute other tests
    assert 'HEPTAPOD_HGRC' not in os.environ


def test_apply_heptapod_headers(tmpdir):
    hgs = make_hgserve(tmpdir)

    env = {'HTTP_X_HEPTAPOD_PERMISSION_USER': 'permuser',
           'REMOTE_ADDR': '::1'}
    hgs.apply_heptapod_headers(env)
    assert env.get('REMOTE_USER') == 'permuser'

    env = {'HTTP_X_HEPTAPOD_PERMISSION_USER': 'permuser',
           'REMOTE_ADDR': '10.1.2.3'}
    hgs.apply_heptapod_headers(env)
    # TODO we might want to revise this and put an explicit denying user
    # in there, since at least in check_publish, absence of REMOTE_USER
    # is interpreted as running from the command line
    assert 'REMOTE_USER' not in env

    env = {'HTTP_X_HEPTAPOD_GL_REPOSITORY': 'wiki-18',
           'HTTP_X_HEPTAPOD_USERINFO_USERNAME': 'testgr',
           }
    hgs.apply_heptapod_headers(env)
    assert env.get('HEPTAPOD_PROJECT_ID') == '18'
    assert env.get('HEPTAPOD_REPOSITORY_USAGE') == 'wiki'
    assert env.get('GL_REPOSITORY') == 'wiki-18'
    assert env.get('HEPTAPOD_USERINFO_USERNAME') == 'testgr'


def test_load_repo(tmpdir):
    wrapper = RepoWrapper.init(
        tmpdir.join('group').ensure(dir=True)
        .join('proj.hg'))
    wrapper.write_commit('foo', message='Foo')
    hgs = make_hgserve(tmpdir)
    hgs.ui.setconfig(b'heptapod', b'canary', b'yellow')

    repo = hgs.load_repo(b'group/proj.hg', {})
    assert repo[0].description() == b'Foo'

    repo.ui.setconfig(b'heptapod', b'canary', b'red')
    assert repo.ui.config(b'heptapod', b'canary') == b'red'
    assert hgs.ui.config(b'heptapod', b'canary') == b'yellow'


def test_load_repo_not_found(tmpdir):
    hgs = make_hgserve(tmpdir)
    with pytest.raises(ErrorResponse) as exc_info:
        hgs.load_repo(b'does/not/exist', {})

    assert exc_info.value.args[0] == 'Not Found'


@parametrize('header_value,no_git_header_value,expected,no_git_expected',
             (('yes', 'yes', True, True),
              ('yes', 'no', True, False),
              ('no', 'yes', False, False),
              ('no', 'no', False, False),
              ))
def test_load_repo_native_header(header_value, no_git_header_value,
                                 expected, no_git_expected,
                                 tmpdir):
    wrapper = RepoWrapper.init(
        tmpdir.join('group').ensure(dir=True)
        .join('proj.hg'))
    wrapper.write_commit('foo', message='Foo')
    hgs = make_hgserve(tmpdir)
    repo = hgs.load_repo(b'group/proj.hg',
                         env={'HTTP_X_HEPTAPOD_HG_NATIVE': header_value,
                              'HTTP_X_HEPTAPOD_NO_GIT': no_git_header_value,
                              })
    ui = repo.ui
    assert ui.configbool(b'heptapod', b'native') is expected
