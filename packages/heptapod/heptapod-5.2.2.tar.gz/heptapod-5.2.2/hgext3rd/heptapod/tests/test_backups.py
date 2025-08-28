# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest
import tarfile
from io import BytesIO

from mercurial import (
    error,
    scmutil,
)
from heptapod.testhelpers import (
    RepoWrapper,
    as_bytes,
)
from .utils import common_config

from .. import (
    backup_additional,
    restore_additional,
)
from ..branch import (
    gitlab_branches,
    get_default_gitlab_branch,
)
from ..git import HeptapodGitHandler
from ..keep_around import (
    create_keep_around,
    iter_keep_arounds,
)
from ..special_ref import (
    special_refs,
    write_gitlab_special_ref,
)
from ..tag import gitlab_tags

from heptapod.testhelpers.gitlab import GitLabMirrorFixture


def test_additional_backup_restore(tmpdir, monkeypatch):
    hg_common_config = common_config(tmpdir)
    fixture = GitLabMirrorFixture.init(tmpdir, monkeypatch,
                                       hg_config=hg_common_config)
    src_wrapper = fixture.hg_repo_wrapper
    src_repo = src_wrapper.repo
    main_hgrc = b'[foo]\nsome=bar\n'
    managed_hgrc = b'[heptapod]\nallow-bookmars=true\n'
    src_repo.vfs.write(b'hgrc', main_hgrc)
    src_repo.vfs.write(b'hgrc.managed', managed_hgrc)

    # Backup/restore for the empty repo to check that config
    # is still ok (even though default branch file is missing)
    tar_for_empty_path = tmpdir / 'additional_empty_repo.tar'
    src_wrapper.command('hpd-backup-additional', as_bytes(tar_for_empty_path))

    empty_dst_wrapper = RepoWrapper.init(tmpdir / 'empty_restored',
                                         config=hg_common_config)
    empty_dst_wrapper.command('hpd-restore-additional',
                              as_bytes(tar_for_empty_path))
    empty_dst_repo = empty_dst_wrapper.repo
    assert empty_dst_repo.vfs(b'hgrc').read() == main_hgrc
    assert empty_dst_repo.vfs(b'hgrc.managed').read() == managed_hgrc

    # Now with repo content and GitLab refs
    sha = src_wrapper.write_commit('foo', branch='surprise').hex()
    src_wrapper.command('tag', b'v3.2.1')
    tagging_sha = scmutil.revsingle(src_wrapper.repo, b'.').hex()

    src_wrapper.command('gitlab-mirror')
    write_gitlab_special_ref(src_wrapper.repo, b'merge_requests/5/head', sha)
    create_keep_around(src_repo, sha)

    tar_path = as_bytes(tmpdir / 'additional.tar')
    backup_additional(src_repo.ui, src_repo, tar_path)

    dst_wrapper = RepoWrapper.init(tmpdir / 'restored',
                                   config=hg_common_config)

    dst_repo = dst_wrapper.repo
    dst_wrapper.command('pull', src_repo.root, remote_hidden=False)

    restore_additional(dst_repo.ui, dst_repo, tar_path)

    # Default GitLab branch (cannot pass by accident thanks to branch name)
    # Assertions for all kinds of GitLab refs
    assert get_default_gitlab_branch(src_repo) == b'branch/surprise'
    assert special_refs(dst_repo) == {b'merge_requests/5/head': sha}
    assert list(iter_keep_arounds(dst_repo)) == [sha]
    assert gitlab_branches(dst_repo) == {b'branch/surprise': tagging_sha}
    assert gitlab_tags(dst_repo) == {b'v3.2.1': sha}

    # Assertions for hg-git mapping
    src_handler = HeptapodGitHandler(src_repo, src_repo.ui)
    dst_handler = HeptapodGitHandler(dst_repo, dst_repo.ui)
    dst_git_sha = dst_handler.map_git_get(sha)
    assert dst_git_sha  # avoid traps
    assert dst_git_sha == src_handler.map_git_get(sha)


def test_restore_bad_tar(tmpdir):
    dst_wrapper = RepoWrapper.init(tmpdir / 'repo',
                                   config=common_config(tmpdir))
    tar_path = tmpdir / 'bad.tar'

    # str() because we support Python 3.7 (for CI)
    # and path-like objects are accepted in tarfile from Python 3.8 onwards
    with tarfile.open(str(tar_path), 'w') as tarf:
        tinfo = tarfile.TarInfo(name='/etc/shadow')
        tarf.addfile(tinfo, BytesIO(b'evil input'))

    with pytest.raises(error.Abort) as exc_info:
        dst_wrapper.command('hpd-restore-additional', as_bytes(tar_path))

    assert b"Prohibited member" in exc_info.value.message
