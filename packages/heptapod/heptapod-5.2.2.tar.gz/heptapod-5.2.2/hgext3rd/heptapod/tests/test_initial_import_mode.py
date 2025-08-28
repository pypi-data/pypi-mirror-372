# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
from heptapod.testhelpers import RepoWrapper

from .utils import common_config


def test_initial_import_settings(tmpdir):
    config = common_config(tmpdir)
    config['heptapod'] = {'initial-import': 'yes'}
    wrapper = RepoWrapper.init(tmpdir.join('repo'), config=config)

    ui = wrapper.repo.ui
    assert not ui.configbool(b'experimental', b'single-head-per-branch')
    assert not ui.configbool(b'experimental', b'topic.publish-bare-branch')
