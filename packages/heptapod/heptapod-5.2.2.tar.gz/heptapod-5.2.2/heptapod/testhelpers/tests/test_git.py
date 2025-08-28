# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import subprocess
from ..git import GitRepo
import pytest

parametrize = pytest.mark.parametrize


def test_refs(tmpdir):
    server = tmpdir / 'server.git'
    # server_repo is bare, hence we cannot commit directly in there
    server_repo = GitRepo.init(server)

    client = tmpdir / 'client'
    client_repo = GitRepo.init(client, bare=False)
    client_repo.git('remote', 'add', 'origin', str(server))
    client_repo.git('config', 'user.name', 'John Doe')
    client_repo.git('config', 'user.email', 'jdoe@heptapod.example')

    (client / 'foo').write('foo')
    client_repo.git('add', 'foo')
    client_repo.git('commit', '-m', 'init commit', '--no-gpg-sign')
    client_repo.git('push', 'origin', 'master')

    assert server_repo.branch_titles() == {b'master': b'init commit'}

    # correct commit SHA is read from server repo
    sha = server_repo.get_branch_sha('master')
    client_log = subprocess.check_output(['git', 'log', '--oneline', sha],
                                         cwd=str(client))
    assert client_log.split(b' ', 1)[-1].strip() == b'init commit'

    # Testing more commit and branch methods
    assert server_repo.commit_hash_title('master') == [sha.encode(),
                                                       b'init commit']
    assert server_repo.get_branch_sha(b'master') == sha

    client_repo = GitRepo(client)
    assert server_repo != client  # wrong class
    assert server_repo != client_repo  # the client has remote refs
    client_repo.git('update-ref', '-d', 'refs/remotes/origin/master')
    assert server_repo == client_repo

    # (for Git < 2.45 coverage): same HEAD but an additional branch
    (client / 'foo').write('bar')
    client_repo.git('checkout', '-b', 'other')
    client_repo.git('add', 'foo')
    client_repo.git('commit', '-m', 'other branch', '--no-gpg-sign')
    assert server_repo != client_repo


@parametrize('stream', ('stream', 'bytes'))
def test_create_from_bundle_data(stream, tmpdir):
    src_path = tmpdir / 'src'
    src = GitRepo.init(src_path, bare=False)
    (src_path / 'foo').write('foo')
    src.git('checkout', '-b', 'main')
    src.git('add', 'foo')
    src.git('config', 'user.name', 'John Doe')
    src.git('config', 'user.email', 'jdoe@heptapod.example')
    src.git('commit', '-m', "commit to bundle", '--no-gpg-sign')

    bundle_data = src.git('bundle', 'create', '-q', '-', '--all')
    stream = stream == 'stream'
    if stream:
        bundle_data = [bundle_data[:10], bundle_data[10:]]

    target_repo = GitRepo.create_from_bundle_data(
        target_path=tmpdir / 'target',
        data=bundle_data,
        stream=stream
    )
    assert target_repo.branch_titles() == {b'main': b"commit to bundle"}
