# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Specific and not-yet externalized test helpers."""

from mercurial_testhelpers.repo_wrapper import (  # noqa: F401
    as_bytes,
    make_ui,
)
from .hg import RepoWrapper

# compatibility alias
LocalRepoWrapper = RepoWrapper
