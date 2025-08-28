# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from mercurial import error
import pytest

from heptapod.testhelpers import RepoWrapper
from ..branch import (
    DEFAULT_GITLAB_BRANCH_FILE_NAME,
    get_default_gitlab_branch,
    set_default_gitlab_branch,
)


def test_default_gitlab_branch(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    repo = wrapper.repo

    assert get_default_gitlab_branch(repo) is None
    set_default_gitlab_branch(repo, b'branch/default')

    assert get_default_gitlab_branch(repo) == b'branch/default'
    assert (tmpdir.join('.hg', DEFAULT_GITLAB_BRANCH_FILE_NAME.decode()).read()
            == 'branch/default')

    with pytest.raises(error.Abort):
        set_default_gitlab_branch(repo, b'')


def test_default_gitlab_branch_share(tmpdir):
    main_path = tmpdir.join('main')
    main = RepoWrapper.init(main_path)
    share = main.share(tmpdir.join('share'))

    assert get_default_gitlab_branch(main.repo) is None
    set_default_gitlab_branch(share.repo, b'branch/default')
    assert get_default_gitlab_branch(main.repo) == b'branch/default'
    assert get_default_gitlab_branch(share.repo) == b'branch/default'
