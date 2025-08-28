# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import

import pytest
from heptapod.testhelpers import RepoWrapper
from mercurial import (
    encoding,
    pycompat,
)

from .utils import common_config

parametrize = pytest.mark.parametrize


def make_repo(tmpdir, config):
    full_config = common_config(tmpdir)
    full_config.update(config)
    wrapper = RepoWrapper.init(tmpdir.join('repo'), config=full_config)
    return wrapper.repo.ui


def test_multiple_heads_allow(tmpdir):
    ui = make_repo(tmpdir,
                   config=dict(heptapod={'allow-multiple-heads': 'yes'},
                               experimental={'single-head-per-branch': 'no'},
                               ))
    assert not ui.configbool(b'experimental', b'single-head-per-branch')


def test_bookmarks_allow(tmpdir):
    ui = make_repo(tmpdir,
                   config=dict(heptapod={'allow-bookmarks': 'yes'},
                               ))
    assert not ui.configbool(b'experimental', b'single-head-per-branch')
    assert ui.configbool(b'experimental',
                         b'hg-git.bookmarks-on-named-branches')


def test_auto_publish_nothing(tmpdir):
    ui = make_repo(tmpdir,
                   config=dict(
                       heptapod={'auto-publish': 'nothing'},
                       experimental={'topic.publish-bare-branch': 'yes'},
                   ))
    assert not ui.configbool(b'experimental', b'topic.publish-bare-branch')


def test_auto_publish_all(tmpdir):
    ui = make_repo(tmpdir,
                   config=dict(
                       heptapod={'auto-publish': 'all'},
                       phases={'publish': 'no'},
                   ))
    assert ui.configbool(b'phases', b'publish')


@parametrize('value', ('disabled', 'explicit'))
def test_clone_bundles_disabled(tmpdir, value):
    ui = make_repo(tmpdir,
                   config=dict(
                       heptapod={'clone-bundles': value},
                   ))
    assert not ui.configbool(b'clone-bundles', b'auto-generate.on-change')


def test_clone_bundles_on_change(tmpdir):
    ui = make_repo(tmpdir,
                   config=dict(
                       heptapod={'clone-bundles': 'on-change'},
                   ))
    assert ui.configbool(b'clone-bundles', b'auto-generate.on-change')


@parametrize('key',
             [('experimental', 'single-head-per-branch'),
              ('experimental', 'hg-git.bookmarks-on-named-branches'),
              ('experimental', 'topic.publish-bare-branch'),
              ('phases', 'publish'),
              ])
@parametrize('value', [True, False])
def test_lower_level_config_untouched(tmpdir, key, value):
    """This case is the default config in Heptapod normal conditions."""
    section, item = key
    ui = make_repo(tmpdir, config={section: {item: value}})
    assert ui.configbool(pycompat.sysbytes(section),
                         pycompat.sysbytes(item)) == value


@parametrize('env_value,expected',
             ((None, False),
              ('no', False),
              ('yes', True),
              ))
def test_native_from_env(env_value, expected,
                         tmpdir, monkeypatch):
    env = dict(encoding.environ)
    env_key = b'HEPTAPOD_HG_NATIVE'
    if env_value is not None:
        env_value = env_value.encode()
        env[env_key] = env_value

    monkeypatch.setattr(encoding, 'environ', env)

    ui = make_repo(tmpdir, {})

    # confirm that test patching worked
    assert ui.environ.get(env_key) == env_value
    # actual test assertions
    assert ui.configbool(b'heptapod', b'native') is expected
