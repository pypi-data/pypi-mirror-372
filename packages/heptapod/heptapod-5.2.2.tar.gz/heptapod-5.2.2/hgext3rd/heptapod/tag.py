# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Heptapod facilities for GitLab tags.

GitLab tags are a case of :mod:`typed refs <hgext3rd.heptapod.typed_ref>`,
we store them in their own state file, which represents the current view
by the other GitLab components, hence if there is an ongoing transaction,
it acts as a snapshot of the state at the beginning of the
transaction, so that we can notify them about the changes at the end
of the transaction.

We would not need this if Mercurial had a way to access tags changes from
a transaction object. Maybe it will in the future.
"""
from .typed_ref import (
    gitlab_typed_refs,
    read_gitlab_typed_refs,
    write_gitlab_typed_refs,
    remove_gitlab_typed_refs,
)


def read_gitlab_tags(repo):
    return read_gitlab_typed_refs(repo, 'tags')


def gitlab_tags(repo):
    return gitlab_typed_refs(repo, 'tags')


def write_gitlab_tags(repo, gl_tags):
    """Write the GitLab tags mapping atomically.
    """
    return write_gitlab_typed_refs(repo, 'tags', gl_tags)


def remove_gitlab_tags(repo):
    remove_gitlab_typed_refs(repo, 'tags')
