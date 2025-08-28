# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os

import dulwich
from dulwich.object_store import (
    DiskObjectStore,
    INFODIR,
    GitFile,
)


# backport from dulwich commits:
# 06b65c3c2aef57939143e33d404f9883ec286597
# 544e90f8cbce1282ecb3d8ff73b5d7ecae905601
#
# see also https://github.com/dulwich/dulwich/pull/815 and heptapod#370
def _read_alternate_paths(self):  # pragma: no cover
    try:
        f = GitFile(os.path.join(self.path, INFODIR, "alternates"), 'rb')
    except FileNotFoundError:
        return
    with f:
        for line in f.readlines():
            line = line.rstrip(b"\n")
            if line.startswith(b"#"):
                continue
            if os.path.isabs(line):
                yield os.fsdecode(line)
            else:
                yield os.fsdecode(os.path.join(os.fsencode(self.path),
                                               line))


if dulwich.__version__ < (0, 20, 14):  # pragma no cover
    # our tests will run immediately on the dulwich with the fix,
    # only coverage telling us it's time to remove the unneeded patch
    DiskObjectStore._read_alternate_paths = _read_alternate_paths
