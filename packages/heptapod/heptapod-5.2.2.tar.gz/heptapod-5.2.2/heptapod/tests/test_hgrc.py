# Copyright 2025 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import stat

from ..testhelpers import RepoWrapper
from ..hgrc import (
    init_project_hgrc_files,
)

PRIVATE_DIR = 0o700
PRIVATE_FILE = 0o600


def hgrc_lines(wrapper, ext=''):
    return [line.strip()
            for line in (wrapper.path / f'.hg/hgrc{ext}').readlines()]


def perms(path):
    # ignore bits that can be due to the path being in /tmp etc.
    return stat.S_IMODE(path.stat().mode)


def test_project_hgrc_files(tmpdir):
    gl_rpath = '@hashed/12/34/looongsha.hg'
    wrapper = RepoWrapper.init(tmpdir / gl_rpath)

    init_project_hgrc_files(wrapper.repo, gl_rpath, 'proj-no-group')
    includes = [line for line in hgrc_lines(wrapper)
                if line.startswith('%include')]
    assert includes == ['%include hgrc.managed']

    init_project_hgrc_files(wrapper.repo, gl_rpath, 'group/proj')
    lines = hgrc_lines(wrapper)
    assert '%include ../../../../../group/hgrc' in lines
    assert '%include hgrc.managed' in lines
    assert 'managed by Heptapod' in hgrc_lines(wrapper, ext='.managed')[0]
    group_path = tmpdir / 'group'
    assert group_path.exists()
    assert perms(group_path) == PRIVATE_DIR
    assert not (group_path / 'hgrc').exists()

    init_project_hgrc_files(wrapper.repo, gl_rpath, 'group/sub/proj')
    lines = hgrc_lines(wrapper)
    assert '%include ../../../../../group/sub/hgrc' in lines
    assert '%include hgrc.managed' in lines
    subgroup_path = group_path / 'sub'
    assert subgroup_path.exists()
    assert perms(subgroup_path) == PRIVATE_DIR
    assert not (group_path / 'hgrc').exists()
    subgroup_hgrc_path = (subgroup_path / 'hgrc')
    assert subgroup_hgrc_path.exists()
    assert perms(subgroup_hgrc_path) == PRIVATE_FILE
    assert '%include ../hgrc' in subgroup_hgrc_path.read()

    # Creating a new project in the same subgroup does not overwrite
    # existing group hgrc files
    subgroup_hgrc_path.write_binary(b"# just a comment, no inclusion")
    gl_rpath2 = '@hashed/56/78/looongsha.hg'
    wrapper = RepoWrapper.init(tmpdir / gl_rpath2)
    init_project_hgrc_files(wrapper.repo, gl_rpath2, 'group/sub/proj2')
    # Main assertion
    assert 'just a comment' in subgroup_hgrc_path.read()
    # Remaining general assertions for sanity
    lines = hgrc_lines(wrapper)
    assert '%include ../../../../../group/sub/hgrc' in lines
    assert '%include hgrc.managed' in lines
    assert perms(subgroup_path) == PRIVATE_DIR
    assert not (group_path / 'hgrc').exists()
    assert perms(subgroup_hgrc_path) == PRIVATE_FILE
