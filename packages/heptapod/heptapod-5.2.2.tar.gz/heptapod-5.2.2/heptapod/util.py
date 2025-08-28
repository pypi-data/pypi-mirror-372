from itertools import islice
from mercurial.i18n import _


def format_bytes_list(bl):
    """Format any iterable of byte strings as a list for output.
    """
    return b'[%s]' % b', '.join(bl)


def format_shas(shas, limit=4):
    """Format and shorten hexadecimal hashes for user feedback.

    :param shas: any iterable with len() of byte strings. each assumed to
                 be a hash in hexadecimal form (customary called "sha"
                 in the whole hg-git/py-heptapod code base).
    :param int limit: maximum number of shortened hashes to explicitely
                     include. Can be ``None`` to include all of them.
    :returns: a formatted bytes string
    """
    excerpt = shas if limit is None else islice(shas, 0, limit)
    first = b' '.join(sha[:12] for sha in excerpt)

    # we could also add special rules for iterables not implementing `len()`
    # but it's not needed right now.
    shas_len = len(shas)
    if limit is None or shas_len <= limit:
        return first

    return _(b"%s and %d others") % (first, shas_len - limit)
