# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from mercurial import pycompat


def switch_user(wrapper, user):
    """Common test helper to change the name of the acting user.

    This helps enforcing that it works uniformly for all permission
    related hooks.
    """
    wrapper.repo.ui.environ[b'REMOTE_USER'] = pycompat.sysbytes(user)
