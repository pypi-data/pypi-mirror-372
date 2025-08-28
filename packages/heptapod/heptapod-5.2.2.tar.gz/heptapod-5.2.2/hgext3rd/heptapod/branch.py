# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Heptapod facilities for GitLab branches.

GitLab tags are a case of :mod:`typed refs <hgext3rd.heptapod.typed_ref>`,
we store them in their own state file, which represents the current view
by the other GitLab components, hence if there is an ongoing transaction,
it acts as a snapshot of the state at the beginning of the
transaction, so that we can notify them about the changes at the end
of the transaction.

Default GitLab branch:
  This a GitLab branch, e.g., ``branch/default`` rather than a Mercurial
  branch, e.g., ``default``.

  It is stored inside the repository directory, but not in the main store.
  In principle, different shares could have different default GitLab branches,
  if that were to be useful.

  For comparison, GitLab uses the value of `HEAD` on Git repositories for
  this.
"""
from mercurial.i18n import _
from mercurial import (
    hg,
    error,
)
from .typed_ref import (
    GITLAB_TYPED_REFS_MISSING,
    gitlab_typed_refs,
    read_gitlab_typed_refs,
    write_gitlab_typed_refs,
    remove_gitlab_typed_refs,
)
from .tag import *  # noqa: F401,F403 (reexports for retrocompat)

DEFAULT_GITLAB_BRANCH_FILE_NAME = b'default_gitlab_branch'

GITLAB_BRANCHES_MISSING = GITLAB_TYPED_REFS_MISSING  # retrocompat


def read_gitlab_branches(repo):
    return read_gitlab_typed_refs(repo, 'branches')


def gitlab_branches(repo):
    return gitlab_typed_refs(repo, 'branches')


def write_gitlab_branches(repo, gl_branches):
    """Write the GitLab branches mapping atomically.
    """
    return write_gitlab_typed_refs(repo, 'branches', gl_branches)


def remove_gitlab_branches(repo):
    remove_gitlab_typed_refs(repo, 'branches')


def get_default_gitlab_branch(repo):
    """Return the default GitLab branch name, or ``None`` if not set."""
    shared_from = hg.sharedreposource(repo)
    if shared_from is not None:
        repo = shared_from
    branch = repo.vfs.tryread(DEFAULT_GITLAB_BRANCH_FILE_NAME)
    # (hg 5.4) tryread returns empty strings for missing files
    if not branch:
        return None
    return branch


def set_default_gitlab_branch(repo, target):
    if not target:
        raise error.Abort(_("The default GitLab branch cannot be an "
                            "empty string."))
    shared_from = hg.sharedreposource(repo)
    if shared_from is not None:
        repo = shared_from

    with repo.wlock():
        repo.vfs.write(DEFAULT_GITLAB_BRANCH_FILE_NAME, target)
