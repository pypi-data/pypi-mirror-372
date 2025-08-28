# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from mercurial import (
    error,
    obsutil as hgobsutil,
)


def latest_unique_successor(ctx):
    """Return the latest of unique set of successors of a changeset.

    The changeset is given by its context, and a context is also returned,
    or `None` if there is no successor.

    `Abort` gets raised if there are several sets of successors.
    """
    repo = ctx.repo()
    successorssets = hgobsutil.successorssets(repo, ctx.node())
    if not successorssets:
        return None
    if len(successorssets) > 1:
        # There is more than one set of successors, so we have
        # a divergence, and we cannot handle it automatically
        raise error.Abort(("Changeset %r evolved into a "
                           "divergent state") % ctx.hex())

    # Single successor set: it can be one or many (split)
    # In all cases, we can take the last one.
    return repo[successorssets[0][-1]]
