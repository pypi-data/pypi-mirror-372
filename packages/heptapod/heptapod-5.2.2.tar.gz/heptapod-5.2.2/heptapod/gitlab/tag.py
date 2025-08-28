# Copyright 2020 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities and conventions for GitLab tags.
"""
GITLAB_TAG_REF_PREFIX = b'refs/tags/'


def gitlab_tag_ref(gitlab_tag):
    return GITLAB_TAG_REF_PREFIX + gitlab_tag


def gitlab_tag_from_ref(ref):
    """Return GitLab tag name from a ref

    Examples::

      >>> from mercurial.pycompat import sysstr as to_str
      >>> to_str(gitlab_tag_from_ref(b'refs/tags/v1.10.1'))
      'v1.10.1'
      >>> gitlab_tag_from_ref(b'refs/heads/some/branch') is None
      True


    Special case for robustness::

      >>> gitlab_tag_from_ref(None) is None
      True
    """
    if ref is None or not ref.startswith(GITLAB_TAG_REF_PREFIX):
        return None
    return ref[len(GITLAB_TAG_REF_PREFIX):]
