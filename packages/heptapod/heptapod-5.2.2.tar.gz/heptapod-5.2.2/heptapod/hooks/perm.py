# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    configitems,
    error,
    pycompat,
    scmutil,
    phases,
)

from ..util import format_bytes_list

WEB_PERMISSIONS = dict(write=b'allow-push',
                       publish=b'allow-publish')


if 'allow-publish' not in configitems.coreitems[b'web']:
    configitems._register(configitems.coreitems,
                          section=b'web',
                          name=b'allow-publish',
                          alias=[(b'web', b'allow_publish')],
                          default=lambda: list([b'*']),
                          )


def validate_hook_type(expected, hooktype=None, **kw):
    """Check that the hook has the expected type, and raise if not.

    It is really important that permission check hooks get executed
    in the right position (pretxnopen, pretxclose).

    For example, it's better to reject invalid writes right away than to
    rollback them, for efficiency and security (smaller attack surface).

    It's also a matter of having the right information at disposal.

    Example usage::

      >>> from heptapod.hooks import perm
      >>> def the_hook(repo, *args, **kwargs):
      ...     perm.validate_hook_type('precommit', **kwargs)
      ...     return 0  # success

    ``repo`` is not needed for our example, and actually that proves it won't
    be used at all::

      >>> repo = None

      >>> the_hook(None, hooktype='precommit')
      0
      >>> the_hook(None, hooktype='postxn') # doctest: +IGNORE_EXCEPTION_DETAIL
      Traceback (most recent call last):
      ProgrammingError: This hook must be used as 'precommit', not 'postxn'.

    :param expected: the proper hook type, e.g, ``pretxnopen``.
    :param hooktype: should be passed straight from hook kwargs
    """
    if hooktype == expected:
        return
    raise error.ProgrammingError(
        "This hook must be used as a %r, not %r" % (pycompat.sysstr(expected),
                                                    pycompat.sysstr(hooktype)))


def get_remote_user(repo):
    """Return remote user name, or `None`

    within Heptapod, the absence of a remote user means that `hg` is invoked
    from the command line, or directly by a server-side process, such as
    the Rails application performing a merge.

    Hence `None` implies to skip all permission checks.

    TODO rename as ``get_user``: it's not obvious for the caller what
    this 'remote' means, it's coincidental, due to the env var we chose for
    uniformity with WSGI.
    """
    return repo.ui.environ.get(b"REMOTE_USER", None)


def allowed(repo, remote_user, config_group, config_item):
    """Read from repo config list to check if given user is allowed.

    within Heptapod, ``remote_user`` being ``None`` means that `hg` is invoked
    from the command line, or directly by a server-side process, such as
    the Rails application performing a merge.

    In these cases, the permission
    checking responsibility is on the caller. Hence a ``None`` remote user
    is always allowed.

    TODO (not in an urgent stable release as the upcoming 0.20.4)
    adopt this code in :func:`is_user_allowed`, hiding implementation
    and historical details to the caller.
    """
    allowed = repo.ui.configlist(config_group, config_item)

    if remote_user is None or b'*' in allowed or remote_user in allowed:
        # leaving %r for user so that it works without extra effort for None
        repo.ui.debug(b"user %r is allowed by %s.%s=%s" % (
            remote_user, config_group, config_item,
            format_bytes_list(allowed)))
        return True

    return False


def is_user_allowed(repo, permission):
    """High level function, hiding all implementation details.

    The current user is determined according to how it is supposed to
    be transmitted by the various Heptapod components, then the prescribed
    permission is checked.

    :param str permission: currently ``write`` or ``publish``.
    """
    return allowed(repo, get_remote_user(repo), b'web',
                   WEB_PERMISSIONS[permission])


def check_write(repo, *args, **kwargs):
    """Check that remote user has write privileges.

    In this hook, the very fact to be called serves as detection that a
    write operation will happen.

    Therefore the implementation is very straightforward.
    """
    validate_hook_type(b'pretxnopen', **kwargs)

    remote_user = get_remote_user(repo)
    if remote_user is not None:
        repo.ui.debug(
            b"check_write detected push from user: '%s'\n" % remote_user)

    if allowed(repo, remote_user, b'web', b'allow-push'):
        return 0

    msg = b"user '%s' does not have write permission" % remote_user
    repo.ui.note(msg)
    repo.ui.status(msg)
    return 1


def extract_published_revs(tr):
    """Extract revision numbers of revision published by given transaction.

    :returns: iterable of revision numbers, without duplicates.
    """
    phaseschanges = tr.changes.get(b"phases", ())
    try:
        # phases changes is a dict in hg < 5.4
        phaseschanges = pycompat.iteritems(phaseschanges)
        revs_range = False
    except AttributeError:
        # phaseschanges is a list of pairs in hg >= 5.4
        revs_range = True

    publishing = set(rev for rev, (old, new) in phaseschanges
                     if new == phases.public and old != phases.public)

    # TODO drop this once we are on hg >= 5.4 only
    if revs_range:
        publishing = set(rev for rev_range in publishing for rev in rev_range)
    return publishing


def check_publish(repo, *args, **kwargs):
    validate_hook_type(b'pretxnclose', **kwargs)
    remoteuser = get_remote_user(repo)

    if remoteuser is not None:
        repo.ui.debug(
            b"check_publish detected push from user: '%s'\n" % remoteuser)

    if allowed(repo, remoteuser, b'web', b'allow-publish'):
        # we have nothing more to check
        return 0

    tr = repo.currenttransaction()
    assert tr is not None and tr.running()
    publishing = extract_published_revs(tr)
    if publishing:
        node = repo.changelog.node
        nodes = [node(r) for r in sorted(publishing)]
        nodes = scmutil.nodesummaries(repo, nodes)
        msg = (
            b'You are not authorised to publish changesets: %s\n'
            b'For more information about topics auto-publishing rules '
            b'in Heptapod, '
            b'see: https://heptapod.net/pages/faq.html#bare-draft\n'
        )
        raise error.Abort(msg % nodes)
    return 0
