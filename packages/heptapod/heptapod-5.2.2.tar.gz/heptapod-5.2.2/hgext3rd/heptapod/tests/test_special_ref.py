# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from hgext3rd.heptapod.branch import read_gitlab_typed_refs
from ..special_ref import (
    special_refs,
    write_special_refs,
    write_gitlab_special_ref,
    delete_gitlab_special_ref,
    GITLAB_TYPED_REFS_MISSING,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic='', evolve=''),
                                 ))


def test_special_ref_target(tmpdir):
    wrapper = make_repo(tmpdir)

    ref_name = b'merge-requests/1/head'

    # empty repo, the file doesn't even exist
    assert special_refs(wrapper.repo) is GITLAB_TYPED_REFS_MISSING

    base = wrapper.commit_file('foo')
    write_special_refs(wrapper.repo, {ref_name: base.hex()})

    # make sure we won't read from cache
    # TODO replace by reload() when available
    wrapper = LocalRepoWrapper.load(wrapper.path, base_ui=wrapper.repo.ui)

    assert special_refs(wrapper.repo) == {ref_name: base.hex()}

    # making target obsolete doesn't hide it to the special refs subsystem

    # updates are applied immediately (cache is updated)
    ctx = wrapper.commit_file('foo')
    write_special_refs(wrapper.repo, {ref_name: ctx.hex()})
    assert special_refs(wrapper.repo) == {ref_name: ctx.hex()}


def test_write_delete_gitlab_special_ref(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ref_name = b'pipelines/123'

    # deletion does not fail if state file is missing
    assert delete_gitlab_special_ref(repo, ref_name) is False

    base = wrapper.commit_file('foo')
    write_gitlab_special_ref(repo, ref_name, base)

    ref_type = 'special-refs'

    # direct read without cache
    assert read_gitlab_typed_refs(repo, ref_type) == {ref_name: base.hex()}

    # cache got updated (actually, created) anyway
    assert special_refs(repo)[ref_name] == base.hex()

    # passing a hex sha (bytes) also works and cache is updated
    ctx1 = wrapper.commit_file('foo')
    write_gitlab_special_ref(repo, ref_name, ctx1.hex())
    assert read_gitlab_typed_refs(repo, ref_type) == {ref_name: ctx1.hex()}
    assert special_refs(repo)[ref_name] == ctx1.hex()

    # deletion cases
    assert delete_gitlab_special_ref(repo, ref_name) is True
    assert read_gitlab_typed_refs(repo, ref_type) == {}  # without cache
    assert special_refs(repo) == {}

    # deletion does not fail if ref is already missing
    assert delete_gitlab_special_ref(repo, ref_name) is False

    # deletion can be achieved by writing the null SHA (same value for Git)
    write_gitlab_special_ref(repo, ref_name, ctx1.hex())
    assert special_refs(repo)[ref_name] == ctx1.hex()  # double-check
    write_gitlab_special_ref(repo, ref_name, b'0' * 40)
    assert read_gitlab_typed_refs(repo, ref_type) == {}  # without cache
    assert special_refs(repo) == {}
