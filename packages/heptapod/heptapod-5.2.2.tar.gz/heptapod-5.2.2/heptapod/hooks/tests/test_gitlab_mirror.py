# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from heptapod.testhelpers import (
    RepoWrapper,
    as_bytes,
)
from hgext3rd.heptapod.state_maintainer import GitLabStateMaintainer

from ..gitlab_mirror import mirror


def test_exception_catching(tmpdir, monkeypatch):
    wrapper = RepoWrapper.init(
        tmpdir,
        config=dict(extensions=dict(heptapod=''),
                    heptapod={b'repositories-root': as_bytes(tmpdir)},
                    ))
    repo = wrapper.repo

    def raiser(*a, **kw):
        raise RuntimeError('test-exc')

    monkeypatch.setattr(GitLabStateMaintainer, 'update_gitlab_references',
                        raiser)
    with pytest.raises(RuntimeError) as exc_info:
        mirror(repo.ui, repo)
    assert exc_info.value.args == ('test-exc', )
