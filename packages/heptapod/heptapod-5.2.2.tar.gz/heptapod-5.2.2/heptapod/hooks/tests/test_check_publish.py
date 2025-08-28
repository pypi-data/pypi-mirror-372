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
    phases,
    pycompat,
)
from heptapod.testhelpers import (
    RepoWrapper,
)

from .utils import switch_user
from ..perm import extract_published_revs


def init_repo(basedir):
    return RepoWrapper.init(
        basedir,
        config=dict(
            phases={'publish': 'no'},
            hooks={'pretxnclose.check_publish':
                   'python:heptapod.hooks.check_publish.check_publish'
                   },
            web={'allow-publish': 'maintainer',
                 'allow-push': '*',
                 },
        ))


def test_draft_publish(tmpdir):
    wrapper = init_repo(tmpdir)
    switch_user(wrapper, 'someone')
    ctx = wrapper.write_commit('foo', content='Foo', return_ctx=True)
    assert ctx.phase() == phases.draft

    with pytest.raises(error.Abort) as exc_info:
        wrapper.set_phase('public', [ctx.hex()])
    expected_msg = b'You are not authorised to publish changesets'
    assert expected_msg in exc_info.value.args[0]

    switch_user(wrapper, 'maintainer')
    wrapper.set_phase('public', [ctx.hex()])
    assert ctx.phase() == phases.public


def test_wrong_hook(tmpdir):
    wrapper = init_repo(tmpdir)
    ui = wrapper.repo.ui
    pretxn = b'pretxnclose.check_publish'
    hookdef = ui.config(b'hooks', pretxn)
    ui.setconfig(b'hooks', pretxn, b'')
    ui.setconfig(b'hooks', b'precommit.check_publish', hookdef)
    # precommit because that one does not swallow exceptions other
    # than abort
    with pytest.raises(error.ProgrammingError) as exc_info:
        wrapper.write_commit('foo')

    # ProgrammingError uses sysstr, because it's considered internal
    assert 'precommit' in exc_info.value.args[0]


class FakeTransaction(object):
    def __init__(self, phases):
        self.changes = {b'phases': phases}


def test_extract_published_revs_hg_5_3():
    txn = FakeTransaction({3: (phases.draft, phases.public),
                           19: (phases.secret, phases.public),
                           7: (phases.secret, phases.draft),
                           })
    assert set(extract_published_revs(txn)) == {3, 19}


def test_extract_published_revs_hg_5_4():
    txn = FakeTransaction([
        (pycompat.xrange(3, 5), (phases.draft, phases.public)),
        (pycompat.xrange(2), (phases.secret, phases.public)),
        (pycompat.xrange(7, 8), (phases.secret, phases.draft)),
    ])
    assert set(extract_published_revs(txn)) == {0, 1, 3, 4}
