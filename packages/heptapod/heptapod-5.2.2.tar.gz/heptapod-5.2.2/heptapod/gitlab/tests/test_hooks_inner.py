# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for hooks that don't need neither a repo, nor to fake requests.
"""
import pytest

from ..hooks import (
    format_alert_message,
    format_warnings,
    format_mr_links,
    git_hook_format_changes,
    parse_broadcast_msg,
    parse_actor,
    InvalidActor,
)


ZERO_SHA = b"0" * 20


def test_parse_actor():
    assert parse_actor("key-1") == ('key_id', '1')
    assert parse_actor("key-17") == ('key_id', '17')
    assert parse_actor("user-3") == ('user_id', '3')
    assert parse_actor("user-35") == ('user_id', '35')
    assert parse_actor("username-testgr") == ('username', 'testgr')
    with pytest.raises(InvalidActor) as exc_info:
        parse_actor('key-1x')
    assert exc_info.value.args[0] == 'key-1x'
    with pytest.raises(InvalidActor) as exc_info:
        parse_actor('user-1a')
    assert exc_info.value.args[0] == 'user-1a'
    with pytest.raises(InvalidActor) as exc_info:
        parse_actor('imaginary-12')
    assert exc_info.value.args[0] == 'imaginary-12'


def test_git_hook_format_changes():
    changes = {b'branch/newbr': (ZERO_SHA, b"beef1234dead" + b"a" * 8),
               b'topic/default/zz': (b"23cafe45" + b"0" * 12,
                                     b"1234" + b"b" * 16),
               }
    assert set(git_hook_format_changes(changes).splitlines()) == {
        b'00000000000000000000 beef1234deadaaaaaaaa branch/newbr',
        b'23cafe45000000000000 1234bbbbbbbbbbbbbbbb topic/default/zz'
    }


def test_parse_broadcast_msg():
    msg = "Short message"
    assert parse_broadcast_msg(msg, 80) == [msg]

    msg = "A somewhat longer message, cut here"
    assert parse_broadcast_msg(msg, 30) == ["A somewhat longer message,",
                                            "cut here"]


def test_format_alert_message():
    # here the point of the test is mostly to make sure that we don't
    # get stupid errors, we don't care that much of the exact amount of
    # padding or leading and trailing separators
    msg = "Short message"
    assert (format_alert_message(msg)[3]
            == b'                             Short message'
            )
    msg = ' '.join('word%d' % i for i in range(20))
    formatted = format_alert_message(msg)
    assert (formatted[3]
            == (b'   word0 word1 word2 word3 word4 word5 word6 word7 word8 '
                b'word9 word10')
            )
    assert (formatted[4]
            == (b'     word11 word12 word13 word14 word15 '
                b'word16 word17 word18 word19')
            )


def test_format_warnings():
    """Test format_warnings for non breakage, not for precise content wording.
    """
    assert b'WARNINGS' in format_warnings('Short warning')[3]


def fmt_mr_links(mrs):
    """Call and convert return into a tuple.

    The goal is that assertions don't depend onto the precise return type.
    """
    return tuple(format_mr_links(mrs))


def test_format_mr_links():
    """Test format_mr_links for non breakage, not for precise content wording.
    """
    assert fmt_mr_links(None) == ()
    assert fmt_mr_links([]) == ()
    assert fmt_mr_links(()) == ()

    seen_create = False
    seen_view = False

    for line in fmt_mr_links(
            [dict(new_merge_request=True,
                  branch_name='heptapod-next',
                  url="https://heptapod.example?query=something"),
             dict(new_merge_request=False,
                  branch_name='heptapod-stable',
                  url="https://heptapod.example?query=other"),
             ]):
        line = line.lower()
        if b'view merge request' in line:
            seen_view = True
            assert b"heptapod-stable" in line
            # query string passed through
            assert b'?query=other' in line
        elif b'create a merge request' in line:
            seen_create = True
            assert b"heptapod-next" in line
            assert b'?query=something' in line
    assert seen_view, "Did not get message to view existing MR"
    assert seen_create, "Did not get message to create new MR"
