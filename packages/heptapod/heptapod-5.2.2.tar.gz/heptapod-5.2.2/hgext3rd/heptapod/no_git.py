# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Interaction with GitLab for native Mercurial repos.

Although we don't need to convert native repos to Git, we still have to
maintain the GitLab branches, and fire appropriate notifications.
"""
from __future__ import absolute_import
import attr
import collections
import itertools

from mercurial.node import hex
from heptapod.gitlab.branch import (
    gitlab_branch_from_ref,
    gitlab_branch_ref,
)
from heptapod.gitlab.tag import gitlab_tag_ref

from .branch import (
    GITLAB_TYPED_REFS_MISSING,
    get_default_gitlab_branch,
    set_default_gitlab_branch,
    gitlab_branches,
    gitlab_tags,  # TODO move in separate module?
)
from .state_maintainer import GitLabStateMaintainer


@attr.s
class RefsByType:
    """Record GitLab refs, with a set for each type of ref.

    Types of ref can be `tags`, `refs` or whatever becomes useful to track.
    """
    heads = attr.ib(default=attr.Factory(set))
    tags = attr.ib(default=attr.Factory(set))

    def __iter__(self):
        return itertools.chain(self.heads, self.tags)

    def __bool__(self):
        return bool(self.heads) or bool(self.tags)


class NoGitStateMaintainer(GitLabStateMaintainer):
    """Maintain GitLab state for native Mercurial without any Git repository.

    Use of this class must be restricted to native Mercurial repositories
    running in "fully native" mode, but that is the concern of configuration,
    which should in turn be passed along by the Rails application or other
    relevant GitLab components.
    """

    def __init__(self, ui, repo):
        self.ui = ui
        self.repo = repo

        self.unfiltered_repo = self.repo.unfiltered()
        self._default_git_ref = None

        gl_branches = gitlab_branches(repo)
        if gl_branches is GITLAB_TYPED_REFS_MISSING:
            # should mean we are on an empty repo
            gl_branches = {}

        gl_tags = gitlab_tags(repo)
        if gl_tags is GITLAB_TYPED_REFS_MISSING:
            # should mean we are on an empty repo
            gl_tags = {}

        self.gitlab_refs = {gitlab_branch_ref(gl_branch): sha
                            for gl_branch, sha in gl_branches.items()}
        self.gitlab_refs.update((gitlab_tag_ref(gl_tag), sha)
                                for gl_tag, sha in gl_tags.items())

    def map_hg_get(self, sha):
        return sha

    def sync(self):
        """Main entry point for synchronisation of shared state with GitLab."""
        self.update_gitlab_references()

    def get_default_gitlab_ref(self):
        res = self._default_git_ref
        if res is None:
            gl_branch = get_default_gitlab_branch(self.repo)
            if gl_branch is not None:
                res = gitlab_branch_ref(gl_branch)
            self._default_git_ref = res
        return res

    def set_default_gitlab_ref(self, new_default_ref):
        new_gl_branch = gitlab_branch_from_ref(new_default_ref)
        self.repo.ui.note(
            b"Setting GitLab branch to %s" % new_gl_branch)
        set_default_gitlab_branch(self.repo, new_gl_branch)

        # cache invalidation
        self._default_git_ref = None

    def hg_sha_from_gitlab_sha(self, sha):
        return sha

    def gitlab_sha_from_hg_sha(self, sha):
        return sha

    def extract_bookmarks(self, git_refs):
        """Update git_refs with current bookmarks."""
        for name, node in self.repo._bookmarks.items():
            git_refs[hex(node)].heads.add(gitlab_branch_ref(name))

    def extract_all_gitlab_refs(self):
        """Heptapod version of GitHandler.get_exportable() for native case.

        We should be able to do without tags, as they are handled separately
        (no persistent state in Mercurial repo, just notifications by
        :meth:heptapod_compare_tags)
        """
        gitlab_refs = collections.defaultdict(RefsByType)
        self.extract_bookmarks(gitlab_refs)
        self.extract_current_gitlab_branches(gitlab_refs)
        return gitlab_refs
