# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from heptapod.testhelpers import RepoWrapper
from ..branch import (
    gitlab_branches,
    read_gitlab_branches,
    write_gitlab_branches,
    gitlab_tags,
    write_gitlab_tags,
    remove_gitlab_tags,
)
from ..typed_ref import (
    gitlab_typed_refs_file_name,
    GITLAB_TYPED_REFS_MISSING,
)

GITLAB_BRANCHES_FILE_NAME = gitlab_typed_refs_file_name('branches')
GITLAB_TAGS_FILE_NAME = gitlab_typed_refs_file_name('tags')


def test_file_unicity():
    """Avoid major problems that too unitary tests could miss.

    Other tests would be perfectly happy to use the same file for
    branches or tags.
    """
    assert GITLAB_BRANCHES_FILE_NAME != GITLAB_TAGS_FILE_NAME


def test_read_gitlab_branches_v1(tmpdir):
    # this test depends on file layout details (so that it serves as a
    # proof of non tautology of all these tests)
    # and is specific to version 1 of the format.
    wrapper = RepoWrapper.init(tmpdir)
    sha1 = "fe54" * 10
    sha2 = "5c34" * 10
    tmpdir.join('.hg', 'store', GITLAB_BRANCHES_FILE_NAME.decode()
                ).write("\n".join((
                    "001",
                    "%s branch/some-branch" % sha1,
                    "%s even includes spaces" % sha2,
                )))
    repo = wrapper.repo
    assert read_gitlab_branches(repo) == {
        b'branch/some-branch': sha1.encode('ascii'),
        b'even includes spaces': sha2.encode('ascii'),
    }


def test_gitlab_branches_write_read(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    branches = {b'topic/default/truc': b'01cafe34' * 5}

    write_gitlab_branches(repo, branches)
    assert read_gitlab_branches(repo) == branches


def test_gitlab_branches(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    branches = {b'topic/default/truc': b'01cafe34' * 5}

    assert gitlab_branches(repo) is GITLAB_TYPED_REFS_MISSING

    write_gitlab_branches(repo, branches)
    # missing marker got invalidated
    assert gitlab_branches(repo) == branches
    # using cached value
    assert gitlab_branches(repo) == branches

    # values other than the missing marker get invalidated as well
    branches2 = {b'topic/default/thing': b'01cafe34' * 5}
    write_gitlab_branches(repo, branches2)
    assert gitlab_branches(repo) == branches2


def test_gitlab_tags_write_read(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    tags = {b'v1.2.3': b'01cafe34' * 5}

    write_gitlab_tags(repo, tags)
    assert gitlab_tags(repo) == tags


def test_gitlab_tags_remove(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    tags = {b'v1.2.3': b'01cafe34' * 5}

    write_gitlab_tags(repo, tags)
    remove_gitlab_tags(repo)
    assert gitlab_tags(repo) == GITLAB_TYPED_REFS_MISSING


def test_gitlab_tags(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    tags = {b'v1.2.3': b'01cafe34' * 5}

    assert gitlab_tags(repo) is GITLAB_TYPED_REFS_MISSING

    write_gitlab_tags(repo, tags)
    # missing marker got invalidated
    assert gitlab_tags(repo) == tags
    # using cached value
    assert gitlab_tags(repo) == tags

    # values other than the missing marker get invalidated as well
    branches2 = {b'topic/default/thing': b'01cafe34' * 5}
    write_gitlab_tags(repo, branches2)
    assert gitlab_tags(repo) == branches2
