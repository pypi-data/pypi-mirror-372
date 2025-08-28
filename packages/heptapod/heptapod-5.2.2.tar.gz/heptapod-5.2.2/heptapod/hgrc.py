# Copyright 2025 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Management of Project and Group Mercurial configuration files.
"""
import os
from pathlib import Path

INITIAL_PROJECT_HGRC_HEADER = b'\n'.join((
    b"# This is the specific configuration for this repository",
    b"# You may modify it on the file system if you follow the explanations",
    b"# in comments below",
    b"",
))

INITIAL_PROJECT_GROUP_INCLUSION_HEADER = b'\n'.join((
    b"#",
    b"# By default, it includes the configuration from the enclosing group",
    b"# or user namespace, but all the settings defined in the present file",
    b"# will take precedence",
    b"# as long as they are below the %include line",
    b"# You may also remove the %include line altogether, although it is",
    b"# cleaner to use the `PUT projects/:id/hgrc` API endpoint with",
    b'# `"inherit": false`` for this purpose. ',
    b"",
    b"# Group-level configuration:",
    b"",
))

INITIAL_PROJECT_HGRC_MANAGED_INCLUSION = b'\n'.join((
    b"# specific configuration managed by Heptapod. "
    b"# Do not remove it, it can come back at any time.",
    b"%include hgrc.managed",
    b"",
))

INITIAL_PROJECT_HGRC_MANAGED = b'\n'.join((
    b"# This file is entirely managed by Heptapod\n",
    b"# Any modification you might do can disappear at any time\n"
))


INITIAL_SUBGROUP_HGRC = b'\n'.join((
    b"# This is the Mercurial configuration for this subgroup.",
    b"# You may modify it freely at your will.",
    b"#",
    b"# By default, it includes the configuration from the enclosing",
    b"# group, but all the settings defined in the present file will",
    b"# take precedence as long as they are below the %include line",
    b"# You may also remove the %include line altogether if you prefer.",
    b"",
    b"# enclosing group configuration",
    b"%include ../hgrc",
    b"",
))

NO_PARENT = Path('.')


def init_project_hgrc_files(repo, repo_rel_path, project_full_path):
    """Create all needed configuration files for the given project.

    :param repo_rel_path: the relative path from storage root of the
        repository, as given in the `relative_path` field of the Gitaly
        ``Repository`` message
    :param project_full_path: the full Project applicative path,
        as given in the `gl_project_path` field of the Gitaly ``Repository``
        message.
    """
    split = project_full_path.rsplit('/', 1)
    if len(split) == 1:
        group_rpath = None
    else:
        group_rpath = Path(split[0])
        hgrc_rpath = Path(repo_rel_path) / '.hg'
        # Path.relative_to gains the `walk_up` option in Python 3.12
        group_rel_repo_path = os.path.relpath(group_rpath, hgrc_rpath)
        group_include_line = "%include {}\n".format(
            Path(group_rel_repo_path) / 'hgrc')

    orig_umask = os.umask(0o077)
    try:
        with repo.wlock():
            with repo.vfs(b'hgrc',
                          mode=b'wb',
                          atomictemp=True,
                          checkambig=True) as fobj:
                fobj.write(INITIAL_PROJECT_HGRC_HEADER)
                if group_rpath is not None:
                    fobj.write(INITIAL_PROJECT_GROUP_INCLUSION_HEADER)
                    fobj.write(os.fsencode(group_include_line))
                fobj.write(INITIAL_PROJECT_HGRC_MANAGED_INCLUSION)

            with repo.vfs(b'hgrc.managed',
                          mode=b'wb',
                          atomictemp=True,
                          checkambig=True) as fobj:
                fobj.write(INITIAL_PROJECT_HGRC_MANAGED)

            if group_rpath is None:
                return

            repo_path = Path(os.fsdecode(repo.path))
            group_abspath = (repo_path / group_rel_repo_path).resolve()
            os.makedirs(group_abspath, exist_ok=True)
            parent_group = group_rpath.parent
            while parent_group != NO_PARENT:
                group_hgrc = (group_abspath / 'hgrc')
                if not group_hgrc.exists():
                    group_hgrc.write_bytes(INITIAL_SUBGROUP_HGRC)
                group_rpath = parent_group
                parent_group = group_rpath.parent
                group_abspath = group_abspath.parent
    finally:
        os.umask(orig_umask)
