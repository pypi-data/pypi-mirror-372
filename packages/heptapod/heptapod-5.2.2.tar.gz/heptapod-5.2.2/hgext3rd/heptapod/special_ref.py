# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Handling of GitLab special refs.

This module provides facilities to store and retrieve special-purpose
GitLab refs, such as `refs/merge_requests/1/head`. These have internal
semantics for the GitLab application and are not general Git concepts,
although Git users can see them, e.g, with `git ls-remote`. Other forges do
something similar, e.g., GitHub has `refs/pull/23/head` etc.

There is a closed list of GitLab special refs: :const:`SPECIAL_REFS`.

The storage backend is a state file similar to those used for GitLab branches
and tags, with an important difference in semantics: special refs are not
meant to represent the state at the beginning of the current transaction.
Relevant caches are updated (or invalidated) on the fly.
"""
from mercurial.context import changectx
from mercurial.node import nullhex
from .branch import (
    GITLAB_TYPED_REFS_MISSING,
    gitlab_typed_refs,
    write_gitlab_typed_refs,
)

SPECIAL_REFS = (b'merge-requests',
                b'environments',
                b'pipelines')
"""All recognized kinds of GitLab special refs.

The source of truth for this is a list of constants in the Rails Repository
model. Excerpt from `/app/models/repository.rb`::

  class Repository
    REF_MERGE_REQUEST = 'merge-requests'
    REF_KEEP_AROUND = 'keep-around'
    REF_ENVIRONMENTS = 'environments'
    REF_PIPELINES = 'pipelines'

    ARCHIVE_CACHE_TIME = 60  # Heptapod comment: proves the list is finished.

The case of keep-around refs will be treated separately because they are

1. permanent
2. potentially many
3. reducible to a list of SHAs

A simple append-only file would thus be preferable for them.
"""


def write_special_refs(repo, special_refs):
    """Write the given refs to disk and update the cache on repo object.

    This replaces all existing refs with the new ones.
    """
    res = write_gitlab_typed_refs(repo, 'special-refs', special_refs)
    repo._gitlab_refs_special = special_refs
    return res


def special_refs(repo):
    """Retrieve all special refs

    :return: a `dict` instance mapping special ref names, such as
        `pipelines/49` to the target changeset ids. This `dict` is actually
        the cache object on the repo, so that any update of it will immediately
        be visible, but won't be persisted until :func:`write_special_refs` is
        called.
    """
    return gitlab_typed_refs(repo, 'special-refs')


def parse_special_ref(ref_path):
    """Parse a special ref full path, returning only its name as a special ref.

    :returns: the name as a special ref, or `None` if not a special ref.

    Examples:

    >>> parse_special_ref(b'refs/merge-requests/base/34')
    b'merge-requests/base/34'
    >>> parse_special_ref(b'refs/heads/a-branch') is None
    True
    >>> parse_special_ref(b'refs/something-else-maybe-not-gitlab') is None
    True
    >>> parse_special_ref(b'not even a ref!') is None
    True
    """
    split = ref_path.split(b'/', 2)
    if len(split) < 3 or split[0] != b'refs' or split[1] not in SPECIAL_REFS:
        return None

    return ref_path[5:]


def write_gitlab_special_ref(repo, name, target):
    """Write a new special ref.

    This goes all the way to the disk, which is a common end use-case, but
    should not be done in a loop. Callers wanting to write a batch
    of special refs should rather use :func:`write_special_refs` directly.

    :param name: the name of the ref, as a special ref, e.g.
       `merge_requests/heads/123`. This is because the caller will
       need to already be sure it is a special ref before calling this
    :param target: full changeset id, as :class:`bytes` or
      :class:`changectx` instance. As a special case, passing the null
      hexadecimal changeset value is converted into an outright deletion, as
      in internal Git exchange protocol.
    """
    if isinstance(target, changectx):
        target = target.hex()

    srefs = special_refs(repo)
    if srefs is GITLAB_TYPED_REFS_MISSING:
        srefs = {}

    if target == nullhex:
        srefs.pop(name)
    else:
        srefs[name] = target
    write_special_refs(repo, srefs)


def delete_gitlab_special_ref(repo, name):
    """Delete a single ref.

    As with :func:`write_gitlab_special_ref`, for batch operations, it
    is preferrable to use `write_special_refs` directly.

    :param name: the name of the ref, as a special ref, e.g.
       `merge_requests/heads/123`. This is because the caller will
       need to already be sure it is a special ref before calling this
    :returns: ``True`` if the ref was really deleted, ``False`` if it was
       not present.
    """
    srefs = special_refs(repo)
    if srefs is GITLAB_TYPED_REFS_MISSING:
        return False

    result = srefs.pop(name, None) is not None
    write_special_refs(repo, srefs)
    return result
