# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    error,
)
from .perm import validate_hook_type


def forbid_commit(repo, *args, **kwargs):
    validate_hook_type(b'precommit', **kwargs)
    if repo.wvfs.exists(b'.hgsub'):
        raise error.Abort(b"This version of Heptapod cannot commit "
                          b"server-side if there are subrepos around. "
                          b"That could ruin .hgsubstate. "
                          b"A subsequent version may reenable this.")
