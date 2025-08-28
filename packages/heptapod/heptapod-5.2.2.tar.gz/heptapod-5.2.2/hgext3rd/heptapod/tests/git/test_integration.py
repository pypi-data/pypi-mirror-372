# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Integration tests for the Git subsystem

In this case, "integration" means that we're testing the main methods,
using true Git repos, and the whole Hook logic. We may also need to create
complex transactions, with several commits, rebases, phase changes etc.
"""
from __future__ import absolute_import

import contextlib
import pytest
import re
import shutil
import subprocess

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
from heptapod.testhelpers.git import (
    extract_git_branch_titles,
    ZERO_SHA,
)
from heptapod.testhelpers.gitlab import (
    patch_gitlab_hooks,
    GitLabMirrorFixture,
)
from heptapod.hooks.tests.utils import switch_user
from hgext3rd.heptapod.branch import (
    GITLAB_TYPED_REFS_MISSING,
    get_default_gitlab_branch,
    read_gitlab_branches,
    write_gitlab_branches,
    remove_gitlab_branches,
    gitlab_tags,
    write_gitlab_tags,
    remove_gitlab_tags,
)
from hgext3rd.heptapod.special_ref import (
    special_refs,
    write_special_refs,
)
from hgext3rd.heptapod.keep_around import (
    iter_keep_arounds,
    init_keep_arounds,
)
from mercurial import (
    encoding,
    error,
    pycompat,
    scmutil,
    ui as uimod,
)
from heptapod.gitlab.change import GitLabRefChange as GitRefChange
from ...git import (
    HeptapodGitHandler,
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
def mirror_fixture_gen(tmpdir, monkeypatch):
    """Common fixture generator."""
    with GitLabMirrorFixture.init(tmpdir, monkeypatch,
                                  hg_config=common_config(tmpdir)) as fixture:
        yield fixture


@pytest.fixture()
def empty_fixture(tmpdir, monkeypatch):
    """A mirror fixture where both repositories are empty."""
    with mirror_fixture_gen(tmpdir, monkeypatch) as fixture:
        yield fixture


@pytest.fixture()
def main_fixture(tmpdir, monkeypatch):
    """A mirror fixture with two public changesets in the Mercurial repo only.

    The changesets are kept on the fixture object as additional attributes
    ``base_ctx`` and ``ctx1``.

    It is up to the test using this fixture to mirror to GitLab or not.
    """
    with mirror_fixture_gen(tmpdir, monkeypatch) as fixture:
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
    git_repo = main_fixture.git_repo
    notifs = main_fixture.gitlab_notifs

    repo.command('gitlab-mirror')

    assert git_repo.branch_titles() == {b'branch/default': b'default1'}
    sha = git_repo.branches()[b'branch/default']['sha']
    assert notifs == [
        ('pre-receive', ({}, {b'refs/heads/branch/default': (ZERO_SHA, sha)})),
        ('post-receive', ({},
                          {b'refs/heads/branch/default': (ZERO_SHA, sha)})),
    ]

    assert read_gitlab_branches(repo.repo) == {
        b'branch/default': repo.repo[b'.'].hex()
    }


@parametrize('pool', ('with-pool', 'without_pool'))
def test_moved_out_of_gitaly_reach(main_fixture, pool):
    with_pool = pool == 'with-pool'
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    wrapper.command('gitlab-mirror')
    orig_git_path = fixture.git_repo.path
    assert fixture.git_repo.branch_titles() == {b'branch/default': b'default1'}
    alternates_relpath = 'objects/info/alternates'
    if with_pool:
        pools_path = orig_git_path / '../@pools'
        pools_path.mkdir()
        in_pool_path = pools_path / 'shared.git'
        orig_git_path.rename(in_pool_path)
        # git clone --shared normalizes the 'alternates' with absolute paths.
        # There is now point trying to give it relative paths, we will
        # edit the alternates later on to match what GitLab does
        pool_rel_path = b'../../@pools/shared.git/objects'
        subprocess.check_call(('git', 'clone', '--bare', '--shared',
                               in_pool_path, orig_git_path))
        (orig_git_path / alternates_relpath).write_binary(pool_rel_path)
        # we did not break it by setting up the alternate objects store.
        assert fixture.git_repo.branch_titles() == {
            b'branch/default': b'default1'}

    wrapper.set_config('heptapod', 'native', True)
    fixture.reload_git_repo()
    assert fixture.git_repo.path != orig_git_path

    # this performs the move
    wrapper.commit_file('foo',
                        content='foo2',
                        message="default2")
    wrapper.command('gitlab-mirror')
    wrapper.command('hpd-export-native-to-git')
    assert fixture.git_repo.branch_titles() == {b'branch/default': b'default2'}
    # subsequent updates (not going through the moving code) also work
    wrapper.commit_file('foo',
                        content='foo3',
                        message="default3")
    wrapper.command('gitlab-mirror')
    wrapper.command('hpd-export-native-to-git')
    assert fixture.git_repo.branch_titles() == {b'branch/default': b'default3'}

    if with_pool:
        # just to be sure
        assert (fixture.git_repo.path / alternates_relpath
                ).read_binary() != pool_rel_path


@parametrize('pushvar', ('skip-ci', 'mr-create'))
def test_pushvars(main_fixture, pushvar):
    wrapper = main_fixture.hg_repo_wrapper
    git_repo = main_fixture.git_repo
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

    assert git_repo.branch_titles() == {b'branch/default': b'default1'}
    sha = git_repo.branches()[b'branch/default']['sha']
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
    git_repo = fixture.git_repo

    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    # Even though it's been initialized from the `HGENCODING` environment
    # variable, the encoding is a global.
    monkeypatch.setattr(encoding, 'encoding', b'latin-1')

    ctx = wrapper.write_commit('encoded', branch=b'pr\xe9parations')
    wrapper.command('gitlab-mirror')

    # not using existing helpers to avoid making the test tautological
    git_branch = b'branch/pr\xe9parations'
    git_ref = b'refs/heads/' + git_branch

    # both in Git repo and in notifs, we have the exact same bytes as provided
    assert set(git_repo.branch_titles()) == {b'branch/default', git_branch}
    sha = git_repo.branches()[git_branch]['sha']
    assert notifs == [
        ('pre-receive', ({}, {git_ref: (ZERO_SHA, sha)})),
        ('post-receive', ({}, {git_ref: (ZERO_SHA, sha)})),
    ]
    assert read_gitlab_branches(wrapper.repo)[git_branch] == ctx.hex()


def test_wiki(main_fixture):
    fixture = main_fixture
    notifs = fixture.gitlab_notifs
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo

    wrapper.repo.ui.environ[b'GL_REPOSITORY'] = b'wiki-251'
    wrapper.command('gitlab-mirror')

    # for wikis, we duplicate `branch/default` as `master`
    assert git_repo.branch_titles() == {b'branch/default': b'default1',
                                        b'master': b'default1',
                                        }
    sha = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {b'refs/heads/branch/default': (ZERO_SHA, sha),
                   b'refs/heads/master': (ZERO_SHA, sha),
                   }
    assert notifs == [
        ('pre-receive', changes),
        ('post-receive', changes),
    ]


def test_tags_simple(main_fixture):
    repo = main_fixture.hg_repo_wrapper
    git_repo = main_fixture.git_repo
    notifs = main_fixture.gitlab_notifs
    base_ctx = main_fixture.base_ctx

    # Creation
    repo.command('tag', b'v1.2.3', rev=base_ctx.hex())
    repo.command('gitlab-mirror')

    branches = git_repo.branches()
    assert list(branches) == [b'branch/default']
    branch = branches[b'branch/default']

    assert b'v1.2.3' in branch['title']
    assert git_repo.tags() == {b'v1.2.3', }
    tagged_git_sha_0, tagged_git_title = git_repo.commit_hash_title('v1.2.3')
    assert tagged_git_title == b'default0'

    first_default_branch_sha = branch['sha']
    changes = {}, {
        b'refs/heads/branch/default': (ZERO_SHA, first_default_branch_sha),
        b'refs/tags/v1.2.3': (ZERO_SHA, tagged_git_sha_0),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Modification
    repo.command('tag', b'v1.2.3', rev=b'1', force=True)
    repo.command('gitlab-mirror')

    assert git_repo.tags() == {b'v1.2.3', }
    tagged_git_sha_1, tagged_git_title = git_repo.commit_hash_title('v1.2.3')
    assert tagged_git_title == b'default1'

    new_default_branch_sha = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {
        b'refs/heads/branch/default': (first_default_branch_sha,
                                       new_default_branch_sha),
        b'refs/tags/v1.2.3': (tagged_git_sha_0, tagged_git_sha_1),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    repo.command('tag', b'v1.2.3', remove=True)
    repo.command('gitlab-mirror')

    assert not git_repo.tags()

    last_default_branch_sha = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {
        b'refs/heads/branch/default': (new_default_branch_sha,
                                       last_default_branch_sha),
        b'refs/tags/v1.2.3': (tagged_git_sha_1, ZERO_SHA),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_tags_permission(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx

    fixture.activate_mirror()  # we'll need the mirror in-transaction

    wrapper.set_config('web', 'allow-push', 'writer')
    wrapper.set_config('web', 'allow-publish', 'publisher')

    # Publisher can create tag
    switch_user(wrapper, 'publisher')
    with wrapper.tags_sanitizer():
        wrapper.command('tag', b'v1.2.3', rev=base_ctx.hex())
        assert git_repo.tags() == {b'v1.2.3', }

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

    assert not git_repo.tags()


def test_tags_escaping_removal(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    git_repo = main_fixture.git_repo
    notifs = main_fixture.gitlab_notifs

    # a tag with a space character
    hg_tag = b'Version 1.2.3'
    git_tag = 'Version_1.2.3'
    wrapper.command('tag', hg_tag)
    wrapper.command('gitlab-mirror')

    assert git_repo.tags() == {as_bytes(git_tag)}
    tagged_git_sha, tagged_git_title = git_repo.commit_hash_title(git_tag)
    assert tagged_git_title == b'default1'

    branches = git_repo.branches()
    assert list(branches) == [b'branch/default']
    branch = branches[b'branch/default']

    branch_git_sha1 = branch['sha']
    changes = {}, {
        b'refs/heads/branch/default': (ZERO_SHA, branch_git_sha1),
        as_bytes('refs/tags/' + git_tag): (ZERO_SHA, tagged_git_sha),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Pushing something else does not count as a tag modification.
    # This asserts that heptapod#464 is fixed.
    wrapper.commit_file('something-else')
    wrapper.command('gitlab-mirror')

    branch_git_sha2 = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {
        b'refs/heads/branch/default': (branch_git_sha1, branch_git_sha2),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Change is still possible
    wrapper.command('tag', hg_tag, force=True)
    wrapper.command('gitlab-mirror')
    assert git_repo.tags() == {as_bytes(git_tag)}
    branch_git_sha3 = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {
        b'refs/heads/branch/default': (branch_git_sha2, branch_git_sha3),
        as_bytes('refs/tags/' + git_tag): (tagged_git_sha, branch_git_sha2),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]
    main_fixture.clear_gitlab_notifs()

    # Removal is still possible
    wrapper.command('tag', hg_tag, remove=True)
    wrapper.command('gitlab-mirror')
    assert not git_repo.tags()

    branch_git_sha4 = git_repo.branches()[b'branch/default']['sha']
    changes = {}, {
        b'refs/heads/branch/default': (branch_git_sha3, branch_git_sha4),
        as_bytes('refs/tags/' + git_tag): (branch_git_sha2, ZERO_SHA),
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
    git_repo = main_fixture.git_repo
    base_ctx = main_fixture.base_ctx
    tmpdir = main_fixture.base_path

    # let's start with some commits in the Git repo
    main_wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    # now let's make a share
    dest_wrapper = main_wrapper.share(tmpdir.join('share.hg'))
    dest_wrapper.write_commit('bar', message='other0',
                              branch='other', parent=base_ctx.node())
    dest_wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'default1',
                                        b'branch/other': b'other0'}


def test_bookmarks(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo

    # this activates in particular the gitlab-mirror hook
    wrapper.repo.ui.readconfig(HEPTAPOD_REQUIRED_HGRC, trust=True)

    set_allow_bookmarks(wrapper, True)

    base = wrapper.commit_file('foo', message="unbookmarked")
    bk1 = wrapper.commit_file('foo', message="book1")
    bk2 = wrapper.commit_file('foo', message="book2")
    wrapper.command('bookmark', b'zebook1', rev=bk1.hex())
    wrapper.command('bookmark', b'zebook2', rev=bk2.hex())
    assert git_repo.branch_titles() == {b'branch/default': b'book2',
                                        b'zebook1': b'book1',
                                        b'zebook2': b'book2'}
    assert read_gitlab_branches(wrapper.repo) == {b'branch/default': bk2.hex(),
                                                  b'zebook1': bk1.hex(),
                                                  b'zebook2': bk2.hex()}
    ctx = wrapper.commit_file('foo', message="new default head", parent=base)
    assert git_repo.branch_titles() == {b'branch/default': b'new default head',
                                        b'zebook1': b'book1',
                                        b'zebook2': b'book2'}
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
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx
    notifs = main_fixture.gitlab_notifs

    repo = server.repo
    default1_ctx = repo[b'.']
    server.command('bookmark', b'zebook', rev=base_ctx.hex())
    # not being in a transaction accepts the bookmark immediately
    server.command('gitlab-mirror')

    fixture.clear_gitlab_notifs()

    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'zebook': b'default0'
    }
    book_git_sha = git_repo.branches()[b'zebook']['sha']

    fixture.activate_mirror()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(base_ctx.node()) == []
    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
    }

    assert read_gitlab_branches(repo) == {
        b'branch/default': default1_ctx.hex()
    }

    changes = {b'zebook': BookmarkRemoved(book_git_sha)}, {
        b'refs/heads/zebook': (book_git_sha, ZERO_SHA)
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_bookmarks_mask_branch_prune(main_fixture):
    fixture = main_fixture
    server = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = main_fixture.gitlab_notifs

    server.command('gitlab-mirror')
    # just checking our assumptions
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    # we need to test the branch masking on a branch
    # that's not the GitLab default (which is protected)
    server.write_commit('foo', branch='other', message='other1')

    fixture.activate_mirror()
    set_allow_bookmarks(server, True)
    head = server.repo[b'tip']
    server.command('bookmark', b'zebook', rev=head.hex())
    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'zebook': b'other1'
    }
    book_git_sha = git_repo.branches()[b'zebook']['sha']

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(head.node()) == []
    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'branch/other': b'other1',
    }

    changes = {b'zebook': BookmarkRemoved(book_git_sha)}, {
        b'refs/heads/zebook': (book_git_sha, ZERO_SHA),
        b'refs/heads/branch/other': (ZERO_SHA, book_git_sha),
    }
    assert notifs == [('pre-receive', changes), ('post-receive', changes)]


def test_bookmarks_obsolete(empty_fixture):
    fixture = empty_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo

    set_allow_bookmarks(wrapper, True)

    draft1 = wrapper.commit_file('foo', message='Initial draft')
    wrapper.command('bookmark', b'zebook', rev=draft1.hex(), inactive=True)
    wrapper.command('gitlab-mirror')

    # just checking our assumptions.
    assert git_repo.branch_titles() == {b'zebook': b'Initial draft'}

    # let's get in-transaction
    fixture.activate_mirror()

    draft2 = wrapper.commit_file('foo', message='amended', parent=NULL_ID)
    with pytest.raises(error.Abort) as exc_info:
        wrapper.prune(draft1.hex(), successors=[draft2.hex()])
    assert re.search(br'bookmark.*zebook.*obsolete', exc_info.value.args[0])


def test_bookmarks_dont_mask_default_branch(main_fixture):
    fixture = main_fixture
    server = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    server.command('gitlab-mirror')
    # just checking our assumptions
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    fixture.activate_mirror()
    set_allow_bookmarks(server, True)
    head = server.repo[b'tip']
    git_sha = git_repo.get_branch_sha('branch/default').encode()

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', rev=head.hex())

    # the default branch is not pruned
    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'zebook': b'default1'
    }

    changes = {b'refs/heads/zebook': (ZERO_SHA, git_sha)}
    assert notifs == [('pre-receive', ({}, changes)),
                      ('post-receive', ({}, changes)),
                      ]

    fixture.clear_gitlab_notifs()
    server.command('bookmark', b'zebook', delete=True)

    assert server.repo.nodebookmarks(head.node()) == []
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}
    changes = {b'refs/heads/zebook': (git_sha, ZERO_SHA)}
    prunes = {b'zebook': BookmarkRemoved(git_sha)}

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


def test_closed_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs
    base_ctx = fixture.base_ctx

    wrapper.write_commit('foo', message="other0",
                         branch='other',
                         parent=base_ctx.node(),
                         return_ctx=True)
    wrapper.command('gitlab-mirror')

    assert git_repo.branch_titles() == {b'branch/default': b'default1',
                                        b'branch/other': b'other0'}
    to_close_sha = git_repo.branches()[b'branch/other']['sha']
    set_prune_closed_branches(wrapper, True)
    fixture.activate_mirror()
    fixture.clear_gitlab_notifs()

    wrapper.command('commit', message=b"closing other",
                    close_branch=True)
    # we'll let GitLab do the pruning so that it can use the closing
    # sha for Merge Request detection.
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)
    closing_sha = handler.map_git_get(wrapper.repo[b'tip'].hex())
    prune_reason = {b'branch/other':
                    BranchClosed([(closing_sha, [to_close_sha])])}
    changes = {b'refs/heads/branch/other': (to_close_sha, ZERO_SHA)}

    assert notifs == [('pre-receive', (prune_reason, changes)),
                      ('post-receive', (prune_reason, changes))]


def test_closed_branch_by_topic(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs
    base_ctx = fixture.base_ctx

    wrapper.write_commit('foo', message="other0",
                         branch='other',
                         parent=base_ctx.node(),
                         return_ctx=True)
    wrapper.command('gitlab-mirror')

    assert git_repo.branch_titles() == {b'branch/default': b'default1',
                                        b'branch/other': b'other0'}
    to_close_sha = git_repo.branches()[b'branch/other']['sha']
    set_prune_closed_branches(wrapper, True)
    fixture.activate_mirror()
    fixture.clear_gitlab_notifs()

    wrapper.command('commit', message=b"closing other",
                    topic=b'drop-support',
                    close_branch=True)
    # the branch stays visible until the changeset is public
    # gracinet: this is debatable, that's the just the way it happened,
    # and something similar happens with `hg branches`
    # OTOH the topic is not itself visible in GitLab branches and we
    # definitely don't want to assert that.
    assert b'branch/other' in git_repo.branches()

    wrapper.set_phase('public', ['.'])
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    prune_reason = {b'branch/other': BranchClosed([])}
    changes = {b'refs/heads/branch/other': (to_close_sha, ZERO_SHA)}

    assert notifs == [('pre-receive', (prune_reason, changes)),
                      ('post-receive', (prune_reason, changes))]


def test_previously_closed_branch_not_pruned(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx

    wrapper.commit_file('foo', message="other0",
                        branch='other',
                        parent=base_ctx)

    # let's prepare a closed branch that hasn't been pruned
    set_prune_closed_branches(wrapper, False)
    wrapper.command('commit', message=b"closing other", close_branch=True)
    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'default1',
                                        b'branch/other': b'closing other'}

    # subsequent calls won't prune it...
    set_prune_closed_branches(wrapper, True)
    wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.prune-previously-closed-branches', False)
    wrapper.command('gitlab-mirror')

    assert git_repo.branch_titles()[b'branch/other'] == b'closing other'

    # until we flip the right switch
    wrapper.repo.ui.setconfig(
        b'experimental', b'hg-git.prune-previously-closed-branches', True)
    wrapper.command('gitlab-mirror')

    assert b'branch/other' not in git_repo.branch_titles()


def test_closed_branch_unknown_to_gitlab(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo

    wrapper.commit_file('foo', message="other0",
                        branch='other',
                        parent=fixture.base_ctx)

    # the `other` branch being mirrored as already closed, will trigger
    # a prune request that should be ignored in order not to fail
    wrapper.command('commit', message=b"closing other", close_branch=True)
    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}


def test_closed_default_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}
    git_repo.set_symref('HEAD', 'refs/heads/branch/default')

    set_prune_closed_branches(wrapper, True)
    wrapper.command('commit', message=b"closing default!", close_branch=True)

    # On non-native repos, this is a user error
    wrapper.repo.ui.setconfig(b'heptapod', b'native', False)  # making sure
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    assert re.search(br'prune.*default branch', exc_info.value.args[0])

    assert git_repo.branch_titles() == {b'branch/default': b'default1'}

    # On native repos, this is a user error as well, but still it will move
    # the repo out of Gitaly reach (this sounds weird in this "git" test, but
    # we need the Git repo to have been created and this test just did it.
    wrapper.repo.ui.setconfig(b'heptapod', b'native', True)
    fixture.reload_git_repo()
    git_repo = fixture.git_repo

    fixture.clear_gitlab_notifs()
    wrapper.command('hpd-export-native-to-git')

    assert not notifs
    assert git_repo.branch_titles() == {b'branch/default': b'default1'}


def test_multiple_heads_merge(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    set_allow_multiple_heads(wrapper, True)
    first = wrapper.repo[b'tip']
    second = wrapper.commit_file('bar', message="second head",
                                 branch='default',
                                 parent=fixture.base_ctx)
    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {
        b'wild/' + first.hex(): b'default1',
        b'wild/' + second.hex(): b'second head',
        # the most recently added revision always wins
        b'branch/default': b'second head',
    }
    git_branches = git_repo.branches()
    first_git_sha = git_branches[b'wild/' + first.hex()]['sha']
    second_git_sha = git_branches[b'wild/' + second.hex()]['sha']
    assert read_gitlab_branches(wrapper.repo) == {
        b'wild/' + first.hex(): first.hex(),
        b'wild/' + second.hex(): second.hex(),
        b'branch/default': second.hex(),
    }
    wrapper.command('merge')
    wrapper.command('commit', message=b'merging heads')
    merge_ctx = wrapper.repo[b'.']

    fixture.clear_gitlab_notifs()
    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {b'branch/default': b'merging heads'}
    assert read_gitlab_branches(wrapper.repo) == {
        b'branch/default': merge_ctx.hex(),
    }

    prune_reasons = {
        b'wild/' + first.hex(): WildHeadResolved(first_git_sha),
        b'wild/' + second.hex(): WildHeadResolved(second_git_sha),
    }
    changes = {
        b'refs/heads/wild/' + first.hex(): (first_git_sha, ZERO_SHA),
        b'refs/heads/wild/' + second.hex(): (second_git_sha, ZERO_SHA),
        b'refs/heads/branch/default': (
            second_git_sha,
            git_repo.branches()[b'branch/default']['sha'])
    }

    assert notifs == [('pre-receive', (prune_reasons, changes)),
                      ('post-receive', (prune_reasons, changes))]


def test_push_multiple_heads_switch_branch(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx

    set_allow_multiple_heads(wrapper, True)
    # second head on default branch (easy to merge for later test)
    wrapper.commit_file(
        'bar', message="default head 2", parent=base_ctx)
    default_heads_titles = {b'default1', b'default head 2'}

    wrapper.command('gitlab-mirror')

    branch_titles = git_repo.branch_titles()
    assert set(branch_titles.values()) == default_heads_titles
    assert len(branch_titles) == 3

    wrapper.commit_file(
        'foo', message="other", branch='other')
    wrapper.command('gitlab-mirror')
    branch_titles = git_repo.branch_titles()
    assert set(branch_titles.values()) == default_heads_titles | {b'other', }
    assert len(branch_titles) == 4

    # now let's add a topic on top of one of those wild 'default' heads
    wrapper.commit_file(
        'foo', message="on topic",
        topic='zetop',
        parent=base_ctx)

    wrapper.command('gitlab-mirror')
    branch_titles = git_repo.branch_titles()
    assert set(b for b in branch_titles if not b.startswith(b'wild/')) == {
        b'branch/default', b'branch/other', b'topic/default/zetop'}

    assert set(title
               for name, title in branch_titles.items()
               if name.startswith(b'wild/')) == default_heads_titles
    assert branch_titles[b'branch/default'] in default_heads_titles
    assert branch_titles[b'branch/other'] == b'other'
    assert branch_titles[b'topic/default/zetop'] == b'on topic'


def test_push_multiple_heads_refuse(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx

    wrapper.commit_file('bar', message="default head 2", parent=base_ctx)

    # default behaviour:
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    # with explicit config:
    set_allow_multiple_heads(wrapper, False)
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('gitlab-mirror')

    assert b'multiple heads' in exc_info.value.args[0]
    assert git_repo.branch_titles() == {}


def test_topic_pruned(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.commit_file(
        'foo', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    topic_gl_branch = b'topic/default/zzetop'
    branches_before = git_repo.branches()
    assert extract_git_branch_titles(branches_before) == {
        b'branch/default': b'default1',
        topic_gl_branch: b'in topic'}

    wrapper.prune(b'zzetop')
    wrapper.command('gitlab-mirror')

    topic_ref = b'refs/heads/topic/default/zzetop'
    topic_change = {topic_ref: (
        branches_before[b'topic/default/zzetop']['sha'],
        ZERO_SHA,
    )}
    prune_reason = {topic_gl_branch: HeadPruneReason()}

    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
    }
    assert notifs == [('pre-receive', (prune_reason, topic_change)),
                      ('post-receive', (prune_reason, topic_change))]


def test_topic_amended(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.commit_file(
        'foo', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    branches_before = git_repo.branches()
    assert extract_git_branch_titles(branches_before) == {
        b'branch/default': b'default1',
        b'topic/default/zzetop': b'in topic'}

    wrapper.amend_file(
        'foo', message=b'amend1')
    wrapper.command('gitlab-mirror')

    branches = git_repo.branches()
    assert extract_git_branch_titles(branches) == {
        b'branch/default': b'default1',
        b'topic/default/zzetop': b'amend1',
    }

    topic_change = {b'refs/heads/topic/default/zzetop': (
        branches_before[b'topic/default/zzetop']['sha'],
        branches[b'topic/default/zzetop']['sha'],
    )}

    assert notifs == [('pre-receive', ({}, topic_change)),
                      ('post-receive', ({}, topic_change))]


def test_topic_ff_publish(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.commit_file(
        'foo', message='in ff topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    topic_gl_branch = b'topic/default/zzetop'
    branches_before = git_repo.branches()
    topic_before_sha = branches_before[b'topic/default/zzetop']['sha']
    default_sha = branches_before[b'branch/default']['sha']
    assert extract_git_branch_titles(branches_before) == {
        b'branch/default': b'default1',
        topic_gl_branch: b'in ff topic'}

    wrapper.set_phase('public', ['zzetop'])
    wrapper.command('gitlab-mirror')

    assert git_repo.branch_titles() == {b'branch/default': b'in ff topic'}

    topic_ref = b'refs/heads/topic/default/zzetop'

    prune_reasons = {topic_gl_branch: TopicPublished(topic_before_sha)}
    changes = {
        b'refs/heads/branch/default': (default_sha, topic_before_sha),
        topic_ref: (topic_before_sha, ZERO_SHA)
    }

    assert notifs == [('pre-receive', (prune_reasons, changes)),
                      ('post-receive', (prune_reasons, changes))]


@parametrize('before_publish', ('add-rebase', 'rebase'))
def test_topic_rebase_publish(main_fixture, before_publish):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.commit_file(
        'bar', message='in topic',
        parent=fixture.base_ctx,
        topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()
    topic_gl_branch = b'topic/default/zzetop'

    branches_before = git_repo.branches()
    assert extract_git_branch_titles(branches_before) == {
        b'branch/default': b'default1',
        topic_gl_branch: b'in topic'}
    default_before_sha = branches_before[b'branch/default']['sha']
    topic_before_sha = branches_before[topic_gl_branch]['sha']

    if before_publish == 'add-rebase':
        wrapper.commit_file('zz', message='topic addition')
        topic_head_title = b'topic addition'
    else:
        topic_head_title = b'in topic'

    wrapper.command('rebase', rev=[b'topic(zzetop)'])
    wrapper.set_phase('public', ['zzetop'])
    wrapper.command('gitlab-mirror')
    branches_after = git_repo.branches()
    assert extract_git_branch_titles(branches_after) == {
        b'branch/default': topic_head_title}
    # now we're sure the head of branch/default is the rebased commit
    rebased_sha = branches_after[b'branch/default']['sha']

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
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    wrapper.commit_file(
        'zz', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')

    topic_gl_branch = b'topic/default/zzetop'

    branches_before = git_repo.branches()
    assert extract_git_branch_titles(branches_before) == {
        b'branch/default': b'default1',
        topic_gl_branch: b'in topic'}

    wrapper.command('topics', rev=[b'.'], clear=True)
    wrapper.command('gitlab-mirror')
    wrapper.set_phase('public', ['.'])
    forced_topic_before_sha = as_bytes(git_repo.get_branch_sha(
        'branch/default'))

    # here's the main point:
    git_repo.set_branch(pycompat.sysstr(topic_gl_branch),
                        forced_topic_before_sha)

    fixture.clear_gitlab_notifs()
    # This used to raise LookupError
    wrapper.command('gitlab-mirror')

    branches_after = git_repo.branches()
    assert extract_git_branch_titles(branches_after) == {
        b'branch/default': b'in topic',
    }
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
    git_repo = fixture.git_repo
    base_ctx = fixture.base_ctx

    wrapper.commit_file(
        'bar', message='other0', parent=base_ctx, branch='other')
    wrapper.commit_file(
        'zz', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')

    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'branch/other': b'other0',
        b'topic/other/zzetop': b'in topic'}

    wrapper.command('rebase', rev=[b'zzetop'], dest=b'default')
    wrapper.command('gitlab-mirror')
    assert git_repo.branch_titles() == {
        b'branch/default': b'default1',
        b'branch/other': b'other0',
        b'topic/default/zzetop': b'in topic',
    }


def test_analyse_vanished_topic_not_in_git(main_fixture, monkeypatch):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    repo = wrapper.repo
    git_repo = fixture.git_repo

    wrapper.write_commit('zz', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')

    def return_unknown(handler, *a, **kw):
        handler.repo.test_patch_called = True
        return b'unknown-to-git'

    # let's make the published topic analysis return something unknown to Git
    monkeypatch.setattr(HeptapodGitHandler, 'published_topic_latest_hg_sha',
                        return_unknown)

    wrapper.set_phase('public', ['zzetop'])
    # Calling export directly because through the hook, such
    # monkey patching often does not work.
    HeptapodGitHandler(repo, repo.ui).export_commits()

    # we didn't fail and have been conservative with the topic GitLab branch
    assert git_repo.branch_titles() == {
        b'branch/default': b'in topic',
        b'topic/default/zzetop': b'in topic'
    }

    # note that coverage would notice if the test harness didn't work
    assert wrapper.repo.test_patch_called


def test_heptapod_notify_gitlab(tmpdir, monkeypatch):
    wrapper = RepoWrapper.init(tmpdir.join('repo'),
                               config=common_config(tmpdir))
    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)

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


def test_heptapod_notify_gitlab_native(main_fixture):
    fixture = main_fixture
    wrapper = fixture.hg_repo_wrapper
    git_repo = fixture.git_repo
    notifs = fixture.gitlab_notifs

    topic_ctx = wrapper.write_commit('zz', message='in topic', topic='zzetop')
    wrapper.command('gitlab-mirror')
    fixture.clear_gitlab_notifs()

    gl_branch_default = b'branch/default'
    default_hg_sha = wrapper.repo[1].hex()
    default_git_sha = git_repo.get_branch_sha(gl_branch_default).encode()

    gl_branch_topic = b'topic/default/zzetop'
    topic_hg_sha = topic_ctx.hex()
    topic_git_sha = git_repo.get_branch_sha(gl_branch_topic).encode()

    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)

    hook1 = hooks.PreReceive(wrapper.repo)
    hook2 = hooks.PostReceive(wrapper.repo)

    wrapper.repo.ui.setconfig(b'heptapod', b'native', b'yes')

    # branch creation, interesting because ZERO_SHA isn't in the mappings
    change = GitRefChange(b'something', ZERO_SHA, topic_git_sha)
    handler.heptapod_notify_gitlab(hook1, [], {b'something': change})
    assert notifs == [
        ('pre-receive', ([], {b'something': (ZERO_SHA, topic_hg_sha)}))
    ]

    # branch change
    # second hook call to check for side effects in pre/post-receive succession
    change = GitRefChange(b'branch/default', default_git_sha, topic_git_sha)
    fixture.clear_gitlab_notifs()

    handler.heptapod_notify_gitlab(hook1, [], {b'branch/default': change})
    assert notifs == [
        ('pre-receive', ([],
                         {b'branch/default': (default_hg_sha, topic_hg_sha)}))
    ]
    fixture.clear_gitlab_notifs()

    handler.heptapod_notify_gitlab(hook2, [], {b'branch/default': change})
    assert notifs == [
        ('post-receive', ([],
                          {b'branch/default': (default_hg_sha, topic_hg_sha)}))
    ]

    # Topic published (making this realistic, but consistency shouldn't matter)
    # this tests most of the PruneReasons. If a new one not subclassing
    # HeadPruneReasonWithSha would appear, coverage drop would warn us.
    fixture.clear_gitlab_notifs()
    prune_change = GitRefChange(gl_branch_topic, topic_git_sha, ZERO_SHA)
    prune_reasons = {gl_branch_topic: TopicPublished(topic_git_sha)}
    changes = {gl_branch_default: change, gl_branch_topic: prune_change}
    expected = ({gl_branch_topic: TopicPublished(topic_hg_sha)},
                {gl_branch_default: (default_hg_sha, topic_hg_sha),
                 gl_branch_topic: (topic_hg_sha, ZERO_SHA),
                 })
    handler.heptapod_notify_gitlab(hook1, prune_reasons, changes)
    assert notifs[-1] == ('pre-receive', expected)
    handler.heptapod_notify_gitlab(hook2, prune_reasons, changes)
    assert notifs[-1] == ('post-receive', expected)

    # BranchClosed.
    # This example is less realistic, we pretend the topic changeset
    # actually closes the default branch. At this low level, it doesn't matter.
    prune_change = GitRefChange(gl_branch_default, default_git_sha, ZERO_SHA)
    changes = {gl_branch_default: prune_change}
    prune_reasons = {
        gl_branch_default: BranchClosed([(topic_git_sha, [default_git_sha])]),
    }
    expected = (
        {gl_branch_default: BranchClosed([(topic_hg_sha, [default_hg_sha])])},
        {gl_branch_default: (default_hg_sha, ZERO_SHA)},
    )
    fixture.clear_gitlab_notifs()
    handler.heptapod_notify_gitlab(hook1, prune_reasons, changes)
    assert notifs[-1] == ('pre-receive', expected)
    handler.heptapod_notify_gitlab(hook2, prune_reasons, changes)
    assert notifs[-1] == ('post-receive', expected)

    # HeadPruneReason with no info to convert
    prune_reasons = {gl_branch_default: HeadPruneReason()}
    expected = (
        {gl_branch_default: HeadPruneReason()},
        {gl_branch_default: (default_hg_sha, ZERO_SHA)},
    )
    handler.heptapod_notify_gitlab(hook1, prune_reasons, changes)
    assert notifs[-1] == ('pre-receive', expected)

    # Corner case: BranchClosed without info to convert
    prune_reasons = {gl_branch_default: BranchClosed()}
    expected = (
        {gl_branch_default: BranchClosed()},
        {gl_branch_default: (default_hg_sha, ZERO_SHA)},
    )
    handler.heptapod_notify_gitlab(hook1, prune_reasons, changes)
    assert notifs[-1] == ('pre-receive', expected)


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
    git_repo = fixture.git_repo

    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)
    # default Git value
    assert handler.get_default_gitlab_ref() == b'refs/heads/master'
    other_ref = b'refs/heads/something'
    handler.set_default_gitlab_ref(other_ref)

    assert git_repo.get_symref('HEAD') == other_ref.decode()

    # instance level cache got invalidated
    assert handler.get_default_gitlab_ref() == other_ref


def test_ensure_gitlab_branches_file(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    wrapper.command('gitlab-mirror')

    repo = wrapper.repo

    # making sure we start afresh
    remove_gitlab_branches(repo)
    with pytest.raises(FileNotFoundError):
        read_gitlab_branches(repo)

    handler = HeptapodGitHandler(repo, repo.ui)
    returned = handler.ensure_gitlab_branches()
    branches = {b'branch/default': repo[b'.'].hex()}
    assert read_gitlab_branches(repo) == branches
    assert returned == branches

    # doesn't do anything if already there
    branches = {b'foo': b'deadbeef' * 5}
    write_gitlab_branches(wrapper.repo, branches)
    assert handler.ensure_gitlab_branches() is None
    assert read_gitlab_branches(repo) == branches


def test_ensure_gitlab_branches_file_empty_repo(empty_fixture):
    wrapper = empty_fixture.hg_repo_wrapper
    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)
    returned = handler.ensure_gitlab_branches()
    assert read_gitlab_branches(wrapper.repo) == {}
    assert returned == {}


def test_ensure_gitlab_tags_file(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    wrapper.command('tag', b'v1.2.3')
    wrapper.command('gitlab-mirror')

    repo = wrapper.repo

    # making sure we start afresh
    remove_gitlab_tags(repo)
    assert gitlab_tags(repo) is GITLAB_TYPED_REFS_MISSING

    handler = HeptapodGitHandler(repo, repo.ui)
    tags = {b'v1.2.3': main_fixture.ctx1.hex()}
    returned = handler.ensure_gitlab_tags()
    assert gitlab_tags(repo) == tags
    assert returned == tags

    # doesn't do anything if already there
    tags = {b'foo': b'deadbeef' * 5}
    write_gitlab_tags(wrapper.repo, tags)
    handler.ensure_gitlab_tags() is None
    assert gitlab_tags(repo) == tags


def test_ensure_gitlab_special_refs_file(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    repo = wrapper.repo
    git_repo = main_fixture.git_repo
    ctx = wrapper.commit_file('foo')
    wrapper.command('gitlab-mirror')

    git_sha = git_repo.get_branch_sha('branch/default')
    ref_path = b'refs/pipelines/98'
    git_repo.write_ref(ref_path, git_sha)
    assert git_repo.all_refs()[ref_path] == git_sha.encode()  # double-check

    handler = HeptapodGitHandler(repo, repo.ui)
    srefs = {b'pipelines/98': ctx.hex()}
    returned = handler.ensure_gitlab_special_refs()
    assert special_refs(repo) == srefs
    assert returned == srefs

    # doesn't do anything if already there
    refs = {b'foo': b'deadbeef' * 5}
    write_special_refs(wrapper.repo, refs)
    assert special_refs(repo) == refs
    assert handler.ensure_gitlab_special_refs() is None


def test_ensure_gitlab_keep_arounds_file(main_fixture):
    wrapper = main_fixture.hg_repo_wrapper
    repo = wrapper.repo
    git_repo = main_fixture.git_repo
    ctx = wrapper.commit_file('foo')
    wrapper.command('gitlab-mirror')

    git_sha = git_repo.get_branch_sha('branch/default')
    git_repo.write_ref(b'refs/keep-around/' + git_sha.encode(), git_sha)

    handler = HeptapodGitHandler(repo, repo.ui)
    returned = handler.ensure_gitlab_keep_arounds()
    assert list(iter_keep_arounds(repo)) == [ctx.hex()]
    assert returned == {ctx.hex()}

    # doesn't do anything if already there, with or without actual
    # content
    for existing in ([], [b'deadcafe' * 8]):
        init_keep_arounds(repo, existing)
        assert handler.ensure_gitlab_keep_arounds() is None
        assert list(iter_keep_arounds(repo)) == existing


def test_ensure_gitlab_default_branch_on_existing_git_repo(empty_fixture):
    wrapper = empty_fixture.hg_repo_wrapper
    git_repo = empty_fixture.git_repo
    # actually create the Git repository
    git_repo.init(git_repo.path)

    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)
    handler.ensure_gitlab_default_branch()
    # the default value of Git is copied over
    assert get_default_gitlab_branch(wrapper.repo) == b'master'


def test_ensure_state_file_does_not_create_git_repo(empty_fixture):
    # we do not want the ensure methods to create an auxiliary Git
    # repo if it does not exist, for clarity in future fully native projects
    # without Git repo.
    wrapper = empty_fixture.hg_repo_wrapper
    git_repo = empty_fixture.git_repo
    shutil.rmtree(git_repo.path)
    assert not git_repo.path.exists()

    handler = HeptapodGitHandler(wrapper.repo, wrapper.repo.ui)
    assert not git_repo.path.exists()

    handler.ensure_gitlab_branches()
    assert not git_repo.path.exists()

    handler.ensure_gitlab_tags()
    assert not git_repo.path.exists()

    handler.ensure_gitlab_special_refs()
    assert not git_repo.path.exists()

    handler.ensure_gitlab_keep_arounds()
    assert not git_repo.path.exists()

    handler.ensure_gitlab_default_branch()
    assert not git_repo.path.exists()
