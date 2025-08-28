# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import webtest

from mercurial.hgweb import hgweb_mod

from .test_wsgi import make_hgserve
from ..testhelpers import (
    RepoWrapper,
)


def make_repo_app(base_dir):
    """Prepare a repo and the HgServe application rewrapper in a TestApp.

    return repo wrapper, app
    """
    repo_wrapper = RepoWrapper.init(
        base_dir.join('group').ensure(dir=True).join('proj.hg'),
        config=dict(extensions=dict(evolve='')),
    )
    repo_wrapper.write_commit('foo', message='Foo')
    hgs = make_hgserve(base_dir)
    return repo_wrapper, webtest.TestApp(hgs)


def test_simple_gets_and_errors(tmpdir):
    rw, app = make_repo_app(tmpdir)
    resp = app.get('/group/proj.hg', params=dict(cmd='capabilities'))
    assert 'bundle2=HG20' in resp.text

    resp = app.get('/group/proj.hg', params=dict(cmd='heads'))
    assert resp.text.strip().encode() == rw.repo[0].hex()

    resp = app.get('/group/proj.hg', params=dict(cmd='unknown'), status=400)
    err_msgs = ('no such method', '400 method not found')
    assert any(resp.status.lower() == msg for msg in err_msgs)

    app.get('/no/such/project', status=404)
    app.get('/group/proj.hg/log/2', status=404)


def test_io_error(tmpdir):
    repo_wrapper, app = make_repo_app(tmpdir)

    # a way to trigger an IOError that's not catched by
    # lower level Mercurial layers would be to make the repo
    # unreadable. However, this breaks on CI because the tests user
    # is too privileged to lock himself out of anything.
    # Let's just mock it, then.
    orig = hgweb_mod.hgweb.run_wsgi
    try:
        def raiser(*a, **kw):
            raise IOError("not from this test")
        hgweb_mod.hgweb.run_wsgi = raiser
        app.get('/group/proj.hg', params=dict(cmd='heads'), status=500)
    finally:
        hgweb_mod.hgweb.run_wsgi = orig


def test_content_security_policy(tmpdir):
    # we don't need a repo for this test
    hgs = make_hgserve(tmpdir)
    app = webtest.TestApp(hgs)
    csp = b"default-src *; script-src https://assets.heptapod.example;"
    hgs.ui.setconfig(b'web', b'csp', csp)
    resp = app.get('/', status=404)
    assert resp.headers['Content-Security-Policy'] == csp.decode()
