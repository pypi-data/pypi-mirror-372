# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
import pytest
from mercurial import (
    error,
)
from heptapod.testhelpers import (
    RepoWrapper,
)

from .utils import switch_user


def init_repo(basedir):
    return RepoWrapper.init(
        basedir,
        config=dict(
            hooks={'pretxnopen.check_write':
                   'python:heptapod.hooks.perm.check_write'
                   },
            web={'allow-push': 'developer',
                 },
        ))


def test_write_empty_repo(tmpdir):
    wrapper = init_repo(tmpdir)
    switch_user(wrapper, 'guest')
    with pytest.raises(error.HookAbort) as exc_info:
        wrapper.write_commit('foo', content='Foo', return_ctx=True)

    assert b'pretxnopen.check_write' in exc_info.value.args[0]
    switch_user(wrapper, 'developer')
    ctx = wrapper.write_commit('foo', message='developer is accepted',
                               return_ctx=True)
    assert ctx.description() == b'developer is accepted'


def test_phase_change(tmpdir):
    wrapper = init_repo(tmpdir)
    switch_user(wrapper, 'developer')
    ctx = wrapper.write_commit('foo', content='Foo', return_ctx=True)

    switch_user(wrapper, 'guest')
    with pytest.raises(error.HookAbort) as exc_info:
        wrapper.set_phase('public', [ctx.hex()])
    assert b'pretxnopen.check_write' in exc_info.value.args[0]


def test_wrong_hook(tmpdir):
    wrapper = init_repo(tmpdir)
    ui = wrapper.repo.ui
    pretxn = b'pretxnopen.check_write'
    hookdef = ui.config(b'hooks', pretxn)
    ui.setconfig(b'hooks', pretxn, b'')
    ui.setconfig(b'hooks', b'precommit.check_write', hookdef)
    # precommit because that one does not swallow exceptions other
    # than abort
    with pytest.raises(error.ProgrammingError) as exc_info:
        wrapper.write_commit('foo')

    assert 'precommit' in exc_info.value.args[0]
