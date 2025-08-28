# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
import pytest
from mercurial import (
    error,
)
from heptapod.testhelpers import (
    RepoWrapper,
    make_ui,
    as_bytes,
)
from ..topic import (
    change_topic,
    cleanup_tmp_bundle,
)
from .utils import common_config


def make_main_repo(tmpdir, path):
    """Make repo with 2 public revs; return wrapper, ctx of rev 0

    The returned ctx is for the first changeset because we'll use it as
    a branching point, hence more often than the second.
    """
    config = common_config(tmpdir)
    config['phases'] = dict(publish=False)
    wrapper = RepoWrapper.init(path, config=config)

    ctx = wrapper.write_commit('foo', content='foo0', message="default0",
                               return_ctx=True)
    wrapper.write_commit('foo', content='foo1', message="default1")
    wrapper.set_phase('public', ['.'])
    return wrapper, ctx


def test_force_draft(tmpdir):
    """Case where the remote changesets are public."""
    main_path = tmpdir.join('main')
    fork_path = tmpdir.join('fork')

    main, base_ctx = make_main_repo(tmpdir, main_path)

    fork = RepoWrapper.init(fork_path)
    fork.command('pull', as_bytes(main_path), rev=[base_ctx.hex()],
                 remote_hidden=False)
    fork_ctx = fork.write_commit('bar', content='bar1', message="in fork 1",
                                 parent=base_ctx)
    fork.set_phase('public', ['.'])

    code = main.command('pull-force-topic', b'zetop',
                        source=as_bytes(fork_path), rev=[fork_ctx.hex()])
    assert code == 0

    # TODO better lookup ?
    imported = main.repo[b'tip']
    assert imported.topic() == b'zetop'  # implied draft
    assert imported.description() == b'in fork 1'


def test_empty_pull(tmpdir):
    """Case where the pull turns out to be empty.

    See also heptapod#169
    """
    main_path = tmpdir.join('main')
    fork_path = tmpdir.join('fork')

    main, base_ctx = make_main_repo(tmpdir, main_path)

    fork = RepoWrapper.init(fork_path)
    fork.command('pull', as_bytes(main_path), rev=[base_ctx.hex()],
                 remote_hidden=False)
    fork_ctx = fork.write_commit('bar', content='bar1', message="in fork 1",
                                 parent=base_ctx)
    fork.set_phase('public', ['.'])

    main.command('pull', as_bytes(fork_path), remote_hidden=False)
    code = main.command('pull-force-topic', b'zetop',
                        source=as_bytes(fork_path), rev=[fork_ctx.hex()])
    assert code == 1


def test_change_topic_sanity(tmpdir):
    wrapper, base_ctx = make_main_repo(tmpdir, tmpdir.join('repo'))
    repo = wrapper.repo

    # early validation:
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('pull-force-topic', b' ')
    assert b'entirely of whitespace' in exc_info.value.args[0]

    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('pull-force-topic', b'tip')
    assert b'reserved' in exc_info.value.args[0]

    # inner check done in transaction
    with pytest.raises(error.Abort) as exc_info:
        change_topic(repo.ui, repo, b'sometopic', [base_ctx.node()])
    assert b'public' in exc_info.value.args[0]


def test_cleanup_tmp_bundle_exc(tmpdir):
    ui = make_ui(None)

    path = tmpdir.join('bundle')

    # no file at given path
    cleanup_tmp_bundle(ui, None, as_bytes(path))

    path.write('foo')
    # close fails (of course, fobj is None)
    cleanup_tmp_bundle(ui, None, as_bytes(path))


def test_already_obsolete(tmpdir):
    """Case where a remote changeset is locally obsolete

    This can happen in practice if two remote pulls are stacked and
    we already pulled one, making it actually obsolete because of the
    topic forcing.
    """
    main_path = tmpdir.join('main')
    fork_path = tmpdir.join('fork')

    main = make_main_repo(tmpdir, main_path)[0]
    amended = main.write_commit('foo', content='foo2', return_ctx=True)

    fork = RepoWrapper.init(fork_path)
    fork.command('pull', as_bytes(main_path), rev=[amended.hex()],
                 remote_hidden=False)

    main_path.join('foo').write('amended')
    main.command('amend', message=b"required in CI environment")

    main.command('pull-force-topic', b'zetop',
                 source=as_bytes(fork_path), rev=[amended.hex()])


def test_overlapping(tmpdir):
    """Case where two intersection pull_force_topic are called.

    this is heptapod#226, with at changeset part of several PRs
    """
    main_path = tmpdir.join('main')
    # actually we could use just one source, but it would be
    # less clear at first sight
    fork1_path = tmpdir.join('fork1')
    fork2_path = tmpdir.join('fork2')

    main, base_ctx = make_main_repo(tmpdir, main_path)

    fork1 = RepoWrapper.init(fork1_path)
    fork1.command('pull', as_bytes(main_path), rev=[base_ctx.hex()],
                  remote_hidden=False)
    fork1_ctx = fork1.write_commit('bar', content='bar1', message="in fork 1",
                                   parent=base_ctx)
    fork1.set_phase('public', ['.'])

    fork2 = RepoWrapper.init(fork2_path)
    fork2.command('pull', as_bytes(fork1_path), rev=[fork1_ctx.hex()],
                  remote_hidden=False)
    fork2_ctx = fork2.write_commit('bar', content='bar2', message="in fork 2",
                                   branch='other',
                                   parent=fork1_ctx)
    fork2.set_phase('public', ['.'])

    code = main.command('pull-force-topic', b'zetop',
                        source=as_bytes(fork1_path),
                        rev=[fork1_ctx.hex()])
    assert code == 0

    imported1 = main.repo[b'tip']
    assert imported1.topic() == b'zetop'  # implied draft
    assert imported1.description() == b'in fork 1'

    code = main.command('pull-force-topic', b'othertop',
                        source=as_bytes(fork2_path),
                        rev=[fork2_ctx.hex()])
    assert code == 0

    # TODO better lookup ?
    imported2 = main.repo[b'tip']
    assert imported2.topic() == b'othertop'  # implied draft
    assert imported2.description() == b'in fork 2'

    assert not imported1.instabilities()
    assert not {b'content-divergent', b'phase-divergent'}.intersection(
        imported2.instabilities())


def test_non_obsolete_revs(tmpdir):
    repo_path = tmpdir.join('repo')
    wrapper, base_ctx = make_main_repo(tmpdir, repo_path)
    amended = wrapper.write_commit('foo', content='foo2', return_ctx=False)

    repo_path.join('foo').write('amended')
    wrapper.command('amend', message=b"required in CI environment")

    from hgext3rd.heptapod.topic import non_obsolete_revs
    assert list(non_obsolete_revs(wrapper.repo,
                                  [base_ctx.node(), amended])
                ) == [0]
