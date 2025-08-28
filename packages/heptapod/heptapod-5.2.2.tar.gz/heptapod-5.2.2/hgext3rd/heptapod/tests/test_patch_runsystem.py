# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
from io import BytesIO

from heptapod.testhelpers import (
    RepoWrapper,
    make_ui,
)
import os

from .utils import common_config


def test_hook(tmpdir):
    """Heptapod environ variables are passed over in hooks."""
    out_path = tmpdir.join('out')
    config = common_config(tmpdir)
    config['hooks'] = dict(commit="echo $HEPTAPOD_VARIABLE > %s" % out_path)
    wrapper = RepoWrapper.init(tmpdir.join('repo'), config=config)
    wrapper.repo.ui.environ[b'HEPTAPOD_VARIABLE'] = b'hepta-value'
    wrapper.write_commit("foo")
    assert out_path.read() == 'hepta-value\n'


def test_none():
    """Test exceptional call with no environment."""
    out = BytesIO()
    ui = make_ui(None)
    ui.environ[b'HEPTAPOD_VARIABLE'] = b'hepta-val'
    ui._runsystem(cmd=b"echo -n $HEPTAPOD_VARIABLE",
                  environ=None,
                  cwd=os.getcwd(),
                  out=out)
    assert out.getvalue() == b'hepta-val'
