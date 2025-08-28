# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import cmdutil, commands, error


def mirror(ui, repo, *args, **kwargs):
    repo.ui.note(b"Heptapod mirror starting")
    gitlab_mirror = cmdutil.findcmd(b'gitlab-mirror', commands.table)[1][0]
    try:
        gitlab_mirror(ui, repo)
    except error.Abort:
        raise
    except Exception:
        repo.ui.traceback()
        raise
    repo.ui.note(b"Heptapod mirror done\n")
    return 0
