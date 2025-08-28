# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from base64 import b64encode
import datetime
import json
import logging
from mercurial import (
    error,
    hg,
    pycompat,
)
import os
import re
import requests
from requests.exceptions import RequestException
import requests_unixsocket

import jwcrypto.jwk as jwk
import python_jwt as jwt


logger = logging.getLogger(__name__)

ACTOR_RX_SYMBS = (
    (re.compile(r'key-(\d+)$'), 'key_id'),
    (re.compile(r'user-(\d+)$'), 'user_id'),
    (re.compile(r'username-(.*)$'), 'username'),
)

ALLOWED_API_KNOWN_STATUS_CODES = (
    requests.codes.ok,
    requests.codes.multiple_choices,
    requests.codes.unauthorized,
    requests.codes.not_found,
    requests.codes.service_unavailable,
)


class InvalidActor(ValueError):
    pass


class GitLabHookError(error.Abort):
    """Specialized class for catching by HGitaly

    Subclassing :class:`error.Abort` so that it is understood as an abort
    while receiving client pushes, and still catchable for proper
    error treatment without crashing by long-running processes such as HGitaly.

    These are raised by the caller of hook classes such as :class:`PreReceive`
    after it has done its onw layer of error treatment.
    """


class GitLabPreReceiveError(GitLabHookError):
    """Indicates an error in authorization."""


class GitLabPostReceiveError(GitLabHookError):
    """Indicates an error in post-receive."""


def parse_actor(actor):
    for regexp, symbol in ACTOR_RX_SYMBS:
        m = regexp.match(actor)
        if m is not None:
            return (symbol, m.group(1))
    raise InvalidActor(actor)


def sanitize_path(path):
    # translated from gitlab-shell/lib/gitlab_net.rb
    return path.replace("'", "")


def git_hook_format_changes(changes):
    """Format Git changes in the way Git hooks expect them in `stdin`.

    :param changes: a dict with keys are Git refs, and values are pairs
                    (old_sha, new_sha)
    :return: formatted changes ready to pipe to a Git hook
    """
    return b'\n'.join(
        b' '.join((old_gitsha, new_gitsha, ref))
        for ref, (old_gitsha, new_gitsha) in changes.items())


def parse_broadcast_msg(msg, text_length):
    """Cut into several lines of at most text_length length.
    """
    if len(msg) <= text_length:
        return [msg]

    lines = []
    current = []
    current_len = 0
    for word in msg.split():
        if current_len + len(word) < text_length:
            current.append(word)
            current_len += len(word) + 1
        else:
            lines.append(' '.join(current))
            current = [word]
            current_len = 0

    if current:
        lines.append(' '.join(current))
    return lines


def format_alert_message(message, encoding='utf-8'):
    """Directly translated from gitlab_post_receive.rb in gitlab-shell.

    :param message: expected to be unicode because of length computations.
    :rtype bytes: this will be handed to Mercurial `ui.status`.
    """
    # A standard terminal window is (at least) 80 characters wide.
    total_width = 80

    # Git prefixes remote messages with "remote: ", so this width is subtracted
    # from the width available to us. TODO recheck for Mercurial
    total_width -= len("remote: ")

    # Our centered text shouldn't start or end right at the edge of the window,
    # so we add some horizontal padding: 2 chars on either side.
    text_width = total_width - 2 * 2

    # Automatically wrap message at text_width (= 68) characters:
    # Splits the message up into the longest possible chunks matching
    # "<between 0 and text_width characters><space or end-of-line>".
    lines = [b"", b"=" * total_width, b""]
    for msg_line in parse_broadcast_msg(message, text_width):
        padding = max((total_width - len(msg_line)) // 2, 0)
        lines.append(b" " * padding + msg_line.encode(encoding, 'replace'))

    lines.extend((b"", b"=" * total_width, b""))

    return lines


def format_warnings(warnings, **kw):
    """Format warnings given as unicode strings"""
    return format_alert_message("\n".join(("WARNINGS", warnings)), **kw)


def format_mr_links(mrs, encoding='utf-8'):
    """Like all format_ functions, takes unicode and return bytes."""
    if not mrs:
        return ()

    out_lines = [""]
    for mr in mrs:
        if mr.get("new_merge_request"):
            fmt = "To create a merge request for {branch_name}, visit:"
        else:
            fmt = "View merge request for {branch_name}:"
        fmt += "\n  {url}"
        out_lines.append(fmt.format(**mr))
    return [l.encode(encoding, 'replace') for l in out_lines]


SKIP = object()


class Hook(object):
    """Allow to call a GitLab hook.

    In Heptapod, we disable by default some of the Git hooks, in order to get
    finer control of them by calling them directly.

    This allows the Mercurial process to send accurate user information in
    its inner pushes to Git repos, as well as to notify GitLab of changes
    at the right stage of Mercurial transaction end.
    """

    def init_repo_path_ui(self, repo):
        """Part of instance initialization that needs a repository object.

        A later refactor could transfer this responsibility to callers, but
        would be too much as of this writing.
        """
        main_repo = hg.sharedreposource(repo)
        if main_repo is None:
            main_repo = repo

        # GitLab FS paths are ASCII
        self.repo_path = pycompat.sysstr(main_repo.root)
        self.ui = repo.ui

    def __init__(self, repo, encoding='utf-8'):
        self.init_repo_path_ui(repo)
        # Really making sure that we don't use `repo` further (this
        # is important because GitLab hooks must not depend on references that
        # may be alive when registered as Mercurial transaction or locks
        # callbacks, and obsolete at the time the callback is used.
        del repo

        self.encoding = encoding
        self.git_fs_path = self.repo_path[:-3] + '.git'
        url = pycompat.sysstr(
            self.ui.config(b'heptapod', b'gitlab-internal-api-url',
                           b'http://localhost:8080'))
        self.gitlab_internal_api_endpoint = url + '/api/v4/internal'

        self.gitlab_url = url
        if self.skip():
            return

        secret = self.ui.config(b'heptapod',
                                b'gitlab-internal-api-secret-file')

        if not secret:
            shell = self.ui.config(b'heptapod', b'gitlab-shell')
            if shell:
                candidate = os.path.join(shell, b'.gitlab_shell_secret')
                if os.path.exists(candidate):
                    secret = candidate

        if not secret:
            raise RuntimeError("heptapod.gitlab-internal-api-secret-file "
                               "config parameter is missing.")
        with open(secret, 'r') as secretf:
            self.gitlab_secret = secretf.read().strip()

    def __str__(self):
        return "GitLab %r hook" % self.name

    def __bytes__(self):
        return pycompat.sysbytes(str(self))

    def encode(self, s):
        """Encode a str (python3) or unicode (python2) into bytes.

        This never fails: we can live with a few chars being dropped and
        even the whole to disappear if encoding is latin-1 and the message
        is entirely chinese. It's far less harmful than a push failing
        because of this.
        """
        return s.encode(self.encoding, 'replace')

    def skip(self):
        env = self.ui.environ
        return (
            env.get(b'HEPTAPOD_SKIP_ALL_GITLAB_HOOKS', b'').strip() == b'yes'
            or env.get(b'HEPTAPOD_SKIP_GITLAB_HOOK',
                       b'').strip() == pycompat.sysbytes(self.name)
        )

    def environ(self):
        if self.skip():
            return SKIP

        base = self.ui.environ
        gl_id = base.get(b'HEPTAPOD_USERINFO_GL_ID')
        if gl_id is None:
            user_id = base.get(b'HEPTAPOD_USERINFO_ID')
            if user_id is not None:
                gl_id = b'user-' + user_id

        gl_repo = base.get(b'GL_REPOSITORY')

        if gl_id is None:
            raise ValueError("User id not available")
        if gl_repo is None:
            raise ValueError("GL_REPOSITORY not available")

        mr_iid = base.get(b'HEPTAPOD_ACCEPT_MR_IID')

        env = dict(os.environ)
        env['HG_GIT_SYNC'] = 'yes'
        env['GL_ID'] = gl_id.decode('ascii')
        # Protocol is only to deny access based on blocked protocol,
        # but 'web' is always accepted
        # (see gitlab_access.rb and protocol_access.rb
        # from gitlab-rails/lib/gitlab lib/gitlab)
        env['GL_PROTOCOL'] = 'web'
        env['GL_REPOSITORY'] = pycompat.sysstr(gl_repo)
        if mr_iid is not None:
            env['HEPTAPOD_ACCEPT_MR_IID'] = pycompat.sysstr(mr_iid)
        return env

    def gitlab_internal_api_request(
            self, meth,
            subpath, params, **kwargs):  # pragma: no cover
        logger.debug("Sending %s to %r, params=%r",
                     meth, subpath, params)
        payload = dict(iss='gitlab-shell')
        key = jwk.JWK.from_password(self.gitlab_secret)
        jwt_token = jwt.generate_jwt(payload, key, 'HS256',
                                     datetime.timedelta(minutes=1))
        headers = {'Gitlab-Shell-Api-Request': jwt_token}
        with requests_unixsocket.monkeypatch():
            return requests.request(
                meth,
                '/'.join((self.gitlab_internal_api_endpoint,
                          subpath)),
                data=params,
                headers=headers,
                **kwargs)

    def __call__(self, changes):
        """Call GitLab Hook for the given changes.

        :return: numeric return code, output and error.

        * The return code is like for a process does: 0 for success,
          anything else for failures.
        * The output is returned as a bytes string. That's because it
          will typically be passed to Mercurial user feedback
          methods of :class:`ui.ui`. For the encoding strategy,
          see :meth:`encode`.
        * The error is usually from an inner exception (OS or requests),
          and hence is a :class:`str` instance (Unicode string on Python3)
        """
        if not changes:
            self.ui.debug(
                b"%s: empty set of changes - nothing to do." % self)
            return 0, b'', ''

        try:
            env = self.environ()
        except ValueError as exc:
            msg = b"%s, not sending notifications!" % pycompat.sysbytes(
                exc.args[0])
            self.ui.warn(b"%s: %s" % (self, msg))
            return 1, b'', msg

        if env is SKIP:
            self.ui.note(
                b'%s: bailing (explicitely told not to send)' % self)
            return 0, b'', ''

        ok, out, err = self.execute(changes, env=env)
        return 0 if ok else 1, out, err

    def execute(self, changes, env=None):
        """Call GitLab internal API endpoint
        """
        params = self.params(changes, env=env)
        try:
            resp = self.gitlab_internal_api_request('POST',
                                                    subpath=self.api_endpoint,
                                                    params=params)
        except RequestException:
            logger.exception("GitLab internal API is unreachable")
            return False, b'', "GitLab is unreachable"

        if resp.status_code not in ALLOWED_API_KNOWN_STATUS_CODES:
            return False, b'', "API is not accessible"

        as_json = resp.json()
        logger.debug("%s for changes %r, response: %r",
                     self, changes, as_json)
        return self.handle_response(resp.status_code, as_json)


class PreReceive(Hook):

    name = 'pre-receive'

    api_endpoint = 'allowed'

    error_cls = GitLabPreReceiveError

    def params(self, changes, env=None):
        if env is None:
            env = self.environ()
        git_changes = changes[1]
        params = dict(action='unbundle',
                      changes=git_hook_format_changes(git_changes),
                      gl_repository=env['GL_REPOSITORY'],
                      project=sanitize_path(self.repo_path),
                      vcs='hg',
                      protocol=env['GL_PROTOCOL'],
                      )
        actor_symb, actor = parse_actor(env['GL_ID'])
        params[actor_symb] = actor
        mr_iid = env.get('HEPTAPOD_ACCEPT_MR_IID')
        if mr_iid is not None:
            params['accept_mr_iid'] = int(mr_iid)
        return params

    def handle_response(self, status_code, as_json):
        ok, message = as_json['status'], as_json.get('message')
        err = ''
        out = b''
        if ok:
            if message:
                out = pycompat.sysbytes(message)
        else:
            err = message
        return ok, out, err


class PostReceive(Hook):

    name = 'post-receive'

    api_endpoint = 'post_receive'

    error_cls = GitLabPostReceiveError

    def params(self, changes, env=None):
        if env is None:
            env = self.environ()
        # prune_reasons will be used when we switch to a Mercurial
        # specific endpoint.
        prune_reasons, git_changes = changes[:2]
        push_options = None if len(changes) <= 2 else changes[2]

        hg_prunes = {}
        for gl_branch, reason in pycompat.iteritems(prune_reasons):
            prune_cat = hg_prunes.setdefault(reason.key, {})
            prune_cat[b64encode(gl_branch).decode()] = reason.extract()
        params = dict(gl_repository=env['GL_REPOSITORY'],
                      identifier=env['GL_ID'],
                      changes=git_hook_format_changes(git_changes))

        # Don't send empty prunes dict. This helps us also being sure
        # that `hg_prunes` is indeed *not* required by the endpoint: we
        # want regular Git post-receive hooks to still work, and they wouldn't
        # include that param.
        if hg_prunes:
            params['hg_prunes'] = json.dumps(hg_prunes)
        if push_options:
            push_options_list = []
            for k, v in push_options.items():
                # TODO make pushvars upstream be any strings instead
                # of key=value (mapping 'key' to 'key=' for compat with
                # existing hooks)
                if v == '':
                    push_options_list.append(k)
                else:
                    push_options_list.append('='.join((k, v)))
            params['push_options'] = json.dumps(push_options_list)
        return params

    def handle_response(self, status_code, as_json):
        ok = status_code == 200
        out_lines = []
        logger.info("Post-Receive response: %r", as_json)
        broadcast_message = as_json.get('broadcast_message')
        if broadcast_message is not None:
            out_lines.extend(format_alert_message(
                broadcast_message, self.encoding))
        out_lines.extend(format_mr_links(as_json.get('merge_request_urls')))
        for msg_name in ('redirected_message', 'project_created_message', ):
            msg = as_json.get(msg_name)
            if msg is not None:
                out_lines.append(msg.encode(self.encoding))
        warnings = as_json.get('warnings')
        if warnings is not None:
            out_lines.extend(format_warnings(warnings, encoding=self.encoding))
        # GitLab 12.3: MR links as messages with type 'basic',
        # broadcasts and warnings as type 'alert'
        # basic treatment, probably won't be very pretty, but good enough
        # for now.
        messages = as_json.get('messages', ())
        for message in messages:
            if message.get(u'type') == u'basic':
                out_lines.append(self.encode(message['message']))
        alert = '\n'.join(m['message']
                          for m in messages if m.get(u'type') == u'alert')
        if alert:
            out_lines.extend(format_alert_message(alert, self.encoding))
        return ok, b'\n'.join(out_lines), ''
