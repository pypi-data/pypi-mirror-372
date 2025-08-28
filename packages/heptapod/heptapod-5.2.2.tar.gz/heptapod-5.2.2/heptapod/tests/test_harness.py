# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""A minimal py.test to make sure the testing harness works.
"""
import subprocess


def test_hg_install():
    vinfo = subprocess.check_output(('hg', 'version'))
    assert vinfo.startswith(b'Mercurial')
