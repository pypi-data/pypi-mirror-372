# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
from heptapod.testhelpers import (
    RepoWrapper,
)


def init_repo(basedir):
    return RepoWrapper.init(
        basedir,
        config=dict(
            phases={'publish': 'no'},
            hooks={'pretxnclose':
                   'python:heptapod.hooks.dev_util.print_heptapod_env'
                   },
        ))


def test_heptapod_env(tmpdir):
    wrapper = init_repo(tmpdir)
    ui = wrapper.repo.ui

    records = []
    orig_status = ui.status

    def status_recorder(*msg, **opts):
        records.append(dict(messages=msg, options=opts))
        return orig_status(*msg, **opts)

    ui.status = status_recorder
    ui.environ = ui.environ.copy()  # don't risk writing into os.environ
    ui.environ[b'HEPTAPOD_SOMETHING'] = b'useful'

    wrapper.write_commit('trigger')
    assert any(repr(('HEPTAPOD_SOMETHING', 'useful'))
               in r['messages'][0].decode()
               for r in records if r['messages'])
