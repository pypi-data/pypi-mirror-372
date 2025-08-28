# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Heptapod specific facilities for GitLab typed refs.

GitLab typed refs:

  GitLab typed refs are pointers to Mercurial changesets that the Rails
  application believes to be actual Git refs having significant
  types, such as branches or tags.

  Typed refs have short names beside the full ref path: a branch with name
  'foo' has full ref path 'refs/heads/foo', etc.

  GitLab typed refs are updated automatically if needed by each transaction,
  applying several rules tailored for
  good interaction with other GitLab components. They are not implemented
  as bookmarks because they are not meant to be exposed to Mercurial clients.

  GitLab typed refs are kept in files that represents the last state that was
  exposed to other GitLab components (notably, the Rails application). In case
  there is an ongoing transaction, the file represents the state at the
  beginning of the transaction, and is updated at the end of transaction.
  Its uses include:

  - sending pre- and post-receive calls to the Rails application based on
    comparisons with the previous state.
  - fast querying by GitLab branch in HGitaly. While it is possible for HGitaly
    to implement the mapping to GitLab branches in a stateless way, it is very
    bad for performance to do it in all read operations.

  The state cannot be reconstructed, since it records what other components
  have already seen. But it can be reinitialized: GitLab will fail to update
  the Merge Requests that should have been affected by the current transaction,
  fail to create new Pipelines and generally miss all the consequences of
  the current transaction. Initializing it at import or in an otherwise
  empty transaction should not create any problem.

  We currently track several types of refs, notably ``branches`` and ``tags``,
  each in its separate file for vastly different updating profiles: there is
  usually more tags than branches, but they don't get updated often. On the
  other hand, there are usually fewer visible branches, but each transaction
  updates at least one of them.

  File format: version preamble (common to all versions):

  - first 3 bytes: decimal string representation of the version number, padded
    with left zeros (spaces also accepted for reading)
  - byte 4: Unix End-Of-Line (LF, 0x10)

  File format: version 1 (after version preamble)

  - line-based, each line terminated the Unix way (LF, 0x10)
  - one GitLab ref per line
  - each line is made of the hexadecimal Mercurial changeset ID, followed by
    exactly one space character, then by the GitLab ref short name (bytes with
    no encoding assumption).

    Example for the branches file::

        01ca23fe01ca23fe01ca23fe01ca23fe01ca23fe branch/default

    Example for the tags file::

        01ca23fe01ca23fe01ca23fe01ca23fe01ca23fe v1.2.3


Default GitLab branch:
  This a GitLab branch, e.g., ``branch/default`` rather than a Mercurial
  branch, e.g., ``default``.

  It is stored inside the repository directory, but not in the main store.
  In principle, different shares could have different default GitLab branches,
  if that were to be useful.

  For comparison, GitLab uses the value of `HEAD` on Git repositories for
  this.
"""
GITLAB_TYPED_REFS_FILE_CURRENT_VERSION = 1

GITLAB_TYPED_REFS_MISSING = object()
"""Cacheable marker to avoid repeated read attempts if missing"""


def gitlab_typed_refs_file_name(type_name):
    return ('gitlab.' + type_name).encode()


def read_gitlab_typed_refs_file_version(fobj):
    """Read the version and leave `fobj` at the start of actual data.
    """
    version_line = fobj.read(4)
    # TODO proper exception
    assert version_line.endswith(b'\n')
    return int(version_line)  # ignores left 0 padding, whitespace and EOL


def write_gitlab_typed_refs_file_version(
        fobj,
        version=GITLAB_TYPED_REFS_FILE_CURRENT_VERSION):
    fobj.write(b"%03d\n" % version)


def read_gitlab_typed_refs(repo, type_name):
    """Return the GitLab named refs mapping for the given type, as a dict.

    The keys of the returned :class:`dict` are typed ref names (by opposition
    to full paths). Examples:

    - ``topic/stable/fix1`` (branch)
    - ``v1.2.3`` (tag).

    The values are Mercurial hexadecimal changeset ids, as :class:`bytes`
    """
    # TODO exceptions other than `FileNotFoundException`, which is fine
    with repo.svfs(gitlab_typed_refs_file_name(type_name), mode=b'rb') as fobj:
        assert read_gitlab_typed_refs_file_version(fobj) == 1
        return {ref_name.strip(): sha for sha, ref_name in
                (line.split(b' ', 1) for line in fobj)}


def remove_gitlab_typed_refs(repo, type_name):
    repo.svfs.unlink(gitlab_typed_refs_file_name(type_name))


def gitlab_typed_refs(repo, type_name):
    """Return GitLab named refs for given type or GITLAB_TYPED_REFS_MISSING.

    The state file can still optional at this stage.
    Callers have to check for GITLAB_TYPED_REFS_MISSING and fall back to
    other means.

    Will eventually become a property on the repo object. Since our use case
    is different than what Mercurial usual filecaches are meant for, it
    is safer to do it directly in this first version.
    """
    # TODO rename glb as glr
    cache_attr = '_gitlab_refs_' + type_name
    glb = getattr(repo, cache_attr, None)
    if glb is not None:
        return glb

    try:
        glb = read_gitlab_typed_refs(repo, type_name)
    except FileNotFoundError:
        glb = GITLAB_TYPED_REFS_MISSING
    setattr(repo, cache_attr, glb)
    return glb


def write_gitlab_typed_refs(repo, type_name, refs_by_name):
    """Write a file for a type of GitLab refs.

    :param refs_by_name: :class:`dict` mapping typed ref names (example
      for ``type_name='branch'``: ``branch/stable``) to Mercurial hexadecimal
    changeset ids (as :class:`bytes`).
    """
    setattr(repo, '_gitlab_refs_' + type_name, None)
    with repo.lock():
        with repo.svfs(gitlab_typed_refs_file_name(type_name),
                       mode=b'wb',
                       atomictemp=True,
                       checkambig=True) as fobj:
            write_gitlab_typed_refs_file_version(fobj)
            for name, sha_hex in refs_by_name.items():
                fobj.write(b"%s %s\n" % (sha_hex, name))
            # atomictempfile does not expose flush(), so there's no
            # point trying an fsync(). Mercurial does not seem to use
            # fsync() anyway.
