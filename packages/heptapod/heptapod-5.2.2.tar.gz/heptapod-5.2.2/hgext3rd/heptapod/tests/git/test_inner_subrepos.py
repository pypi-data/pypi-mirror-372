# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from collections import OrderedDict

from hgext3rd.heptapod import hggit_parse_hgsub


def parse_hgsub(lines):
    return hggit_parse_hgsub(None, lines)


def test_parse_hgsub():
    assert parse_hgsub([b""]) == OrderedDict()
    parsed = parse_hgsub((b"foo2=bar2\n", b"foo=bar"))
    assert isinstance(parsed, OrderedDict)
    assert parsed == OrderedDict(((b"foo2", b"bar2"),
                                  (b"foo", b"bar")))

    # [subpaths] section is simply ignored, in particular we don't
    # barf on it (see heptapod#310)
    assert parse_hgsub((b"foo=bar\n",
                        b"[subpaths]\n",
                        b"foo2=bar\n")) == OrderedDict([(b"foo", b"bar")])
