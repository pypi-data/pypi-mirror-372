# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
from os.path import (
    dirname,
    join,
)
import heptapod
from heptapod.testhelpers import as_bytes
import hgext3rd.heptapod
HGEXT_HEPTA_SOURCE = dirname(hgext3rd.heptapod.__file__)

HEPTAPOD_REQUIRED_HGRC = join(os.fsencode(dirname(heptapod.__file__)),
                              b'required.hgrc')


def common_config(repos_root):
    """Return a configuration dict, prefilled with what we almost always need.

    Notably, it activates the present extension.
    """
    return dict(extensions=dict(heptapod=HGEXT_HEPTA_SOURCE,
                                topic='',
                                evolve='',
                                rebase='',
                                clonebundles='',
                                ),
                heptapod={b'repositories-root': as_bytes(repos_root)})
