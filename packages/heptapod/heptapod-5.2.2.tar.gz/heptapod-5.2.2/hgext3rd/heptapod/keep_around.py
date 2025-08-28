# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Handling of GitLab keep-arounds.

GitLab uses Git refs to prevent garbage collecting of commits that are
referenced in its database. While Mercurial does not have a garbage collector
it could grow one in the future for obsolete changesets, hence we better
not lose that information.

There is no reason to store keep-arounds as typed refs in Mercurial context,
though. We use a simpler format.

File format:

- version preamble (same as for typed refs)
- one hexadecimal Mercurial changeset ID per line.

Writes are append-only, there is no update or removal of keep-arounds.
For reads, we provide only a simple iterator.
"""
from contextlib import contextmanager
from .typed_ref import (
    gitlab_typed_refs_file_name,
    read_gitlab_typed_refs_file_version,
    write_gitlab_typed_refs_file_version,
    GITLAB_TYPED_REFS_MISSING,
)
TYPED_REF_NAME = 'keep-arounds'

KEEP_AROUND_REF_PREFIX = b'refs/keep-around/'
KEEP_AROUND_REF_PREFIX_LEN = len(KEEP_AROUND_REF_PREFIX)


def parse_keep_around_ref(ref_path):
    """Return target sha from ref_path, or ``None`` if not a keep-around ref.

    :param ref_path: full ref path, as :class:`bytes`
    :rtype: :class:`bytes

    Examples::

      >>> parse_keep_around_ref(
      ...     b'refs/keep-around/006e626febb896ca416bec68734a6199f4de5632')
      b'006e626febb896ca416bec68734a6199f4de5632'
      >>> parse_keep_around_ref(b'refs/merge-requests/1/head') is None
      True

    Special case for robustness, uniformity with other refs and convenience::

      >>> parse_keep_around_ref(None) is None
      True
    """
    if ref_path is None or not ref_path.startswith(KEEP_AROUND_REF_PREFIX):
        return None
    return ref_path[KEEP_AROUND_REF_PREFIX_LEN:]


@contextmanager
def open_keep_arounds_file(repo):
    """Context manager that opens the keep-arounds state file.

    The file format version is checked and the file handle is left after
    the preamble.

    If the state file is missing, yields :const:`GITLAB_TYPED_REFS_MISSING`
    """
    try:
        with repo.svfs(gitlab_typed_refs_file_name(TYPED_REF_NAME),
                       mode=b'rb') as fobj:
            assert read_gitlab_typed_refs_file_version(fobj) == 1
            yield fobj
    except FileNotFoundError:
        yield GITLAB_TYPED_REFS_MISSING


def iter_keep_arounds(repo):
    """Generator for existing keep-arounds.

    If the state file is missing, yields only
    :const:`GITLAB_TYPED_REFS_MISSING`.

    A future garbage collector could use this method to create a set of
    changesets to exclude from collection.
    """
    with open_keep_arounds_file(repo) as fobj:
        if fobj is GITLAB_TYPED_REFS_MISSING:
            yield fobj
            return

        for line in fobj:
            yield line.strip()


def create_keep_around(repo, hg_sha):
    """Write a new keep around to disk.

    :param hg_sha: Mercurial hexadecimal changeset ID, given as :class:`bytes`
    """
    with repo.lock():
        with repo.svfs(gitlab_typed_refs_file_name(TYPED_REF_NAME),
                       mode=b'ab',
                       checkambig=True) as fobj:
            if fobj.tell() == 0:  # new file
                write_gitlab_typed_refs_file_version(fobj)
            fobj.write(hg_sha)
            fobj.write(b'\n')


def init_keep_arounds(repo, hg_shas):
    """Initialize the state file from any iterable of SHAs.

    The state file is created or entirely remplaced.
    :param hg_shas: iterable of Mercurial hexadecimal changeset IDs,
        given as :class:`bytes`
    """
    with repo.lock():
        with repo.svfs(gitlab_typed_refs_file_name(TYPED_REF_NAME),
                       mode=b'wb',
                       atomictemp=True,
                       checkambig=True) as fobj:
            write_gitlab_typed_refs_file_version(fobj)
            for hg_sha in hg_shas:
                fobj.write(hg_sha)
                fobj.write(b'\n')
