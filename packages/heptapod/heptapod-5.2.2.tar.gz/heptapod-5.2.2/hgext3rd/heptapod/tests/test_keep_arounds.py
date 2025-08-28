# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from heptapod.testhelpers import RepoWrapper
from ..keep_around import (
    TYPED_REF_NAME,
    iter_keep_arounds,
    init_keep_arounds,
    create_keep_around,
)
from ..typed_ref import (
    gitlab_typed_refs_file_name,
    GITLAB_TYPED_REFS_MISSING,
)

KEEP_AROUND_FILE_NAME = gitlab_typed_refs_file_name(TYPED_REF_NAME).decode(
    'ascii')


def test_read_keep_arounds_v1(tmpdir):
    # this test depends on file layout details (so that it serves as a
    # proof of non tautology of all these tests)
    # and is specific to version 1 of the format.
    wrapper = RepoWrapper.init(tmpdir)
    sha1 = "fe54" * 10
    sha2 = "5c34" * 10
    (tmpdir / '.hg' / 'store' / KEEP_AROUND_FILE_NAME).write(
        "\n".join(("001", sha1, sha2)))
    repo = wrapper.repo
    assert [
        sha.decode('ascii') for sha in iter_keep_arounds(repo)
    ] == [sha1, sha2]


def test_create_keep_around(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo
    sha1 = b"ef57" * 10
    sha2 = b"c512" * 10
    create_keep_around(repo, sha1)
    assert list(iter_keep_arounds(repo)) == [sha1]
    create_keep_around(repo, sha2)
    assert list(iter_keep_arounds(repo)) == [sha1, sha2]


def test_init_keep_arounds(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo
    sha1 = b"ef57" * 10
    sha2 = b"c512" * 10
    init_keep_arounds(repo, (sha1, sha2))
    assert list(iter_keep_arounds(repo)) == [sha1, sha2]


def test_keep_arounds_file_missing(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo
    assert list(iter_keep_arounds(repo)) == [GITLAB_TYPED_REFS_MISSING]
