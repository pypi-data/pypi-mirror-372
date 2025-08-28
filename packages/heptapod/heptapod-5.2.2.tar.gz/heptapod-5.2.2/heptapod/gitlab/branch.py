# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities and conventions for GitLab branches.

Although Mercurial branches don't have much in common with Git branches,
the GitLab web application still needs to handle "branches" as source and
target for Merge Requests, for navigation etc. This means that GitLab needs
to address Mercurial content through abstract "GitLab branches", which, like
Git branches are just references to uniquely defined Mercurial revisions.

In classical upstream GitLab, a GitLab branch is just a Git branch.

Under the hood, GitLab branches can be also be adressed by full Git-like
reference names.

A "branchmap branch" is what gets displayed by the `hg branches` command.
Internally these are the keys of the branchmap object.

To avoid ambiguities, in this module function names and variables,
we never use the "branch" word alone, it's always either "GitLab branch" or
"named branch" etc, even if that sounds heavy or silly.
"""
from hgext3rd.topic.common import formatfqbn, parsefqbn
GITLAB_BRANCH_REF_PREFIX = b'refs/heads/'
NAMED_BRANCH_PREFIX = b'branch/'
TOPIC_BRANCH_PREFIX = b'topic/'
WILD_BRANCH_PREFIX = b'wild/'


class InvalidGitLabBranch(ValueError):
    pass


class InvalidRef(ValueError):
    pass


def gitlab_branch_ref(gitlab_branch):
    return GITLAB_BRANCH_REF_PREFIX + gitlab_branch


TOPIC_REF_PREFIX = gitlab_branch_ref(TOPIC_BRANCH_PREFIX)
NAMED_BRANCH_REF_PREFIX = gitlab_branch_ref(NAMED_BRANCH_PREFIX)
WILD_BRANCH_REF_PREFIX = gitlab_branch_ref(WILD_BRANCH_PREFIX)


def gitlab_branch_from_ref(ref):
    """Return GitLab branch name from a ref name.

    Examples::

      >>> from mercurial.pycompat import sysstr as to_str
      >>> to_str(gitlab_branch_from_ref(b'refs/heads/some/branch'))
      'some/branch'
      >>> gitlab_branch_from_ref(b'refs/tags/1.0.1') is None
      True


    Special case for robustness::

      >>> gitlab_branch_from_ref(None) is None
      True
    """

    if ref is None or not ref.startswith(GITLAB_BRANCH_REF_PREFIX):
        return None
    return ref[len(GITLAB_BRANCH_REF_PREFIX):]


def ref_is_topic(ref):
    return ref.startswith(TOPIC_REF_PREFIX)


def ref_is_named_branch(ref):
    return ref.startswith(NAMED_BRANCH_REF_PREFIX)


def ref_is_wild_branch(ref):
    return ref.startswith(WILD_BRANCH_REF_PREFIX)


def branch_is_topic(branch):
    """Tell if GitLab branch is a topic.

    Examples::

      >>> branch_is_topic(b'branch/gnu')
      False
      >>> branch_is_topic(b'topic/default/gnu')
      True
    """
    return branch.startswith(TOPIC_BRANCH_PREFIX)


def parse_ref(ref):
    """Parse a Git branch ref for named branch and topic information

    Return ``None`` if ``ref`` is not a Git branch. This is considered
    to be a normal case::

      >>> parse_ref(b"refs/tags/v1.2.3") is None
      True

    Example with a topical GitLab branch::

      >>> parsed = parse_ref(b"refs/heads/topic/default/thetop")
      >>> parsed == (b'default', b'thetop')
      True

    For named branches, the returned topic is ``None``. Checking for `None`
    is the normal way for downstream code to know if this is a topic or not::

      >>> parsed = parse_ref(b"refs/heads/branch/default")
      >>> parsed == (b'default', None)
      True

    Special case: forward slashes are considered part of the named branch::

      >>> parsed = parse_ref(b"refs/heads/branch/ze/branch")
      >>> parsed == (b'ze/branch', None)
      True


      >>> from mercurial.pycompat import sysstr as to_str
      >>> try:
      ...     _ = parse_ref(b"refs/heads/topic/invalid")
      ... except InvalidRef as exc:
      ...     print(to_str(exc.args[0]))
      ... else:
      ...     print("Expected InvalidRef exception not raised")
      refs/heads/topic/invalid
    """
    gitlab_branch = gitlab_branch_from_ref(ref)
    if gitlab_branch is None:
        return None
    try:
        return parse_gitlab_branch(gitlab_branch)
    except InvalidGitLabBranch:
        raise InvalidRef(ref)


def parse_gitlab_branch(git_branch):
    """For GitLab branches related to Mercurial branches and topics.

    :return: ``(Mercurial branch name, topic name)`` or ``None`` if
             another kind (currently wild or bookmark)
    """

    topic_prefix = b'topic/'
    if git_branch.startswith(topic_prefix):
        res = tuple(git_branch.split(b'/', 1)[1].rsplit(b'/', 1))
        if len(res) != 2:
            raise InvalidGitLabBranch(git_branch)
        return res

    named_branch_prefix = b'branch/'
    if git_branch.startswith(named_branch_prefix):
        return git_branch[len(named_branch_prefix):], None


def parse_wild_gitlab_branch(gl_branch):
    """Parse GitLabbranch name from the "wild" namespace.

    :return: ``None`` if not a wild branch, or changeset hexadecimal node id.

    Examples::

      >>> from mercurial.pycompat import sysstr as to_str
      >>> to_str(parse_wild_gitlab_branch(b'wild/01deadbeef'))
      '01deadbeef'
      >>> parse_wild_gitlab_branch(b'tame/experiment') is None
      True
    """
    if not gl_branch.startswith(WILD_BRANCH_PREFIX):
        return None

    return gl_branch[len(WILD_BRANCH_PREFIX):]


def branchmap_branch_from_gitlab_branch(gl_branch):
    """Return the branchmap branch for a given GitLab branch.

    Many GitLab branches don't correspond to branchmap branches. In that
    case ``None`` is returned.

    Examples::

      >>> from mercurial.pycompat import sysstr as to_str
      >>> to_str(branchmap_branch_from_gitlab_branch(b'branch/default'))
      'default'
      >>> to_str(branchmap_branch_from_gitlab_branch(b'topic/default/zetop'))
      'default//zetop'
      >>> branchmap_branch_from_gitlab_branch(b'bookmark') is None
      True
    """
    parsed = parse_gitlab_branch(gl_branch)
    if parsed is None:
        return None  # could be a SHA, a bookmark or a tag
    branch, topic = parsed
    if topic is None:
        return formatfqbn(branch=branch)
    return formatfqbn(branch=branch, topic=topic)


class TopicNameSpaceUnsupported(ValueError):
    """Exception raised when encountering a topic namespace.

    (figure of speech for a value different from the default namespace).
    These are not supported yet.
    """


def parse_branchmap_branch(branchmap_branch):
    """Return (branch, topic) from a branchmap branch name.

    Same as in :func:`parse_gitlab_branch`, we use ``None`` to mean there is
    no topic.
    """
    branch, topic_ns, topic = parsefqbn(branchmap_branch)
    if not topic:
        topic = None
    # absence of topic namespace is encoded as 'default' in hg-evolve 11.0
    # and 'none' in hg-evolve 11.1
    if topic_ns not in (b'default', b'none'):
        raise TopicNameSpaceUnsupported
    return branch, topic


def gitlab_branch_from_branchmap_branch(branchmap_branch):
    """Return the GitLab branch for a branchmap branch.

    Examples::

      >>> from mercurial.pycompat import sysstr as to_str
      >>> to_str(gitlab_branch_from_branchmap_branch(b"default"))
      'branch/default'
      >>> to_str(gitlab_branch_from_branchmap_branch(b"other//zetop"))
      'topic/other/zetop'

    """
    branch, topic = parse_branchmap_branch(branchmap_branch)
    if topic is None:
        return b'branch/' + branch
    return b'topic/%s/%s' % (branch, topic)
