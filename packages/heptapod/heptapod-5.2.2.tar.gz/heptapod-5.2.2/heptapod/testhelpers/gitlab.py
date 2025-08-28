# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Test support for users of heptapod.gitlab
"""
from __future__ import absolute_import
import attr
from copy import deepcopy
import logging
import shutil

from mercurial_testhelpers.repo_wrapper import (
    as_bytes,
)
from heptapod.gitlab import hooks
from hgext3rd.heptapod.branch import (
    get_default_gitlab_branch,
)

from .hg import RepoWrapper
from .git import GitRepo
logger = logging.getLogger(__name__)

STATE_MAINTAINER_ACTIVATION_CONFIG = (
    b'hooks', b'pretxnclose.testcase',
    b'python:heptapod.hooks.gitlab_mirror.mirror',
)


def patch_gitlab_hooks(monkeypatch, records, action=None):

    def call(self, changes):
        records.append((self.name, changes))
        if action is not None:
            return action(self.name, changes)
        else:
            return 0, ("hook %r ok" % self.name).encode(), 'no error'

    def init(self, repo, encoding='utf-8'):
        self.repo = repo
        self.encoding = encoding

    monkeypatch.setattr(hooks.Hook, '__init__', init)
    monkeypatch.setattr(hooks.PreReceive, '__call__', call)
    monkeypatch.setattr(hooks.PostReceive, '__call__', call)


def activate_gitlab_state_maintainer(hg_repo_wrapper):
    """Make state maintaining or mirroring to Git repo automatic.

    This is essential to get the state maintaining happen in-transaction.
    If the repository is configured with `native=False` (legacy hg-git based
    projects), this triggers the mirroring to Git.
    """
    hg_repo_wrapper.repo.ui.setconfig(*STATE_MAINTAINER_ACTIVATION_CONFIG)


def activate_gitlab_state_maintainer_in_dict(config):  # pragma no cover
    """Activation in config dicts used before persisting configuration.

    This is used in HGitaly tests, as py-heptapod tests tend to do it
    after repo creation, in non-persistent form.
    """
    section, key, value = STATE_MAINTAINER_ACTIVATION_CONFIG
    config[section] = {key: value}


@attr.s
class GitLabStateMaintainerFixture:
    """Helper class to create fixtures for GitLab state maintainers.

    The pytest fixture functions themselves will have to be provided with
    the tests that use them.

    It is not the role of this class to make decisions about scopes or
    the kind of root directory it operates in.

    This provides

    - Mercurial repository test wrapper
    - GitLab notifications interception

    and is thus usable directly for native repositories.
    """
    base_path = attr.ib()
    hg_repo_wrapper = attr.ib()
    gitlab_notifs = attr.ib()

    @classmethod
    def init(cls, base_path, monkeypatch, hg_config=None,
             common_repo_name='repo',
             additional_extensions=(),
             **kw):
        if hg_config is None:
            config = {}
        else:
            config = deepcopy(hg_config)

        config.setdefault('extensions', {}).update(
            (ext, '') for ext in additional_extensions)
        config['phases'] = dict(publish=False)

        hg_repo_wrapper = RepoWrapper.init(
            base_path / (common_repo_name + '.hg'),
            config=config)
        notifs = []
        patch_gitlab_hooks(monkeypatch, notifs)
        return cls(hg_repo_wrapper=hg_repo_wrapper,
                   gitlab_notifs=notifs,
                   base_path=base_path,
                   **kw)

    def clear_gitlab_notifs(self):
        """Forget about all notifications already sent to GitLab.

        Subsequent notifications will keep on being recorded in
        ``self.gitlab_notifs``.
        """
        del self.gitlab_notifs[:]

    def activate_mirror(self):
        activate_gitlab_state_maintainer(self.hg_repo_wrapper)

    def delete(self):
        hg_path = self.hg_repo_wrapper.repo.root
        try:
            shutil.rmtree(hg_path)
        except Exception:
            logger.exception("Error removing the Mercurial repo at %r",
                             hg_path)

    def __enter__(self):
        return self

    def __exit__(self, *exc_args):
        self.delete()
        return False  # no exception handling related to exc_args

    def assert_default_gitlab_branch(self, expected):
        gl_branch = get_default_gitlab_branch(self.hg_repo_wrapper.repo)
        assert gl_branch == as_bytes(expected)


@attr.s
class GitLabMirrorFixture(GitLabStateMaintainerFixture):
    """Helper class to create fixtures for GitLab aware hg-git mirroring.

    Adds the Git repository to GitLabStateMaintainerFixture
    """
    git_repo = attr.ib()
    import heptapod.testhelpers.gitlab

    @classmethod
    def init(cls, base_path, monkeypatch,
             common_repo_name='repo', **kw):
        git_repo = GitRepo.init(
            base_path / (common_repo_name + '.git')
        )
        return super(GitLabMirrorFixture, cls).init(
            base_path, monkeypatch,
            common_repo_name=common_repo_name,
            additional_extensions=['hggit'],
            git_repo=git_repo,
            **kw)

    def reload_git_repo(self):
        """Useful in particular after setting native=true"""
        if self.hg_repo_wrapper.repo.ui.configbool(b'heptapod', b'native'):
            parent_path = self.base_path / '+hgitaly/hg-git'
        else:
            parent_path = self.base_path
        self.git_repo = GitRepo(parent_path / self.git_repo.path.basename)

    def delete(self):
        git_path = self.git_repo.path
        try:
            shutil.rmtree(git_path)
        except Exception:
            logger.exception("Error removing the Git repo at %r", git_path)

        super(GitLabMirrorFixture, self).delete()

    def assert_default_gitlab_branch(self, expected):
        assert self.git_repo.get_symref('HEAD') == 'refs/heads/' + expected
        super(GitLabMirrorFixture, self).assert_default_gitlab_branch(expected)
