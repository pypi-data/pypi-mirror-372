# Copyright 2019-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from .. import util


def test_format_shas():
    fmt = util.format_shas
    shas = [b'dbad978fb2c3694e0ff8f6ac6889ffafe34ca0b6',
            b'88670e10840db7ccfec5cb0c590970907ac3b382',
            b'393dc94367af44ec57e7cd3a804ddc77e998e564',
            b'55e51a162f6fd259fab1c81395c7ba4d469335c2',
            b'bfd903562a133d228dd91c66954706b1cba35756',
            b'02ad4cac53815a65b890a090ef344268d149a4bb']

    assert fmt(shas[:1]) == b'dbad978fb2c3'
    assert fmt(shas[:2]) == b'dbad978fb2c3 88670e10840d'
    assert fmt(shas) == (
        b'dbad978fb2c3 88670e10840d 393dc94367af 55e51a162f6f and 2 others'
    )
    assert fmt(shas, limit=2) == b'dbad978fb2c3 88670e10840d and 4 others'

    # works with sets as well as lists (see heptapod#441)
    assert fmt(set(shas)).endswith(b'and 2 others')
