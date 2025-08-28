# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
from dulwich.tests.test_object_store import (
    DiskObjectStore,
    DiskObjectStoreTests,
)


class AlternatePathsTests(DiskObjectStoreTests):

    def test_read_alternate_paths(self):
        store = DiskObjectStore(self.store_dir)

        abs_path = os.path.abspath(os.path.normpath('/abspath'))
        # ensures in particular existence of the alternates file
        store.add_alternate_path(abs_path)
        self.assertEqual(set(store._read_alternate_paths()), {abs_path})

        store.add_alternate_path("relative-path")
        self.assertIn(os.path.join(store.path, "relative-path"),
                      set(store._read_alternate_paths()))

        # arguably, add_alternate_path() could strip comments.
        # Meanwhile it's more convenient to use it than to import INFODIR
        store.add_alternate_path("# comment")
        for alt_path in store._read_alternate_paths():
            self.assertNotIn("#", alt_path)
