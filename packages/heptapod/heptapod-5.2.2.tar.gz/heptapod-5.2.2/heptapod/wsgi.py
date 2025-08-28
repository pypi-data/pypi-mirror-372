# heptapod/hgweb.py - Heptapod HTTP interface for a directory of repositories.
#
# derived under GPL2+ from Mercurial's hgwebdir_mod.py, whose
# copyright holders are
#   Copyright 21 May 2005 - (c) 2005 Jake Edge <jake@edge2.net>
#   Copyright 2005, 2006 Matt Mackall <mpm@selenic.com>
#
# This file Copyright 2019 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import

import logging
import gc
import os
import time
import weakref

from mercurial.i18n import _

from mercurial.hgweb.common import (
    ErrorResponse,
    HTTP_SERVER_ERROR,
    HTTP_NOT_FOUND,
    cspvalues,
    statusmessage,
)

from mercurial import (
    error,
    extensions,
    hg,
    profiling,
    pycompat,
    ui as uimod,
)

from mercurial.hgweb import (
    hgweb_mod,
    request as requestmod,
)
from mercurial.repoview import _filteredrepotypes


logger = logging.getLogger(__name__)
# logging configuration will be initialized from the Mercurial global
# configuration, overriding this:
logging.basicConfig(level=logging.INFO)

ALLOWED_REMOTES = (
    '127.0.0.1',
    '::1',
    '',  # Unix Domain Socket
)


# Suffixes of HTTP headers that are directly forwarded in environment
FORWARDED_HEADERS_SUFFIXES = (
    'USERINFO_ID',
    'USERINFO_USERNAME',
    'USERINFO_NAME',
    'USERINFO_EMAIL',
    'PROJECT_PATH',
    'PROJECT_NAMESPACE_FULL_PATH',
    'PUBLIC_REPOSITORY',
)


def clear_repo_class(repo_class):
    _filteredrepotypes.pop(repo_class, None)


class HgServe(object):
    """WSGI application serving repositories under a given root path

    The repositories are expected in the `heptapod.repositories-root`
    Mercurial configuration.

    This works under full trust of the incoming request: callers are either
    `gitlab-rails` or `gitlab-workhorse`.
    """
    def __init__(self, conf_path=None, baseui=None):
        """On python3, conf_path is str."""
        self.baseui = baseui
        if baseui:
            self.ui = baseui.copy()
        else:
            self.ui = uimod.ui.load()
        self.motd = None
        self.requests_count = 0
        self.gc_full_collect_rate = self.ui.configint(
            b'experimental', b'web.full-garbage-collection-rate'
        )
        self.gc_full_collections_done = 0
        if not baseui:
            # set up environment for new ui
            extensions.loadall(self.ui)
            extensions.populateui(self.ui)
        self.conf_path = conf_path
        if conf_path is not None:
            for i, rcf in enumerate(conf_path.split(':')):
                # ui.readconfig does a blank open(), but will later
                # store the file path (needing bytes, of course)
                rcf = pycompat.fsencode(rcf)
                if i == 0 and not os.path.exists(rcf):
                    raise error.Abort(_(b'config file %s not found!') % rcf)
                logger.info("Loading configuration from %r", rcf)
                self.ui.readconfig(rcf, trust=True)

        root = self.ui.config(b'heptapod', b'repositories-root')
        if root is None:
            raise ValueError("heptapod.repositories-root is not configured.")
        self.repos_root = root

    def apply_heptapod_headers(self, environ):
        environ['HEPTAPOD_HGRC'] = self.conf_path
        perm_user = environ.get('HTTP_X_HEPTAPOD_PERMISSION_USER')
        if perm_user is not None and environ['REMOTE_ADDR'] in ALLOWED_REMOTES:
            environ['REMOTE_USER'] = perm_user
        for hepta_key in FORWARDED_HEADERS_SUFFIXES:
            hepta_val = environ.pop('HTTP_X_HEPTAPOD_' + hepta_key, None)
            if hepta_val is not None:
                environ['HEPTAPOD_' + hepta_key] = hepta_val
        # special case for GL_REPOSITORY, forwarded as such to match
        # system environment variable name in subprocess calls
        gl_repo = environ.pop('HTTP_X_HEPTAPOD_GL_REPOSITORY', None)
        if gl_repo is not None:
            environ['GL_REPOSITORY'] = gl_repo
            split_repo = gl_repo.split('-', 1)
            if len(split_repo) == 2:
                environ['HEPTAPOD_REPOSITORY_USAGE'] = split_repo[0]
                environ['HEPTAPOD_PROJECT_ID'] = split_repo[1]

    def __call__(self, env, respond):
        self.apply_heptapod_headers(env)
        profile = self.ui.configbool(b'profiling', b'enabled')
        with profiling.profile(self.ui, enabled=profile):
            try:
                for r in self._runwsgi(env, respond):
                    yield r
            finally:
                # There are known cycles in localrepository that prevent
                # those objects (and tons of held references) from being
                # collected through normal refcounting.
                # In some cases, the resulting memory consumption can
                # be tamed by performing explicit garbage collections.
                # In presence of actual leaks or big long-lived caches, the
                # impact on performance of such collections can become a
                # problem, hence the rate shouldn't be set too low.
                # See "Collecting the oldest generation" in
                # https://devguide.python.org/garbage_collector
                # for more about such trade-offs.
                rate = self.gc_full_collect_rate

                # this is not thread safe, but the consequence (skipping
                # a garbage collection) is arguably better than risking
                # to have several threads perform a collection in parallel
                # (long useless wait on all threads).
                self.requests_count += 1
                if rate > 0 and self.requests_count % rate == 0:
                    start = time.time()
                    gc.collect()
                    elapsed = time.time() - start
                    self.ui.note(b"Total requests served: %d, full garbage "
                                 b"collecting (rate=%d) done in %dms. Stats "
                                 b"after: %r" % (self.requests_count,
                                                 rate,
                                                 elapsed * 1000,
                                                 gc.get_stats()))
                    self.gc_full_collections_done += 1
                else:
                    gc.collect(generation=1)

    def load_repo(self, uri_path, env):
        repo_path = os.path.join(self.repos_root, uri_path)
        if not os.path.isdir(os.path.join(repo_path, b'.hg')):
            # hg.repository() would raise a RepoError which is
            # not qualified enough to distinguish it cleanly (just
            # the message)
            raise ErrorResponse(HTTP_NOT_FOUND, "Not Found")
        logger.info("loading repo at %r", repo_path)
        repo = hg.repository(self.ui, repo_path)
        weakref.finalize(repo, clear_repo_class, repo.unfiltered().__class__)

        # setting native mode booleans
        native = env.get('HTTP_X_HEPTAPOD_HG_NATIVE')
        if native:
            repo.ui.setconfig(b'heptapod', b'native',
                              pycompat.sysbytes(native))
        return repo

    def _runwsgi(self, env, respond):
        baseurl = self.ui.config(b'web', b'baseurl')
        # TODO simplify without bringing too much code duplication
        first_parse = requestmod.parserequestfromenv(env, altbaseurl=baseurl)
        uri_path = first_parse.dispatchpath.strip(b'/')
        try:
            # Actual parsing of WSGI environment to take into account our
            # repository path component.
            req = requestmod.parserequestfromenv(
                env, reponame=uri_path,
                altbaseurl=baseurl,
                # Reuse wrapped body file object otherwise state
                # tracking can get confused.
                bodyfh=first_parse.bodyfh)
            res = requestmod.wsgiresponse(req, respond)
            csp = cspvalues(self.ui)[0]
            if csp:
                res.headers[b'Content-Security-Policy'] = csp

            try:
                repo = self.load_repo(uri_path, env)
                return hgweb_mod.hgweb(repo).run_wsgi(req, res)
            except IOError as inst:
                raise ErrorResponse(HTTP_SERVER_ERROR, inst.strerror)
            except error.RepoError as inst:  # pragma: no cover
                # This case can't happen because hgweb_mod catches them
                # already. To be removed in Heptapod 0.8
                raise ErrorResponse(HTTP_SERVER_ERROR, bytes(inst))

        except ErrorResponse as e:
            # not passing the 'message' kwarg here gives us the standard
            # human readable version of the code (e.g., '404 Not Found').
            # Details about the error are provided in the body.
            res.status = statusmessage(e.code)
            res.headers[b'Content-Type'] = b'text/plain; charset=UTF-8'
            # ErrorResponse.message is produced by pycompat.sysstr
            # Python2: the encoding could be anything, and it's not
            #          not even clear that `encoding.encoding` would apply.
            #          At worst, our Content-Type is wrong.
            # Python3: it could be emitted originally as `str` or have been
            #          decoded to `latin-1` by `sysstr()`. In the latter
            #          case, the upstream usage of `sysstr()` would be plain
            #          wrong.
            # That was in theory. In practice, all messages generated
            # by hgweb are actually ASCII as of Mercurial 5.4,
            # except maybe repetition of user requested file.
            # pycompat.sysbytes() encodes to UTF-8 in py3
            res.setbodybytes(pycompat.sysbytes(e.message) + b'\n')
            return res.sendresponse()

    @classmethod
    def default_app(cls):
        HEPTAPOD_HGRC = os.environ.get('HEPTAPOD_HGRC')
        if HEPTAPOD_HGRC:
            return HgServe(conf_path=HEPTAPOD_HGRC)


hgserve = HgServe.default_app()
