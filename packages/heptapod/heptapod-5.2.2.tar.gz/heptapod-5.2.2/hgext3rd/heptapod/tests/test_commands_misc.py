# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import

import json
from hgext.clonebundles import (
    GeneratedBundle,
    read_auto_gen,
)
from mercurial import (
    error,
    scmutil,
)
from mercurial.utils import procutil
import os
import pytest
import re

import botocore

import heptapod.clone_bundles

from mercurial_testhelpers.util import as_bytes
from heptapod.testhelpers import (
    RepoWrapper,
)
from heptapod.testhelpers.gitlab import (
    GitLabMirrorFixture,
    GitLabStateMaintainerFixture,
)
from heptapod.testhelpers.git import GitRepo
from hgext import clonebundles

from .utils import common_config

from .. import (
    versions as hpd_versions,
    branch as hpd_branch,
    special_ref,
    keep_around,
    ASYNC_HEPTAPOD_CLONE_BUNDLE_GENERATE,
)

parametrize = pytest.mark.parametrize


@pytest.fixture
def wrapper(tmpdir):
    repo_path = tmpdir.join('repo')
    yield RepoWrapper.init(repo_path, config=common_config(tmpdir))


def test_hpd_unique_successor(wrapper, monkeypatch):
    ctx = wrapper.write_commit('foo', message="default0",
                               return_ctx=True)
    repo_path = wrapper.path
    repo_path.join('foo').write('amend 1')
    wrapper.command('amend', message=b'amend1')
    repo_path.join('foo').write('amend 2')
    wrapper.command('amend', message=b'amend2')

    records = []

    def write(*args, **opts):
        records.append((args, opts))

    wrapper.repo.ui.write = write
    wrapper.command('hpd-unique-successor', rev=ctx.hex())
    out = records[0][0][0]

    succ_ctx = scmutil.revsingle(wrapper.repo, out)
    assert succ_ctx.description() == b'amend2'


def test_hpd_unique_successor_divergence(tmpdir, monkeypatch):
    repo_path = tmpdir.join('repo')
    config = common_config(tmpdir)
    config.setdefault('experimental', {})['evolution.allowdivergence'] = 'yes'
    wrapper = RepoWrapper.init(repo_path, config=config)
    ctx = wrapper.write_commit('foo', message="default0",
                               return_ctx=True)
    repo_path.join('foo').write('amend 1')
    wrapper.command('amend', message=b'amend1')

    # let's create the divergence
    wrapper.update(ctx.hex(), hidden=True)
    repo_path.join('foo').write('amend 2')
    wrapper.command('amend', message=b'amend2')

    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('hpd-unique-successor', rev=ctx.hex())
    # from Mercurial 7.1 onwards, the message *is* bytes, we use `as_bytes`
    # to keep compat with earlier versions
    assert b'divergent' in as_bytes(exc_info.value.args[0])


def test_hpd_ensure_gitlab_branches(wrapper):
    # test almost trivial because all the logic is in HeptapodGitHandler
    wrapper.command('hpd-ensure-gitlab-branches')
    assert hpd_branch.read_gitlab_branches(wrapper.repo) == {}


def test_hpd_ensure_gitlab_default_branch(wrapper):
    # initially we don't have any default_gitlab_branch file
    assert not hpd_branch.get_default_gitlab_branch(wrapper.repo)
    # run command to create the file
    wrapper.command('hpd-ensure-gitlab-default-branch')
    assert hpd_branch.get_default_gitlab_branch(wrapper.repo) == b'master'
    # if already exists, running again shouldn't make any difference
    wrapper.command('hpd-ensure-gitlab-default-branch')
    assert hpd_branch.get_default_gitlab_branch(wrapper.repo) == b'master'


def test_hpd_ensure_gitlab_tags(wrapper):
    # test almost trivial because all the logic is in HeptapodGitHandler
    wrapper.command('hpd-ensure-gitlab-tags')
    assert hpd_branch.read_gitlab_tags(wrapper.repo) == {}


def test_hpd_ensure_gitlab_special_refs(wrapper):
    # test almost trivial because all the logic is in HeptapodGitHandler
    wrapper.command('hpd-ensure-gitlab-special-refs')
    assert special_ref.special_refs(wrapper.repo) == {}


def test_hpd_ensure_gitlab_keep_arounds(wrapper):
    # test almost trivial because all the logic is in HeptapodGitHandler
    wrapper.command('hpd-ensure-gitlab-keep-arounds')
    assert list(keep_around.iter_keep_arounds(wrapper.repo)) == []


def test_hpd_ensure_all_gitlab_specific_state_files(wrapper):
    # test almost trivial because all the logic is in HeptapodGitHandler
    wrapper.command('hpd-ensure-all-gitlab-specific-state-files')
    assert special_ref.special_refs(wrapper.repo) == {}
    assert hpd_branch.read_gitlab_tags(wrapper.repo) == {}
    assert hpd_branch.read_gitlab_tags(wrapper.repo) == {}
    assert list(keep_around.iter_keep_arounds(wrapper.repo)) == []
    assert hpd_branch.get_default_gitlab_branch(wrapper.repo) == b'master'


def test_hpd_unique_successor_missing_rev(wrapper, monkeypatch):
    with pytest.raises(error.Abort) as exc_info:
        wrapper.command('hpd-unique-successor')
    assert b'specify a revision' in exc_info.value.args[0]


def test_hpd_versions_with_hg_git(tmpdir, monkeypatch):
    # using RepoWrapper is pure lazyness on our part: they  give us the easiest
    # access to fully set up `ui` objects, with activated extensions
    config = common_config(tmpdir)
    config['extensions']['hggit'] = ''
    ui = RepoWrapper.init(tmpdir, config=config).repo.ui
    records = []

    def write(*args, **opts):
        assert all(isinstance(a, bytes) for a in args)
        records.append((args, opts))

    monkeypatch.setattr(ui, 'write', write)
    hpd_versions(ui)
    out = json.loads(records[0][0][0].decode())
    assert set(out.keys()) == {'python', 'mercurial',
                               'topic', 'hggit', 'evolve'}
    # for hggit it looks like: x.y.z (dulwich a.b.c)
    # for Mercurial, it can be just x.y
    version_re = re.compile(r'\d+[.]\d+([.]\d+)?')
    assert all(v is None or version_re.match(v) is not None
               for v in out.values())
    out.pop('hggit', None)  # hggit won't be shipped in some future
    assert all(v is not None for v in out.values())


@pytest.fixture()
def git_mirror_fixture(tmpdir, monkeypatch):
    with GitLabMirrorFixture.init(tmpdir, monkeypatch,
                                  hg_config=common_config(tmpdir)) as fixture:
        yield fixture


def test_git_resync_existing_git_repo(git_mirror_fixture):
    fixture = git_mirror_fixture
    wrapper = fixture.hg_repo_wrapper

    base_ctx = wrapper.commit_file('foo', message='Commit 0')

    # Adding various repo content
    wrapper.command('tag', b'v1.2.3', rev=base_ctx.hex())
    wrapper.commit_file('foo', message='Commit 1')
    # special refs and keep-arounds are added later in this test
    wrapper.command('gitlab-mirror')
    git_repo = fixture.git_repo

    wrapper.set_config('heptapod', 'native', 'yes')

    def assert_initial_git_state():
        assert git_repo.branch_titles() == {b'branch/default': b'Commit 1'}
        assert git_repo.tags() == {b'v1.2.3'}
        # checking ref targets, we don't care about the hashes
        base_git_sha, base_git_title = git_repo.commit_hash_title('v1.2.3')
        assert base_git_title == b'Commit 0'
        return base_git_sha

    # first call does not break anything, and moves Git repo to the dedicated
    # location
    wrapper.command('hpd-git-resync')
    fixture.reload_git_repo()
    assert fixture.git_repo.path != git_repo.path
    git_repo = fixture.git_repo
    assert_initial_git_state()

    # now adding a new commit to check basic incrementality
    # (adding another branch just to spice it a bit)
    wrapper.commit_file('foo', message='Commit 2')
    wrapper.commit_file('bar', parent=base_ctx, branch='other',
                        message='Commit 3')
    wrapper.command('gitlab-mirror')

    # Mirroring to Git did not happen (validity of test hypothesis)
    assert git_repo.branch_titles() == {b'branch/default': b'Commit 1'}

    wrapper.command('hpd-git-resync')
    assert git_repo.branch_titles() == {b'branch/default': b'Commit 2',
                                        b'branch/other': b'Commit 3'}
    assert git_repo.tags() == {b'v1.2.3'}


@pytest.fixture()
def native_fixture(tmpdir, monkeypatch):
    with GitLabStateMaintainerFixture.init(
            tmpdir, monkeypatch,
            hg_config=common_config(tmpdir)) as fixture:
        fixture.hg_repo_wrapper.set_config('heptapod.native', True)
        yield fixture


def test_git_resync_creates_git_repo(native_fixture):
    fixture = native_fixture
    wrapper = fixture.hg_repo_wrapper

    base_ctx = wrapper.commit_file('foo', message='Commit 0')

    # Adding various repo content
    wrapper.command('tag', b'v1.2.3', rev=base_ctx.hex())
    wrapper.commit_file('foo', message='Commit 1')
    # TODO special ref
    # TODO keep around
    wrapper.command('gitlab-mirror')
    wrapper.command('hpd-export-native-to-git')
    git_repo = GitRepo(
        fixture.base_path / '+hgitaly/hg-git'
        / wrapper.path.basename.replace('.hg', '.git')
    )
    assert git_repo.branch_titles() == {b'branch/default': b'Commit 1'}
    assert git_repo.tags() == {b'v1.2.3'}
    # checking ref targets, we don't care about the hashes
    base_git_sha, base_git_title = git_repo.commit_hash_title('v1.2.3')
    assert base_git_title == b'Commit 0'
    return base_git_sha


def test_move_out_of_gitaly_reach(git_mirror_fixture):
    fixture = git_mirror_fixture
    wrapper = fixture.hg_repo_wrapper
    orig_path = fixture.git_repo.path

    with pytest.raises(error.Abort):
        wrapper.command('move-hg-git-repo-out-of-gitaly-reach')

    wrapper.set_config('heptapod', 'native', True)
    wrapper.command('move-hg-git-repo-out-of-gitaly-reach')

    fixture.reload_git_repo()
    git_repo = fixture.git_repo
    assert git_repo.path != orig_path
    assert not os.path.exists(orig_path)
    assert os.path.exists(git_repo.path)
    # would not work if it were not a Git repo
    assert git_repo.branches() == {}


class FakeS3Client:

    fail_rm = False

    def __init__(self):
        self.rm_records = []
        self.upload_records = []
        self.presigned_records = []

    def upload_file(self, *a, **kw):
        self.upload_records.append((a, kw))

    def delete_object(self, *a, **kw):
        if not self.fail_rm:
            self.rm_records.append((a, kw))
        else:
            raise botocore.exceptions.ClientError(
                {'Error': {'Code': 403, 'Message': "I beg to differ"}},
                'delete_object'
            )

    def generate_presigned_url(self, *a, **kw):
        self.presigned_records.append((a, kw))
        return 'https://presigned.test'


class CloneBundlesFixture():
    def __init__(self, parent, monkeypatch):
        self.native_fixture = parent
        wrapper = self.hg_repo_wrapper = parent.hg_repo_wrapper

        self.bucket = 'seau'
        self.priv_bucket = 'coffre'
        self.bucket_subdir = 'group/subgrp/project-123'
        self.pub_base_url = 'https://pub.hgcb.test'

        self.set_conf('trigger.below-bundled-ratio', 1.0)
        self.set_conf('auto-generate.formats', 'zstd-v2')
        self.set_conf('clone-bundles.public-base-url', self.pub_base_url,
                      section='heptapod')
        self.set_conf('clone-bundles.s3.endpoint', 's3.test',
                      section='heptapod')
        self.set_conf('clone-bundles.s3.public-bucket', self.bucket,
                      section='heptapod')
        self.set_conf('clone-bundles.s3.private-bucket', self.priv_bucket,
                      section='heptapod')

        wrapper.repo.ui.environ.update((
            (b'GL_REPOSITORY', b'project-123'),
            (b'HEPTAPOD_HGRC', b'/some/heptapod.hgrc'),
        ))

        self.fake_s3_client = FakeS3Client()

        orig = heptapod.clone_bundles.s3_client_bucket

        def s3_client_bucket(repo, public=False):
            # still calling original instantiation for coverage
            # and inspection
            self.orig_s3_client, bucket = orig(repo, public=public)
            return self.fake_s3_client, bucket

        monkeypatch.setattr(heptapod.clone_bundles,
                            's3_client_bucket',
                            s3_client_bucket)

    def set_conf(self, k, v, section='clone-bundles'):
        self.hg_repo_wrapper.repo.ui.setconfig(
            section.encode(), k.encode(), str(v).encode())


@pytest.fixture
def clone_bundles_fixture(native_fixture, monkeypatch):
    yield CloneBundlesFixture(native_fixture, monkeypatch)


# with 'disabled', the point is to run everything configured
# as for 'command' and check that is really does nothing
@parametrize('trigger', ('command', 'on-change', 'disabled'))
@parametrize('access', ('public-bucket', 'public-with-acl', 'private'))
def test_clone_bundles_refresh(clone_bundles_fixture, monkeypatch,
                               trigger, access):
    fixture = clone_bundles_fixture
    wrapper = fixture.hg_repo_wrapper
    on_change = trigger == 'on-change'
    with_acl = access == 'public-with-acl'
    public = access != 'private'

    if on_change:
        fixture.set_conf('auto-generate.on-change', True)
        environ = wrapper.repo.ui.environ
        environ.update((
            (b'HEPTAPOD_PROJECT_NAMESPACE_FULL_PATH', b'group/subgrp'),
        ))
        if public:
            environ[b'HEPTAPOD_PUBLIC_REPOSITORY'] = b'true'

        bg_commands = []
        monkeypatch.setattr(procutil, 'runbgcommand',
                            lambda *a, **kw: bg_commands.append((a, kw)))

    upload_records = fixture.fake_s3_client.upload_records

    if trigger == 'disabled':
        wrapper.repo.ui.setconfig(b'heptapod', b'clone-bundles', b'disabled')

    wrapper.repo.ui.setconfig(
        b'heptapod', b'clone-bundles.s3.public.with-acl', with_acl)

    base_ctx = wrapper.commit_file('foo', message='Commit 0')

    # Adding various repo content
    wrapper.command('tag', b'v1.2.3', rev=base_ctx.hex())
    wrapper.commit_file('foo', message='Commit 1')

    if on_change:
        assert len(bg_commands) == 3  # indeed, we had 3 transactions
        (cmd, env), _ = bg_commands[-1]
        assert env[b'GL_REPOSITORY'] == b'project-123'
        assert env[b'HGRCPATH'] == b'/some/heptapod.hgrc'
        assert env.get(b'HEPTAPOD_HG_BUNDLE_SPEC')
        # let us launch it synchronously instead and benefit
        # from our S3 monkey patch
        wrapper.repo.ui.environ.update(env)
        wrapper.command(ASYNC_HEPTAPOD_CLONE_BUNDLE_GENERATE)
    else:
        wrapper.command('hpd-clone-bundles-refresh',
                        project_namespace_full_path=b'group/subgrp',
                        public=public,
                        )
        if trigger == 'disabled':
            assert not upload_records
            return

    upload_args = upload_records[0][0]
    assert upload_args[1] == fixture.bucket if public else fixture.priv_bucket
    basename = upload_args[0].rsplit('/', 1)[1]
    assert upload_args[2] == '/'.join((fixture.bucket_subdir, basename))
    upload_extra = upload_records[0][1]['ExtraArgs']
    if with_acl:
        assert upload_extra == {'ACL': 'public-read'}

    bundles = read_auto_gen(wrapper.repo)
    assert len(bundles) == 1
    bundle = bundles[0]
    assert isinstance(bundle, GeneratedBundle)
    assert bundle.ready
    assert bundle.basename == basename.encode()
    assert bundle.revs == 3
    base_url = fixture.pub_base_url if public else 'bucket:'
    assert bundle.file_url.decode() == '/'.join(
        (base_url, fixture.bucket_subdir, basename)
    )

    from mercurial.bundlecaches import alter_bundle_url
    final_url = alter_bundle_url(wrapper.repo, bundle.file_url)
    sig_records = fixture.fake_s3_client.presigned_records
    if public:
        assert final_url == bundle.file_url
        assert not sig_records
    else:
        assert final_url == b'https://presigned.test'
        assert len(sig_records) == 1
        record = sig_records[0]
        assert record[0] == ('get_object', )
        assert record[1] == {
            'Params': {'Bucket': fixture.priv_bucket,
                       'Key': 'group/subgrp/project-123/' + basename},
            'ExpiresIn': 7200,
        }


@parametrize('result', ('success', 's3_failure'))
def test_delete_clone_bundle(clone_bundles_fixture, monkeypatch, result):
    fixture = clone_bundles_fixture
    wrapper = fixture.hg_repo_wrapper
    rm_records = fixture.fake_s3_client.rm_records

    wrapper.commit_file('foo', message='Commit 0')
    wrapper.command('hpd-clone-bundles-refresh',
                    project_namespace_full_path=b'group/subgrp',
                    public=True,
                    )

    bundles = read_auto_gen(wrapper.repo)
    assert len(bundles) == 1
    bundle = bundles[0]
    assert isinstance(bundle, GeneratedBundle)

    def find_outdated_bundles(repo, bundles):
        return [bundle]

    if result == 's3_failure':
        fixture.fake_s3_client.fail_rm = True

    monkeypatch.setattr(clonebundles, 'find_outdated_bundles',
                        find_outdated_bundles)

    clonebundles.collect_garbage(wrapper.repo)

    if result == 'success':
        assert len(rm_records) == 1
        rm_args = rm_records[0][1]
        basename = bundle.basename.decode('ascii')
        assert rm_args == {
            'Bucket': fixture.bucket,
            'Key': '/'.join((fixture.bucket_subdir, basename)),
        }
    else:
        # no crash and nothing else done
        assert len(rm_records) == 0
