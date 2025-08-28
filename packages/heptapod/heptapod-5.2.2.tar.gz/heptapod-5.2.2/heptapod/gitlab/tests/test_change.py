# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for the GitRefChange object.

(that may later be renamed as GitLabRefChange or other so that it doesn't
sound too weird once we are in full native mode)

TODO move now to heptapod.gitlab.tests
"""
import pytest
from heptapod.gitlab.change import (
    GitLabRefChange as RefChange,
    ZERO_SHA,
)


class FakeHandler:

    def __init__(self, **git2hg):
        self.git2hg = git2hg

    def map_hg_get(self, git_sha):
        return self.git2hg.get(git_sha.decode())


def test_export_for_hook_errors():
    handler = FakeHandler(known_git_sha=b'123d12fa45')

    ch = RefChange(b'branch/something', b'known_git_sha', b'the_unknown')
    with pytest.raises(KeyError) as exc_info:
        ch.export_for_hook(handler=handler, native=True)
    assert exc_info.value.args[0] == b'the_unknown'

    ch = RefChange(b'branch/something', b'unknown', b'known_git_sha')
    assert ch.export_for_hook(handler=handler, native=True) == (
        ZERO_SHA, b'123d12fa45')
