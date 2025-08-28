class HeadPruneReason(object):
    """Common base class for reasons a GitLab branch would disappear.

    A GitLab branch corresponds either a branch/topic combination, or to
    a named branch, or to a bookmark.

    The bundled information is important for Merge Request detection on the
    GitLab side.

    :attr:`key` is to be used for extraction.
    :attr:`info` complementary information that can be crucial for
          Merge Request detection or any other action on the GitLab side.

    This base class can be used for an unspecified reason::

        >>> reason = HeadPruneReason()
        >>> reason
        HeadPruneReason(None)

    Extraction without further details for a ref just gives the ref back
    (actually on Python3, ref will be bytes)::

        >>> reason.extract() is None
        True
    """
    key = None

    def __init__(self, info=None):
        self.info = info

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.info)

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.info == other.info

    def extract(self):
        """Extract information for serialization in GitLab API message.

        Can be overridden in subclasses
        """
        return self.info

    def convert_native(self, git_handler):
        """Return a new reason, with all SHAs converted back to Mercurial.
        """
        return self


class HeadPruneReasonWithSha(HeadPruneReason):
    """Base class for all prune reasons whose info is a single SHA (bytes)
    """

    def extract(self):
        return self.info.decode()

    def convert_native(self, handler):
        return self.__class__(handler.map_hg_get(self.info))


class TopicPublished(HeadPruneReasonWithSha):
    """The current transaction published the topic GitLab branch.

    :attr:`info` is the GitLab SHA of the last public changeset
          bearing the given branch/topic combintation. It is useful for
          Merge Request updates, so that they display the same thing as
          if the changeset and their publication had been pushed separately.

    ::

        >>> reason = TopicPublished(b'last_sha')
        >>> 'last_sha' in repr(reason)
        True
        >>> print(reason.extract())
        last_sha
    """
    key = 'topic_published'


class BranchClosed(HeadPruneReason):
    """The GitLab branch is closed within the current transaction.

    :attr:`info` is a list of pairs, one for each new closing changeset.
         The first element of each pair is the GitLab SHA of the new closing
         changeset, and the second element is the list of GitLab SHAs for its
         parents. Both information can be useful in Merge Request detection.
         Can also be ``None`` in cases of lingering old closed branches.

    >>> BranchClosed().extract() is None
    True
    """
    key = 'branch_closed'

    def convert_native(self, handler):
        if self.info is None:
            return self

        hg_sha = handler.map_hg_get
        return self.__class__(
            [(hg_sha(closing), [hg_sha(p) for p in parents])
             for closing, parents in self.info]
        )

    def extract(self):
        if self.info is None:
            return None
        return [[closing.decode(), [p.decode() for p in parents]]
                for closing, parents in self.info]


class BookmarkRemoved(HeadPruneReasonWithSha):
    """
    :attr:`info` is the GitLab SHA for the previous position of the bookmark
    """
    key = 'bookmark_removed'


class WildHeadResolved(HeadPruneReasonWithSha):
    """Used when a wild head is no more a head.

    Could be because it has more wild descendents, or because it's been
    properly merged.
    """
    key = 'wild_resolved'


class AllHeadsBookmarked(HeadPruneReason):
    """Used if all heads of a named branch become bookmarked.

    In that case, the GitLab branch for the named branch simply disappears.
    """
    key = 'all_heads_bookmarked'
