# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Integration tests for the GitLab state maintainer with no Git repo.

In this case, "integration" means that we're testing the main methods,
and the whole Hook logic. We may also need to create
complex transactions, with several commits, rebases, phase changes etc.
"""
from __future__ import absolute_import

import contextlib
import pytest
import re

from heptapod.gitlab import hooks
from heptapod.gitlab.prune_reasons import (
    HeadPruneReason,
    BookmarkRemoved,
    BranchClosed,
    TopicPublished,
    WildHeadResolved,
)
from mercurial_testhelpers.repo_wrapper import NULL_ID
from mercurial_testhelpers.util import as_bytes
from heptapod.testhelpers import (
    RepoWrapper,
)
from heptapod.testhelpers.gitlab import (
    patch_gitlab_hooks,
    GitLabStateMaintainerFixture,
)
from heptapod.hooks.tests.utils import switch_user
from hgext3rd.heptapod.branch import (
    set_default_gitlab_branch,
    gitlab_branches,
    read_gitlab_branches,
    write_gitlab_branches,
)
from mercurial import (
    encoding,
    error,
    pycompat,
    scmutil,
    ui as uimod,
)
from heptapod.gitlab.change import (
    GitLabRefChange as GitRefChange,
    ZERO_SHA,
)
from ...no_git import (
    NoGitStateMaintainer,
)
from ..utils import common_config, HEPTAPOD_REQUIRED_HGRC


parametrize = pytest.mark.parametrize


# not covering a log interceptor for tests is not a break of coverage
# perhaps this utility should move to pytest-mercurial
def patch_ui_warnings(monkeypatch, records):  # pragma no cover

    def warn(self, *a):
        records.append(a)

    monkeypatch.setattr(uimod.ui, 'warn', warn)


@contextlib.contextmanager
def gitlab_state_fixture_gen(tmpdir, monkeypatch):
    """Common fixture generator."""
    with GitLabStateMaintainerFixture.init(
            tmpdir, monkeypatch,
            hg_config=common_config(tmpdir)) as fixture:
        fixture.hg_repo_wrapper.set_config('heptapod.native', True)
        yield fixture


@pytest.fixture()
def empty_fixture(tmpdir, monkeypatch):
    """Minimal fixture where the repository is empty."""
    with gitlab_state_fixture_gen(tmpdir, monkeypatch) as fixture:
        yield fixture


@pytest.fixture()
def main_fixture(tmpdir, monkeypatch):
    """A fixture with two public changesets in the Mercurial repository.

    The changesets are kept on the fixture object as additional attributes
    ``base_ctx`` and ``ctx1``.

    It is up to the test using this fixture to share state with GitLab or not.
    """
    with gitlab_state_fixture_gen(tmpdir, monkeypatch) as fixture:
        wrapper = fixture.hg_repo_wrapper
        fixture.base_ctx = wrapper.commit_file('foo',
                                               content='foo0',
                                               message='default0')
        fixture.ctx1 = wrapper.commit_file('foo',
                                           content='foo1',
                                           message="default1")
        wrapper.set_phase('public', ['.'])
        yield fixture


def set_allow_bookmarks(repo_wrapper, value):
    repo_wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.bookmarks-on-named-branches', value)


def set_allow_multiple_heads(repo_wrapper, value):
    repo_wrapper.repo.ui.setconfig(b'heptapod', b'allow-multiple-heads', value)


def set_prune_closed_branches(repo_wrapper, value):
    repo_wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.prune-newly-closed-branches', value)


def test_basic(main_fixture):
    repo = main_fixture.hg_repo_wrapper
    notifs = main_fixture.gitlab_notifs

    repo.command('gitlab-mirror')

    sha = main_fixture.ctx1.hex()
    assert notifs == [
        ('pre-receive', ({}, {b'refs/heads/branch/default': (ZERO_SHA, sha)})),
        ('post-receive', ({},
                          {b'refs/heads/branch/default': (ZERO_SHA, sha)})),
    ]

    assert read_gitlab_branches(repo.repo) == {
        b'branch/default': repo.repo[b'.'].hex()
    }


@parametrize('pushvar', ('skip-ci', 'mr-create'))
def test_pushvars(main_fixture, pushvar):
    wrapper = main_fixture.hg_repo_wrapper
    notifs = main_fixture.gitlab_notifs

    if pushvar == 'skip-ci':
        hookargs = {b'USERVAR_CI.SKIP': b''}
        push_opts = {'ci.skip': ''}
    elif pushvar == 'mr-create':
        hookargs = {b'USERVAR_MERGE_REQUEST.CREATE': b''}
        push_opts = {'merge_request.create': ''}
    # no default case, better have an error instead

    with wrapper.repo.transaction(b'tests') as txn:
        txn.hookargs = hookargs
        wrapper.command('gitlab-mirror')

    sha = main_fixture.ctx1.hex()
    assert notifs == [
        ('pre-receive', ({}, {b'refs/heads/branch/default': (ZERO_SHA, sha)})),
        ('post-receive', ({},
                          {b'refs/heads/branch/default': (ZERO_SHA, sha)},
                          push_opts)),
    ]


def test_alternate_encoding(main_fixture, monkeypatch):
    """Round trip with branch name not in UTF-8.

    It's not clear whether this is valid on the GitLab side, but it should
    be transparent in here: what comes in comes out.
    """
    fixture = main_fixture
    notifs = fixture.gitlab_notifs
    wrapper = fixture.hg_repo_wrapper

    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    # Even though it's been initialized from the `HGENCODING` environment
    # variable, the encoding is a global.
    monkeypatch.setattr(encoding, 'encoding', b'latin-1')

    ctx = wrapper.write_commit('encoded', branch=b'pr\xe9parations')
    wrapper.command('gitlab-mirror')

    # not using existing helpers to avoid making the test tautological
    gitlab_branch = b'branch/pr\xe9parations'
    gitlab_ref = b'refs/heads/' + gitlab_branch
    sha = ctx.hex()

    # Both in GitLab branches state file and in notifs,
    # we have the exact same bytes as provided
    assert notifs == [
        ('pre-receive', ({}, {gitlab_ref: (ZERO_SHA, sha)})),
        ('post-receive', ({}, {gitlab_ref: (ZERO_SHA, sha)})),
    ]
    assert read_gitlab_branches(wrapper.repo)[gitlab_branch] == sha


def test_wiki(main_fixture):
    fixture = main_fixture
    notifs = fixture.gitlab_notifs
    wrapper = fixture.hg_repo_wrapper

    wrapper.repo.ui.environ[b'GL_REPOSITORY'] = b'wiki-251'
    wrapper.command('gitlab-mirror')

    sha = fixture.ctx1.hex()
    # for wikis, we duplicate `branch/default` as `master`
    changes = {}, {b'refs/heads/branch/default': (ZERO_SHA, sha)}
    assert notifs == [
        ('pre-receive', changes),
        ('post-receive', changes),
    ]


def test_tags_simple(main_fixture):
    repo = main_fixture.hg_repo_wrapper
    hg_repo = repo.repo
    notifs = main_fixture.gitlab_notifs
    base_ctx = main_fixture.base_ctx

    # Creation
    repo.command('tag', b'v1.2.3', rev=base_ctx.hex())
    repo.command('gitlab-mirror')

    branches = gitlab_branches(hg_repo)
    assert list(branches) == [b'branch/default']
    first_default_branch_sha = branches[b'branch/default']

    tagged_sha_0 = base_ctx.hex()

    changes = {}, {
        b'refs/heads/branch/default': (ZERO_SHA, first_default_branch_sha),
        b'refs/tags/v1.2.3': (ZERO_SHA, tagged_sha_0),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Modification
    repo.command('tag', b'v1.2.3', rev=b'1', force=True)
    repo.command('gitlab-mirror')

    tagged_sha_1 = hg_repo[1].hex()

    new_default_branch_sha = hg_repo[b'tip'].hex()
    changes = {}, {
        b'refs/heads/branch/default': (first_default_branch_sha,
                                       new_default_branch_sha),
        b'refs/tags/v1.2.3': (tagged_sha_0, tagged_sha_1),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    repo.command('tag', b'v1.2.3', remove=True)
    repo.command('gitlab-mirror')

    last_default_branch_sha = hg_repo[b'tip'].hex()
    changes = {}, {
        b'refs/heads/branch/default': (new_default_branch_sha,
                                       last_default_branch_sha),
        b'refs/tags/v1.2.3': (tagged_sha_1, ZERO_SHA),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_tags_permission(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    hg_repo = wrapper.repo
    base_ctx = fixture.base_ctx

    fixture.activate_mirror()  # we'll need the mirror in-transaction

    wrapper.set_config('web', 'allow-push', 'writer')
    wrapper.set_config('web', 'allow-publish', 'publisher')

    # Publisher can create tag
    switch_user(wrapper, 'publisher')
    with wrapper.tags_sanitizer():
        wrapper.command('tag', b'v1.2.3', rev=base_ctx.hex())
        assert set(hg_repo.tags()) == {b'v1.2.3', b'tip'}

    # With simple write permission, every change in tags is refused
    switch_user(wrapper, 'writer')
    with wrapper.tags_sanitizer(), pytest.raises(error.Abort) as exc_info:
        wrapper.command('tag', b'v6.5.4')
    exc = exc_info.value
    assert b'permission' in exc.args[0]
    assert b'6.5.4' in exc.hint

    with wrapper.tags_sanitizer(), pytest.raises(error.Abort) as exc_info:
        wrapper.command('tag', b'v1.2.3', force=True)
    exc = exc_info.value
    assert b'permission' in exc.args[0]
    assert b'1.2.3' in exc.hint

    with wrapper.tags_sanitizer(), pytest.raises(error.Abort) as exc_info:
        wrapper.command('tag', b'v1.2.3', remove=True)
    exc = exc_info.value
    assert b'permission' in exc.args[0]
    assert b'1.2.3' in exc.hint

    # Publisher can change and remove tags
    switch_user(wrapper, 'publisher')
    with wrapper.tags_sanitizer():
        wrapper.command('tag', b'v1.2.3', force=True)

    with wrapper.tags_sanitizer():
        wrapper.command('tag', b'v1.2.3', remove=True)

    assert set(hg_repo.tags()) == {b'tip'}


def test_tags_escaping_removal(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    hg_repo = wrapper.repo
    notifs = main_fixture.gitlab_notifs

    # a tag with a space character
    hg_tag = b'Version 1.2.3'
    gitlab_tag_ref = b'refs/tags/Version_1.2.3'
    wrapper.command('tag', hg_tag)
    wrapper.command('gitlab-mirror')

    assert set(hg_repo.tags()) == {hg_tag, b'tip'}
    tagged_sha = main_fixture.ctx1.hex()

    branches = gitlab_branches(hg_repo)
    assert list(branches) == [b'branch/default']

    branch_sha1 = branches[b'branch/default']
    changes = {}, {
        b'refs/heads/branch/default': (ZERO_SHA, branch_sha1),
        gitlab_tag_ref: (ZERO_SHA, tagged_sha),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Pushing something else does not count as a tag modification.
    # This asserts that heptapod#464 is fixed.
    branch_sha2 = wrapper.commit_file('something-else').hex()
    wrapper.command('gitlab-mirror')

    changes = {}, {
        b'refs/heads/branch/default': (branch_sha1, branch_sha2),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Change is still possible
    wrapper.command('tag', hg_tag, force=True)
    wrapper.command('gitlab-mirror')
    assert set(hg_repo.tags()) == {hg_tag, b'tip'}
    branch_sha3 = gitlab_branches(hg_repo)[b'branch/default']
    changes = {}, {
        b'refs/heads/branch/default': (branch_sha2, branch_sha3),
        gitlab_tag_ref: (tagged_sha, branch_sha2),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Removal is still possible
    wrapper.command('tag', hg_tag, remove=True)
    wrapper.command('gitlab-mirror')
    assert set(hg_repo.tags()) == {b'tip'}

    branch_sha4 = gitlab_branches(hg_repo)[b'branch/default']
    changes = {}, {
        b'refs/heads/branch/default': (branch_sha3, branch_sha4),
        gitlab_tag_ref: (branch_sha2, ZERO_SHA),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()


def test_tags_obsolete(tmpdir, empty_fixture):
    fixture = empty_fixture

    # we'll need to perform a pull in order to amend a tagged changeset
    # and rebase the tagging changeset in a single transaction.
    src_path = fixture.base_path / 'src.hg'
    src = RepoWrapper.init(src_path, config=common_config(tmpdir))

    dest = fixture.hg_repo_wrapper
    fixture.activate_mirror()

    def dest_pull():
        dest.command('pull', as_bytes(src_path),
                     force=True,
                     remote_hidden=False)

    # Creation
    src.commit_file('foo')

    # no problem on receiving side with obsolescence of changesets
    # that it never received
    src.commit_file('bar')
    src.command("amend", message=b'amend before exchange')
    dest_pull()

    src.command('tag', b'v1.2.3')
    tag_ctx = scmutil.revsingle(src.repo, b'.')
    dest_pull()

    tagged = scmutil.revsingle(src.repo, b'v1.2.3')
    src.update_bin(tagged.node())
    # let's create a topic from the changeset to be amended,
    # so that it will still be visible after amendment.
    src.commit_file('foo', topic='stacked')

    # amending the tagged changeset
    src.update_bin(tagged.node())
    src_path.join("foo", "amending")
    src.command('amend', message=b'amend')
    src.command('rebase', rev=[tag_ctx.hex()])
    rebased_tag_ctx = scmutil.revsingle(src.repo, b'tip')

    with pytest.raises(error.Abort) as exc_info:
        dest_pull()
    assert re.search(br'tag.*v1\.2\.3.*obsolete', exc_info.value.args[0])

    src.prune(rebased_tag_ctx.hex())
    dest_pull()


def test_tip_obsolete(empty_fixture):
    """Since 'tip' is a tag, we don't to refuse making it obsolete."""
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper
    wrapper.commit_file('foo')

    fixture.activate_mirror()  # we'll need the mirror in-transaction

    ctx = wrapper.commit_file('foo')
    wrapper.prune(ctx.hex())  # no error

    # yet the tip of the unfiltered repo is obsolete
    # (if this changes in a future Mercurial version, we may get rid of
    # this assertion)
    assert b'tip' in wrapper.repo.unfiltered()[ctx.node()].tags()


def test_share(main_fixture):
    main_wrapper = main_fixture.hg_repo_wrapper
    base_ctx = main_fixture.base_ctx
    tmpdir = main_fixture.base_path

    # let's start with some commits known to GitLab
    main_wrapper.command('gitlab-mirror')

    # TODO make a helper on fixture for that
    assert set(gitlab_branches(main_wrapper.repo)) == {b'branch/default'}

    # now let's make a share
    dest_wrapper = main_wrapper.share(tmpdir.join('share.hg'))
    dest_wrapper.write_commit('bar', message='other0',
                              branch='other', parent=base_ctx.node())
    dest_wrapper.command('gitlab-mirror')
    # of course, since the write went through another localrepo instance,
    # we need to bypass the cache
    assert set(read_gitlab_branches(main_wrapper.repo)) == {b'branch/default',
                                                            b'branch/other'}


def test_bookmarks(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    # this activates in particular the gitlab-mirror hook
    wrapper.repo.ui.readconfig(HEPTAPOD_REQUIRED_HGRC, trust=True)

    set_allow_bookmarks(wrapper, True)

    base = wrapper.commit_file('foo', message="unbookmarked")
    bk1 = wrapper.commit_file('foo', message="book1")
    bk2 = wrapper.commit_file('foo', message="book2")
    wrapper.command('bookmark', b'zebook1', rev=bk1.hex())
    wrapper.command('bookmark', b'zebook2', rev=bk2.hex())
    assert read_gitlab_branches(wrapper.repo) == {b'branch/default': bk2.hex(),
                                                  b'zebook1': bk1.hex(),
                                                  b'zebook2': bk2.hex()}
    ctx = wrapper.commit_file('foo', message="new default head", parent=base)
    assert read_gitlab_branches(wrapper.repo) == {b'branch/default': ctx.hex(),
                                                  b'zebook1': bk1.hex(),
                                                  b'zebook2': bk2.hex()}

    # and multiple heads are still refused
    with pytest.raises(error.Abort) as exc:
        wrapper.commit_file('foo', message="2nd default head", parent=base)
    assert b'multiple heads' in exc.value.args[0]
    hint_lead, hint_shas = exc.value.hint.split(b': ')
    assert hint_lead == b'2 heads'
    assert ctx.hex()[:12] in set(hint_shas.split())


def test_bookmarks_prune(main_fixture):
    fixture = main_fixture
    server = fixture.hg_repo_wrapper
    base_ctx = fixture.base_ctx
    notifs = main_fixture.gitlab_notifs

    repo = server.repo
    default1_ctx = fixture.ctx1
    server.command('bookmark', b'zebook', rev=base_ctx.hex())
    # not being in a transaction accepts the bookmark immediately
    server.command('gitlab-mirror')

    fixture.clear_gitlab_notifs()

    assert gitlab_branches(repo) == {
        b'branch/default': default1_ctx.hex(),
        b'zebook': base_ctx.hex(),
    }

    fixture.activate_mirror()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(base_ctx.node()) == []
    assert read_gitlab_branches(repo) == {
        b'branch/default': default1_ctx.hex(),
    }

    changes = {b'zebook': BookmarkRemoved(base_ctx.hex())}, {
        b'refs/heads/zebook': (base_ctx.hex(), ZERO_SHA)
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_bookmarks_mask_branch_prune(main_fixture):
    fixture = main_fixture
    server = fixture.hg_repo_wrapper
    notifs = main_fixture.gitlab_notifs
    repo = server.repo
    default_sha = fixture.ctx1.hex()

    server.command('gitlab-mirror')
    # just checking our assumptions
    assert gitlab_branches(repo) == {b'branch/default': default_sha}

    # we need to test the branch masking on a branch
    # that's not the GitLab default (which is protected)
    server.write_commit('foo', branch='other', message='other1')

    fixture.activate_mirror()
    set_allow_bookmarks(server, True)
    head = server.repo[b'tip']
    server.command('bookmark', b'zebook', rev=head.hex())
    head_sha = head.hex()
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        b'zebook': head_sha,
    }

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(head.node()) == []
    assert read_gitlab_branches(repo) == {
        b'branch/default': default_sha,
        b'branch/other': head_sha,
    }

    changes = {b'zebook': BookmarkRemoved(head_sha)}, {
        b'refs/heads/zebook': (head_sha, ZERO_SHA),
        b'refs/heads/branch/other': (ZERO_SHA, head_sha),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_bookmarks_obsolete(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo

    set_allow_bookmarks(wrapper, True)

    draft1 = wrapper.commit_file('foo', message='Initial draft')
    wrapper.command('bookmark', b'zebook', rev=draft1.hex(), inactive=True)
    wrapper.command('gitlab-mirror')

    # just checking our assumptions.
    assert gitlab_branches(repo) == {b'zebook': draft1.hex()}

    # let's get in-transaction
    fixture.activate_mirror()

    draft2 = wrapper.commit_file('foo', message='amended', parent=NULL_ID)
    with pytest.raises(error.Abort) as exc_info:
        wrapper.prune(draft1.hex(), successors=[draft2.hex()])
    assert re.search(br'bookmark.*zebook.*obsolete', exc_info.value.args[0])


def test_bookmarks_dont_mask_default_branch(main_fixture):
    fixture = main_fixture
    server = fixture.hg_repo_wrapper
    repo = server.repo
    notifs = fixture.gitlab_notifs
    sha = fixture.ctx1.hex()

    server.command('gitlab-mirror')
    # just checking our assumptions
    assert gitlab_branches(repo) == {b'branch/default': sha}

    fixture.activate_mirror()
    set_allow_bookmarks(server, True)
    head = server.repo[b'tip']

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', rev=head.hex())

    # the default branch is not pruned
    assert gitlab_branches(repo) == {
        b'branch/default': sha,
        b'zebook': sha,
    }

    changes = {b'refs/heads/zebook': (ZERO_SHA, sha)}
    assert notifs == [('pre-receive', ({}, changes)),
                      ('post-receive', ({}, changes)),
                      ]

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(head.node()) == []
    assert gitlab_branches(repo) == {b'branch/default': sha}
    changes = {b'refs/heads/zebook': (sha, ZERO_SHA)}
    prunes = {b'zebook': BookmarkRemoved(sha)}

    assert notifs == [('pre-receive', (prunes, changes)),
                      ('post-receive', (prunes, changes)),
                      ]


@parametrize('branch_name', ('default', 'other'))
def test_change_gitlab_default_branch(empty_fixture, branch_name):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    wrapper.write_commit('foo', message="other0",
                         branch=branch_name,
                         topic='initial')
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/%s/initial' % branch_name)

    wrapper.set_phase('public', ['.'])
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('branch/' + branch_name)


def test_change_gitlab_default_branch_nothing_new(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    wrapper.write_commit('foo', message="other0",
                         branch='default',
                         topic='initial')
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/default/initial')

    wrapper.write_commit('foo', message="same gitlab branch")
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/default/initial')


def test_topical_gitlab_default_branch_one_more_topic(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    wrapper.write_commit('foo', message="other0",
                         branch='default',
                         topic='top1')
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/default/top1')

    wrapper.write_commit('foo', message="same gitlab branch", topic="top2")
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/default/top1')


def test_topical_gitlab_default_branch_full_prune(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    wrapper.write_commit('foo', message="other0",
                         branch='default',
                         topic='top1')
    wrapper.command('gitlab-mirror')
    fixture.assert_default_gitlab_branch('topic/default/top1')

    wrapper.prune('.')
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')
    assert re.search(br'obsolet.*default branch', exc_info.value.args[0])

    fixture.assert_default_gitlab_branch('topic/default/top1')


def test_topical_gitlab_default_branch_rename_topic(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    wrapper.write_commit('foo', message="other0",
                         branch='default',
                         topic='top1')
    wrapper.command('gitlab-mirror')
    fixture.assert_default_gitlab_branch('topic/default/top1')

    wrapper.command('topics', b'top2', rev=[b'.'])
    wrapper.command('gitlab-mirror')

    fixture.assert_default_gitlab_branch('topic/default/top2')


def test_closed_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs
    base_ctx = fixture.base_ctx
    default_sha = fixture.ctx1.hex()

    other_ctx = wrapper.write_commit('foo', message="other0",
                                     branch='other',
                                     parent=base_ctx)
    wrapper.command('gitlab-mirror')

    to_close_sha = other_ctx.hex()
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        b'branch/other': to_close_sha,
    }
    set_prune_closed_branches(wrapper, True)
    fixture.activate_mirror()
    fixture.clear_gitlab_notifs()

    wrapper.command('commit', message=b"closing other",
                    close_branch=True)
    # we'll let GitLab do the pruning so that it can use the closing
    # sha for Merge Request detection.
    assert gitlab_branches(repo) == {b'branch/default': default_sha}

    closing_sha = scmutil.revsingle(repo, b'.').hex()
    prune_reason = {b'branch/other':
                    BranchClosed([(closing_sha, [to_close_sha])])}
    changes = {b'refs/heads/branch/other': (to_close_sha, ZERO_SHA)}

    assert notifs == [('pre-receive', (prune_reason, changes)),
                      ('post-receive', (prune_reason, changes))]


def test_previously_closed_branch_not_pruned(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    base_ctx = fixture.base_ctx
    default_sha = fixture.ctx1.hex()

    wrapper.commit_file('foo', message="other0",
                        branch='other',
                        parent=base_ctx)
    # let's prepare a closed branch that hasn't been pruned
    set_prune_closed_branches(wrapper, False)
    wrapper.command('commit', message=b"closing other", close_branch=True)
    closing_sha = scmutil.revsingle(repo, b'.').hex()
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {b'branch/default': default_sha,
                                     b'branch/other': closing_sha}

    # subsequent calls won't prune it...
    set_prune_closed_branches(wrapper, True)
    wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.prune-previously-closed-branches', False)
    wrapper.command('gitlab-mirror')

    assert gitlab_branches(repo).get(b'branch/other') == closing_sha

    # until we flip the right switch
    wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.prune-previously-closed-branches', True)
    wrapper.command('gitlab-mirror')

    assert b'branch/other' not in gitlab_branches(repo)


def test_closed_branch_unknown_to_gitlab(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo

    wrapper.commit_file('foo', message="other0",
                        branch='other',
                        parent=fixture.base_ctx)

    # the `other` branch being mirrored as already closed, will trigger
    # a prune request that should be ignored in order not to fail
    wrapper.command('commit', message=b"closing other", close_branch=True)
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {b'branch/default': fixture.ctx1.hex()}


def test_closed_default_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs
    default_sha = fixture.ctx1.hex()

    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {b'branch/default': default_sha}
    set_default_gitlab_branch(repo, b'branch/default')

    set_prune_closed_branches(wrapper, True)
    wrapper.command('commit', message=b"closing default!", close_branch=True)

    # On native repos, this is a user error

    fixture.clear_gitlab_notifs()
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    assert re.search(br'prune.*default branch', exc_info.value.args[0])

    # and nothing happened
    assert not notifs
    assert gitlab_branches(repo) == {b'branch/default': default_sha}


def test_multiple_heads_merge(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs

    set_allow_multiple_heads(wrapper, True)
    first = wrapper.repo[b'tip']
    second = wrapper.commit_file('bar', message="second head",
                                 branch='default',
                                 parent=fixture.base_ctx)
    first_sha = first.hex()
    second_sha = second.hex()
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {
        b'wild/' + first_sha: first_sha,
        b'wild/' + second_sha: second_sha,
        # the most recently added revision always wins
        b'branch/default': second_sha,
    }
    wrapper.command('merge')
    wrapper.command('commit', message=b'merging heads')
    merge_sha = wrapper.repo[b'.'].hex()

    fixture.clear_gitlab_notifs()
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {
        b'branch/default': merge_sha,
    }

    prune_reasons = {
        b'wild/' + first_sha: WildHeadResolved(first_sha),
        b'wild/' + second_sha: WildHeadResolved(second_sha),
    }
    changes = {
        b'refs/heads/wild/' + first_sha: (first_sha, ZERO_SHA),
        b'refs/heads/wild/' + second_sha: (second_sha, ZERO_SHA),
        b'refs/heads/branch/default': (second_sha, merge_sha)
    }

    assert notifs == [('pre-receive', (prune_reasons, changes)),
                      ('post-receive', (prune_reasons, changes))]


def test_push_multiple_heads_switch_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    base_ctx = fixture.base_ctx

    set_allow_multiple_heads(wrapper, True)
    # second head on default branch (easy to merge for later test)
    default_head2 = wrapper.commit_file(
        'bar', message="default head 2", parent=base_ctx)
    default_heads_shas = {fixture.ctx1.hex(), default_head2.hex()}

    wrapper.command('gitlab-mirror')

    gl_branches = gitlab_branches(repo)
    assert set(gl_branches.values()) == default_heads_shas
    assert len(gl_branches) == 3

    other_head = wrapper.commit_file(
        'foo', message="other", branch='other')
    other_sha = other_head.hex()
    wrapper.command('gitlab-mirror')
    gl_branches = gitlab_branches(repo)
    assert set(gl_branches.values()) == default_heads_shas | {other_sha, }
    assert len(gl_branches) == 4

    # now let's add a topic on top of one of those wild 'default' heads
    topic_ctx = wrapper.commit_file(
        'foo', message="on topic",
        topic='zetop',
        parent=base_ctx)

    wrapper.command('gitlab-mirror')
    gl_branches = gitlab_branches(repo)
    assert set(b for b in gl_branches if not b.startswith(b'wild/')) == {
        b'branch/default', b'branch/other', b'topic/default/zetop'}

    assert set(sha
               for name, sha in gl_branches.items()
               if name.startswith(b'wild/')) == default_heads_shas
    assert gl_branches[b'branch/default'] in default_heads_shas
    assert gl_branches[b'branch/other'] == other_sha
    assert gl_branches[b'topic/default/zetop'] == topic_ctx.hex()


def test_push_multiple_heads_refuse(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    base_ctx = fixture.base_ctx

    # base line with GitLab branches state file already initialized
    wrapper.command('gitlab-mirror')
    default_sha = fixture.ctx1.hex()

    wrapper.commit_file('bar', message="default head 2", parent=base_ctx)

    # default behaviour:
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    # with explicit config:
    set_allow_multiple_heads(wrapper, False)
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    assert b'multiple heads' in exc_info.value.args[0]
    assert gitlab_branches(repo) == {b'branch/default': default_sha}


def test_topic_pruned(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs
    default_sha = fixture.ctx1.hex()

    topic_ctx = wrapper.commit_file(
        'foo', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    topic_sha = topic_ctx.hex()
    topic_gl_branch = b'topic/default/zzetop'
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        topic_gl_branch: topic_sha}

    wrapper.prune(b'zzetop')
    wrapper.command('gitlab-mirror')

    topic_ref = b'refs/heads/topic/default/zzetop'
    topic_change = {topic_ref: (topic_sha, ZERO_SHA)}
    prune_reason = {topic_gl_branch: HeadPruneReason()}

    assert gitlab_branches(repo) == {b'branch/default': default_sha}
    assert notifs == [('pre-receive', (prune_reason, topic_change)),
                      ('post-receive', (prune_reason, topic_change))]


def test_topic_amended(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs
    default_sha = fixture.ctx1.hex()

    topic_ctx = wrapper.commit_file(
        'foo', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    topic_sha = topic_ctx.hex()
    topic_gl_branch = b'topic/default/zzetop'
    assert gitlab_branches(repo) == {b'branch/default': default_sha,
                                     topic_gl_branch: topic_sha}

    amended_ctx = wrapper.amend_file(
        'foo', message=b'amend1')
    wrapper.command('gitlab-mirror')

    amended_sha = amended_ctx.hex()
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        topic_gl_branch: amended_sha}

    topic_change = {
        b'refs/heads/topic/default/zzetop': (topic_sha, amended_sha)
    }

    assert notifs == [('pre-receive', ({}, topic_change)),
                      ('post-receive', ({}, topic_change))]


def test_topic_ff_publish(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs
    default_sha = fixture.ctx1.hex()

    topic_ctx = wrapper.commit_file(
        'foo', message='in ff topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    topic_gl_branch = b'topic/default/zzetop'
    topic_before_sha = topic_ctx.hex()
    assert gitlab_branches(repo) == {b'branch/default': default_sha,
                                     topic_gl_branch: topic_before_sha}

    wrapper.set_phase('public', ['zzetop'])
    wrapper.command('gitlab-mirror')

    assert gitlab_branches(repo) == {b'branch/default': topic_before_sha}

    topic_ref = b'refs/heads/topic/default/zzetop'

    prune_reasons = {topic_gl_branch: TopicPublished(topic_before_sha)}
    changes = {
        b'refs/heads/branch/default': (default_sha, topic_before_sha),
        topic_ref: (topic_before_sha, ZERO_SHA)
    }

    assert notifs == [('pre-receive', (prune_reasons, changes)),
                      ('post-receive', (prune_reasons, changes))]


@parametrize('before_publish', ('add-rebase', 'rebase'))
def test_topic_publish(main_fixture, before_publish):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs

    topic_ctx = wrapper.commit_file(
        'bar', message='in topic',
        parent=fixture.base_ctx,
        topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()
    topic_gl_branch = b'topic/default/zzetop'

    default_before_sha = fixture.ctx1.hex()
    topic_before_sha = topic_ctx.hex()
    assert gitlab_branches(repo) == {
        b'branch/default': default_before_sha,
        topic_gl_branch: topic_before_sha
    }

    if before_publish == 'add-rebase':
        wrapper.commit_file('zz', message='topic addition')

    wrapper.command('rebase', rev=[b'topic(zzetop)'])
    rebased_sha = scmutil.revsingle(repo, b'zzetop').hex()
    wrapper.set_phase('public', ['zzetop'])
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {b'branch/default': rebased_sha}

    prune_reasons = {topic_gl_branch: TopicPublished(rebased_sha)}
    changes = {
        b'refs/heads/branch/default': (default_before_sha, rebased_sha),
        b'refs/heads/topic/default/zzetop': (topic_before_sha, ZERO_SHA),
    }
    assert notifs == [('pre-receive', (prune_reasons, changes)),
                      ('post-receive', (prune_reasons, changes))]


def test_topic_git_escape(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper

    # Only test names that are possible with topics in the first place
    invalid_git_ref_names = [
        ".starts-with-dot",
        "..",
        "ends-with.lock",
        "ends-with-dot.",
    ]
    for name in invalid_git_ref_names:
        wrapper.write_commit('zz', message='in topic', topic=name)

    # This fails if topic names that are invalid in Git are not escaped
    wrapper.command('gitlab-mirror')


def test_topic_clear_publish(main_fixture):
    """The topic head seen from Git is public and has changed topic.

    This is the test for heptapod#265
    The starting point can be considered to be corrupted: any topic change
    should have updated the GitLab branch for the topic. In this scenario
    the change is a removal, wich should have pruned the Git branch, but
    somehow the GitLab branch got updated to the new changeset, that doesn't
    have a topic.
    """
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    notifs = fixture.gitlab_notifs

    topic_before_ctx = wrapper.commit_file(
        'zz', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')

    topic_gl_branch = b'topic/default/zzetop'

    default_before_sha = fixture.ctx1.hex()
    topic_before_sha = topic_before_ctx.hex()
    gitlab_branches_before = gitlab_branches(repo)
    assert gitlab_branches_before == {b'branch/default': default_before_sha,
                                      topic_gl_branch: topic_before_sha}

    wrapper.command('topics', rev=[b'.'], clear=True)
    topic_after_sha = scmutil.revsingle(repo, b'.').hex()
    wrapper.command('gitlab-mirror')
    wrapper.set_phase('public', ['.'])
    forced_topic_before_sha = default_before_sha

    # here's the main point:
    corrupted_gitlab_branches = gitlab_branches(repo)
    corrupted_gitlab_branches[topic_gl_branch] = forced_topic_before_sha
    write_gitlab_branches(repo, corrupted_gitlab_branches)

    fixture.clear_gitlab_notifs()
    # This used to raise LookupError
    wrapper.command('gitlab-mirror')

    assert gitlab_branches(repo) == {b'branch/default': topic_after_sha}
    changes = (
        {topic_gl_branch: TopicPublished(forced_topic_before_sha)},
        {b'refs/heads/topic/default/zzetop': (forced_topic_before_sha,
                                              ZERO_SHA)},
    )
    assert notifs == [('pre-receive', changes),
                      ('post-receive', changes)]


def test_topic_branch_change(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    base_ctx = fixture.base_ctx
    default_sha = fixture.ctx1.hex()

    other_ctx = wrapper.commit_file(
        'bar', message='other0', parent=base_ctx, branch='other')
    topic_other_ctx = wrapper.commit_file(
        'zz', message='in topic', topic='zzetop')

    wrapper.command('gitlab-mirror')

    other_sha, topic_other_sha = other_ctx.hex(), topic_other_ctx.hex()
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        b'branch/other': other_sha,
        b'topic/other/zzetop': topic_other_sha,
    }

    wrapper.command('rebase', rev=[b'zzetop'], dest=b'default')
    wrapper.command('gitlab-mirror')
    assert gitlab_branches(repo) == {
        b'branch/default': default_sha,
        b'branch/other': other_sha,
        b'topic/default/zzetop': scmutil.revsingle(repo, b'zzetop').hex(),
    }


# git.test_integration has test_analyse_vanished_topic_unknown_to_git, that
# does not make sense for native repos, since it is about a changeset present
# in Mercurial and not in the Git auxiliary repository,
# instead of about branches/refs being out of sync


def test_heptapod_notify_gitlab(empty_fixture, monkeypatch):
    wrapper = empty_fixture.hg_repo_wrapper
    handler = NoGitStateMaintainer(wrapper.repo.ui, wrapper.repo)

    notifs = []

    def trigger_failures(name, changes):
        if b'exc' in changes[1]:
            raise RuntimeError('trigger_failures: ' + name)
        if b'code_one' in changes[1]:
            return 1, b'', 'hook refusal'
        return 0, b'Consider a MR for ' + name.encode(), ''

    patch_gitlab_hooks(monkeypatch, notifs, action=trigger_failures)

    # minimal valid change
    change = GitRefChange(b'master', b'before', b'after')
    hook = hooks.PreReceive(wrapper.repo)
    handler.heptapod_notify_gitlab(hook, [], {b'master': change},
                                   allow_error=False)
    assert notifs == [('pre-receive',
                       ([], {b'master': (b'before', b'after')})
                       )]
    del notifs[:]

    with pytest.raises(error.Abort) as exc_info:
        handler.heptapod_notify_gitlab(hook, [], {b'code_one': change},
                                       allow_error=False)
    assert b"hook refusal" in exc_info.value.args[0]

    with pytest.raises(RuntimeError) as exc_info:
        handler.heptapod_notify_gitlab(hook, [], {b'exc': change},
                                       allow_error=False)
    assert "trigger_failures" in exc_info.value.args[0]

    # case where exception is triggered yet is accepted
    errors = []

    def record_ui_error(*args):
        errors.append(args)
    monkeypatch.setattr(handler.repo.ui, 'error', record_ui_error)
    handler.heptapod_notify_gitlab(hook, [], {b'exc': change},
                                   allow_error=True)
    assert errors[0][0].splitlines()[:2] == [
        (b"GitLab update error (GitLab 'pre-receive' hook): "
         + pycompat.sysbytes(
             # this repr() differs between py2 and py3
             repr(RuntimeError('trigger_failures: pre-receive')))),
        b"Traceback (most recent call last):"
    ]


# git.test_integration has a test_heptapod_notify_gitlab_native
# that obviously doesn't make sense for NoGitStateMaintainer, which is always
# native.


def test_subrepos(main_fixture):
    """See heptapod#310 and heptapod#311."""
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper

    # TODO wrapper.path when available
    main_path = fixture.base_path / 'repo.hg'
    nested_path = main_path / 'nested'
    nested = RepoWrapper.init(nested_path)
    nested.write_commit("bar", content="in nested")
    main_path.join('.hgsub').write("\n".join((
        "nested = ../bar",
        "[subpaths]",  # reproduction of heptapod#310
        "foo2=bar2",
    )))

    wrapper.command(b'add', subrepos=True)
    wrapper.command(b'commit', subrepos=True, message=b"invalid")
    wrapper.command('gitlab-mirror')

    wrapper.repo.ui.setconfig(b'hooks', b'precommit',
                              b'python:heptapod.hooks.subrepos.forbid_commit')
    with pytest.raises(error.Abort) as exc_info:
        wrapper.write_commit("foo")
    assert re.search(b'cannot commit.*there are subrepos',
                     exc_info.value.args[0])

    # Now let's simulate update from NULL revision, as Heptapod's
    # use of shares would do
    wrapper.command(b'update', b'0000000000000000000000', clean=True)
    nested_path.remove()

    with pytest.raises(error.Abort) as exc_info:
        wrapper.command(b'update', b'default')
    assert b'not supported' in exc_info.value.args[0]


def test_default_gitlab_ref(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper

    handler = NoGitStateMaintainer(wrapper.repo.ui, wrapper.repo)
    # default Git value
    assert handler.get_default_gitlab_ref() is None
    other_ref = b'refs/heads/something'
    handler.set_default_gitlab_ref(other_ref)

    # instance level cache got invalidated
    assert handler.get_default_gitlab_ref() == other_ref


# git.test_integration has tests for the various `ensure_*` methods,
# starting from there.
# The `NoGitStateMaintainer` class does not implement them
