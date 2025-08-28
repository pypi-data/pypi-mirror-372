# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import tempfile

from mercurial.i18n import _
from mercurial import (
    bundlerepo,
    bundle2,
    error,
    exchange,
    hg,
    pycompat,
)

from hgext3rd.topic import _changetopics


def pull_force(ui, repo, source, pull_rev, topic, **opts):

    other = hg.peer(repo, opts, source)
    branches = (None, ())  # we want to work on precise revs only
    revs, checkout = hg.addbranchrevs(repo, other, branches, pull_rev)
    if revs:
        revs = [other.lookup(rev) for rev in revs]

    fd, bundlepath = tempfile.mkstemp(prefix='pull-force-topic')
    # it's a bit unfortunate that we wouldn't get a bundlerepo without
    # 'bundlename' for local repos as it wouldn't work on tests or be
    # really different than real usage.
    bundlepath = pycompat.sysbytes(bundlepath)
    other, inc_nodes, cleanupfn = bundlerepo.getremotechanges(
        ui, repo.unfiltered(), other,
        onlyheads=revs,
        force=opts.get('force'),
        bundlename=bundlepath,
    )
    if not inc_nodes:
        ui.status(_(b"Empty pull, nothing to do\n"))
        cleanupfn()
        return 1

    try:
        bundle = os.fdopen(fd, 'rb')
        with repo.lock():
            with repo.transaction(b'pull-force-topic') as txn:
                unbundle(ui, repo, bundle, txn)
                change_topic(ui, repo, topic, inc_nodes)
        return 0
    finally:
        cleanupfn()
        cleanup_tmp_bundle(ui, bundle, bundlepath)


def cleanup_tmp_bundle(ui, fobj, path):
    try:
        os.unlink(path)
        fobj.close()
    except Exception as exc:
        ui.warn(b"Got an error while cleaning up '%s': %r\n" % (
            path, exc))


def unbundle(ui, repo, bundle, transaction):
    """Unbundler for pull-force-topic.

    inspired from `commands.unbundle()`, much simplified to run
    in an already provided transaction, and have only what we need.

    :param bundle: file-like object
    :param txn: Mercurial transaction
    """
    # we probaly already made sure in negociation with remote
    # that we don't risk getting BundleUnknownFeatureError
    # on a bundle we generated ourselves
    gen = exchange.readbundle(ui, bundle, None)
    op = bundle2.applybundle(repo, gen, transaction,
                             source='pull-force-topic')
    bundle2.combinechangegroupresults(op)
    # commands.postincoming is for user feedback and wdir update


def non_obsolete_revs(repo, nodes):
    rev = repo.changelog.rev
    for node in nodes:
        try:
            yield rev(node)
        except error.FilteredLookupError:
            pass


def change_topic(ui, repo, topic, nodes):
    revset = repo.revs('%ld', non_obsolete_revs(repo, nodes))
    if repo.revs(b'%ld and public()', revset):
        raise error.Abort(b"can't change topic of a public change")
    _changetopics(ui, repo, revset, topic)
