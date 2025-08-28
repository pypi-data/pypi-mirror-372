# Copyright 2020 Raphaël Gomès <raphael.gomes@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest
from heptapod.testhelpers import RepoWrapper
from mercurial_testhelpers import as_bytes

from .utils import common_config


def make_repo(tmpdir, path, heptapod_config_overrides=None):
    heptapod_config_overrides = heptapod_config_overrides or {}
    config = common_config(tmpdir)
    config.setdefault('heptapod', {}).update(heptapod_config_overrides)
    config['phases'] = dict(publish=False)
    wrapper = RepoWrapper.init(path, config=config)

    ctx = wrapper.commit_file('foo', content='foo0', message="default0")
    wrapper.command('bookmark', b'book1', rev=ctx.hex())
    wrapper.set_phase('public', ['.'])
    return wrapper


def get_revs_with_bookmark(wrapper):
    return wrapper.repo.revs(b'bookmark()')


@pytest.mark.parametrize("ignore_bookmarks", [True, False])
def test_pull_bookmarks(tmpdir, ignore_bookmarks):
    """Case where the pulled has a bookmark."""
    source_path = tmpdir.join('source')
    dest_path = tmpdir.join('dest')

    source = make_repo(tmpdir, source_path)

    dest = RepoWrapper.init(dest_path)

    assert len(get_revs_with_bookmark(dest)) == 0
    assert len(get_revs_with_bookmark(source)) == 1

    dest.repo.ui.setconfig(
        b'heptapod',
        b'exchange-ignore-bookmarks',
        ignore_bookmarks,
    )

    dest.command('pull', as_bytes(source_path), remote_hidden=False)

    if ignore_bookmarks:
        assert len(get_revs_with_bookmark(dest)) == 0
    else:
        assert list(get_revs_with_bookmark(dest)) == [0]


@pytest.mark.parametrize("ignore_bookmarks", [True, False])
def test_push_bookmarks(tmpdir, ignore_bookmarks):
    """Case where the pusher has a bookmark."""
    source_path = tmpdir.join('source')
    dest_path = tmpdir.join('dest')

    overrides = {
        'exchange-ignore-bookmarks': ignore_bookmarks,
    }
    source = make_repo(tmpdir, source_path,
                       heptapod_config_overrides=overrides)

    dest = RepoWrapper.init(dest_path)

    assert len(get_revs_with_bookmark(dest)) == 0
    assert len(get_revs_with_bookmark(source)) == 1

    source.command('push', as_bytes(dest_path), bookmark=[b'book1'])
    dest = RepoWrapper.load(dest_path)
    if ignore_bookmarks:
        assert len(get_revs_with_bookmark(dest)) == 0
    else:
        assert list(get_revs_with_bookmark(dest)) == [0]
