# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
try:
    from pkg_resources import packaging
    Version = packaging.version.Version  # pragma no cover
except ImportError:  # pragma no cover
    # Seen first on Python >=3.11 but should be about `pkg_resources` version
    from packaging.version import Version

import heptapod


def test_package_version():
    # the Version class accepts only PEP440 compliant version strings
    Version(heptapod.__version__)
