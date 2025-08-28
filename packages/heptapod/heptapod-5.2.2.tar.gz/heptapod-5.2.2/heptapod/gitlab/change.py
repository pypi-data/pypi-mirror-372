# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generic GitLab integration logic.
"""
import attr

ZERO_SHA = b'0' * 40
"""GitLab zero SHA

Used to represent ref/branch creation or deletion.
As of this writing, it is actually equal to Mercurial's hex for null node,
and to the Git zero SHA, but could become different because of different rates
of adoption of SHA-2 in Mercurial, Git, and GitLab.
"""


@attr.s
class GitLabRefChange(object):
    """Represent a change to be performed in a target Git repo.

    Public attributes:

    - :attr:`ref`: Git ref name
    - :attr:`before`, :attr:`after`: Git SHAs

    These will be complemented with a system of options, e.g., to specify that
    a topic change actually comes with publication, leading to a deferred
    removal of the corresponding Git branch once all appropriate treatments are
    done, whether this removal is performed from here or by GitLab.
    """
    ref = attr.ib()
    before = attr.ib()
    after = attr.ib()

    def is_creation(self):
        return self.before == ZERO_SHA and self.after != ZERO_SHA

    def is_deletion(self):
        return self.after == ZERO_SHA and self.before != ZERO_SHA

    def export_for_hook(self, handler, native=False):
        """Prepare for actual hook sending.

        This depends on the `heptapod.native` boolean config item.
        """
        if native:

            def hg_sha(git_sha):
                if git_sha == ZERO_SHA:
                    return git_sha
                return handler.map_hg_get(git_sha)

            before_hg_sha = hg_sha(self.before)
            if before_hg_sha is None:
                # before is not known to Git, this is a corruption as in the
                # old heptapod/hg-git#3 and we must recover by creating the
                # Git branch anyway. On the 'after' side, it would mean
                # a severe inconsistency on our side
                # TODO in a later version we should
                # not convert at all, but we still rely as Git being
                # a giant cache of previous state of GitLab branches.
                before_hg_sha = ZERO_SHA
            after_hg_sha = hg_sha(self.after)
            if after_hg_sha is None:
                raise KeyError(self.after)
            return before_hg_sha, after_hg_sha

        return self.before, self.after
