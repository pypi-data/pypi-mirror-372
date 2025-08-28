# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Git test helpers based on the actual Git

This module does not depend on the dulwich library, hence avoiding
a Python dependency and potential tautology problems in the testing
of code that relies on dulwich.

The price to pay for that is to assume the non-Python dependency on Git,
typically solved by installing Git system-wide.
"""
import os
import re
import shutil
import subprocess
import tempfile
from mercurial import pycompat

ZERO_SHA = b'0' * 40
"""Git null commit.

Used notably to represent creation and deletion of Git refs.

It is actually identical to Mercurial's `nullid`, but that could change
at some point.

It is also identical to ``dulwich.protocol.ZERO_SHA``, but we don't want
to depend on dulwich here.
"""


def extract_git_branch_titles(branches):
    return {ref: info['title'] for ref, info in branches.items()}


def git_version():
    out = subprocess.check_output(('git', 'version')).decode().strip()
    m = re.match(r'git version (\d+)\.(\d+)\.(\d+)', out)
    return tuple(int(m.group(i)) for i in range(1, 4))


GIT_VERSION = git_version()


class GitRepo(object):
    """Represent a Git repository, relying on the Git executable.

    The ``git`` command is expected to be available on the ``PATH``.
    """

    def __init__(self, path):
        self.path = path

    @classmethod
    def init(cls, path, bare=True):
        cmd = ['git', 'init']
        if bare:
            cmd.append('--bare')
        cmd.append(str(path))
        subprocess.call(cmd)
        return cls(path)

    @classmethod
    def create_from_bundle_data(cls, target_path, data,
                                tmpdir=None, stream=False):
        """Create a Git repository from a bundle.

        The data is dumped to a temporary file before calling Git.

        :param stream: see ``data``
        :param bundle_data: either :class:`bytes` if ``stream`` is False
          or an iterable of :class: `bytes` if ``stream`` is True
        :param tmpdir: passed over to ``tempfile``.
        """
        with tempfile.NamedTemporaryFile(dir=tmpdir) as bundlef:
            if stream:
                for chunk in data:
                    bundlef.write(chunk)
            else:
                bundlef.write(data)
            bundlef.flush()

            subprocess.check_call(
                ('git', 'clone', '--bare', bundlef.name, str(target_path))
            )
        return cls(target_path)

    def git(self, *args):
        return subprocess.check_output(('git', ) + args, cwd=str(self.path))

    def delete(self):  # pragma no cover (see below)
        # We just removed the unique caller of this method. It was a direct
        # call from a test, not something deeply buried in fixture code or
        # similar (coverage drop would have been suspicious in that case).
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def branch_titles(self):
        return extract_git_branch_titles(self.branches())

    def branches(self):
        out = self.git('branch', '-v', '--no-abbrev')
        split_lines = (l.lstrip(b'*').strip().split(None, 2)
                       for l in out.splitlines())
        return {sp[0]: dict(sha=sp[1], title=sp[2]) for sp in split_lines}

    def tags(self):
        out = self.git('tag')
        return set(l.strip() for l in out.splitlines())

    def commit_hash_title(self, revspec):
        out = self.git('log', '-n1', revspec, r'--pretty=format:%H|%s')
        return out.strip().split(b'|')

    def get_symref(self, name):
        dotgit = self.path.join('.git')
        path = dotgit if dotgit.exists() else self.path
        return path.join(name).read().strip().split(':', 1)[1].strip()

    def set_symref(self, name, target_ref):
        self.path.join(name).write('ref: %s\n' % target_ref)

    def set_branch(self, name, sha):
        sha = pycompat.sysstr(sha)
        self.path.join('refs', 'heads', name).ensure().write(sha + '\n')

    def get_branch_sha(self, name):
        if isinstance(name, bytes):
            name = name.decode()
        return self.path.join('refs', 'heads', name).read().strip()

    def write_ref(self, ref_path, value):
        """Call git to write a ref.

        symbolic refs are taken at face value, hence
        ``write_git_ref(repo, b'HEAD', b'refs/heads/mybranch')`` will move
        ``HEAD`` to ``mybranch``, instead of moving whatever ``HEAD``
        points to.
        """
        self.git('update-ref', b'--no-deref', ref_path, value)

    def all_refs(self):
        """Call git to return all refs.

        :return: a :class:`dict` whose keys are full ref paths and values are
           Git commit SHAs, both as :class:`bytes`.
        """
        lines = self.git('show-ref').splitlines()
        return {split[1]: split[0]
                for split in (line.split(b' ', 1) for line in lines)}

    def raw_refs(self, with_root_refs=False):
        """Use `git for-each-ref` to query all refs, including "root refs"

        The output is the full `stdout` of the Git process, as bytes.
        Each line has 2 or 3 fields:

        - the target object SHA
        - the name of the ref (e.g, `refs/heads/main` or `HEAD`)
        - its target ref *if* it is a root ref (e.g, `HEAD`).

        The root refs are a subset of symrefs. It includes `HEAD` but not
        arbitrary symrefs that can be created with `git symbolic-ref`.

        Git sorts the output on `refname` (e.g., `refs/heads/main` or `HEAD`)
        by default, which is fine to compare two repositories.
        """
        git_args = ['for-each-ref',
                    '--format', '%(objectname)s %(refname) %(symref)']
        if with_root_refs:
            git_args.append('--include-root-refs')  # pragma no cover

        return self.git(*git_args)

    def __eq__(self, other):
        """True iff the two repos have the same content.

        THis is done by comparing all refs, including the remotes
        """
        # not insisting on the same exact class
        if not isinstance(other, GitRepo):
            return False

        opts = dict(with_root_refs=True)
        if GIT_VERSION < (2, 45, 0):  # pragma no cover
            opts['with_root_refs'] = False
            if self.get_symref('HEAD') != other.get_symref('HEAD'):
                return False

        return self.raw_refs(**opts) == other.raw_refs(**opts)
