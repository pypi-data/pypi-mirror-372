# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import itertools
import traceback
# Even for fully native Mercurial projects, we'll need
# to make sure that our refs are acceptable to GitLab.
# For now, we are not planning to drop the dependency to Dulwich
# and perhaps we never will (push to external Git repo), but if that
# becomes an issue, it won't be so hard to find a solution
from dulwich.repo import check_ref_format

from mercurial import (
    error,
    phases,
    pycompat,
)
from mercurial.encoding import encoding as cli_encoding
from mercurial.node import hex
from mercurial.i18n import _

from heptapod import (
    obsutil,
    util,
)
from heptapod.gitlab.branch import (
    TopicNameSpaceUnsupported,
    branch_is_topic,
    gitlab_branch_from_ref,
    gitlab_branch_ref,
    parse_branchmap_branch,
    parse_gitlab_branch,
    ref_is_topic,
    ref_is_named_branch,
    ref_is_wild_branch,
    InvalidGitLabBranch,
)
from heptapod.gitlab.change import (
    ZERO_SHA,
    GitLabRefChange,
)
from heptapod.gitlab.hooks import (
    PreReceive,
    PostReceive,
)
from heptapod.gitlab.prune_reasons import (
    AllHeadsBookmarked,
    BookmarkRemoved,
    BranchClosed,
    HeadPruneReason,
    TopicPublished,
    WildHeadResolved,
)
from heptapod.gitlab.tag import (
    gitlab_tag_ref,
    gitlab_tag_from_ref,
)
from heptapod.hooks.perm import is_user_allowed


from .branch import (
    write_gitlab_branches,
    write_gitlab_tags,
)
from .special_ref import parse_special_ref
from .keep_around import parse_keep_around_ref

REF_TARGET_PASS_THROUGH = object()
"""Possible value for fallback in GitLab refs conversion."""

REF_TARGET_UNKNOWN_RAISE = object()
"""Possible value for fallback in GitLab refs conversion."""

DOT_BYTE = ord(b'.')


class MultipleDescendants(LookupError):
    pass


class GitLabStateMaintainer:
    """Base class providing logic to maintain state shared with GitLab.

    More specifically, the maintained state can be used directly by HGitaly,
    and this class handles all needed notifications to GitLab components,
    (mostly the Rails app).

    All the logic is also meant to be applicable in the hg-git case.
    """

    #
    # Methods to be implemented by concrete classes
    #

    def get_default_gitlab_ref(self):
        raise NotImplementedError  # pragma no cover

    def set_default_gitlab_ref(self):
        raise NotImplementedError  # pragma no cover

    def gitlab_sha_from_hg_sha(self, sha):
        raise NotImplementedError  # pragma no cover

    def hg_sha_from_gitlab_sha(self, sha):
        raise NotImplementedError  # pragma no cover

    def extract_all_gitlab_refs(self):
        """Assessment of GitLab refs for current state of Mercurial repo.

        This is what GitLab should see once we are done telling it.
        """
        raise NotImplementedError  # pragma no cover

    #
    # Methods relying on the expected implemented methods
    #

    @property
    def native(self):
        return self.repo.ui.configbool(b'heptapod', b'native')

    def is_wiki(self):
        """Tell whether self.repo is the storage for a GitLab wiki"""
        return (self.repo.ui.environ.get(b'GL_REPOSITORY', b'')
                .startswith(b'wiki-'))

    def get_default_gitlab_branch(self):
        return gitlab_branch_from_ref(self.get_default_gitlab_ref())

    def extract_current_gitlab_branches(self, gitlab_refs):
        """Assessment of GitLab branches for current state of Mercurial repo.

        This method updates the :param:`gitlab_refs` dict, so that the refs
        stored in its value completely reflect the current state of the
        Mercurial repository. The provided information cannot be derived from
        the GitLab branches state file nor in anyway from GitLab knowledge of
        the repository: it is precisely meant to update these.

        The 'current state' includes any ongoing transaction, which is the most
        common case (receiving a push, or performing writes from GitLab).

        Once completed, the GitLab branches in the values of `gitlab_refs` are
        """
        logprefix = b'HeptapodGitHandler.get_exportable '
        repo = self.repo.filtered(b'served')
        ui = repo.ui

        # "exporting" the ZERO_SHA will mean by convention a request to prune
        # the corresponding heads -- only a request, we can't really decide
        # at this stage.
        # The value is a dict mapping refs to reasons (instances of
        # `HeadPruneReason` or simple strings if it needs to be refined later)
        to_prune = gitlab_refs[ZERO_SHA] = {}

        txn = repo.currenttransaction()
        allow_bookmarks = ui.configbool(b'experimental',
                                        b'hg-git.bookmarks-on-named-branches')
        allow_multiple_heads = ui.configbool(b'heptapod',
                                             b'allow-multiple-heads')
        if txn is None:
            deleted_bms = ()
        else:
            bm_changes = txn.changes.get(b'bookmarks')
            deleted_bms = self.heptapod_gate_bookmarks(
                repo, allow_bookmarks, bm_changes)
            # after general bookmark gating in order not to mask the
            # more common message that bookmarks aren't allowed anyhow.
            self.validate_obsolescence(txn)

        to_prune.update((bm, BookmarkRemoved(prev_git_sha))
                        for (bm, prev_git_sha) in deleted_bms)
        hgshas_with_bookmark_gitlab_ref = {
            hex(node) for node in self.repo._bookmarks.values()
        }
        for branch, hg_nodes in repo.branchmap().iteritems():
            gb = self.git_branch_for_branchmap_branch(branch)
            ctxs = [repo[n] for n in hg_nodes]

            if ui.configbool(b'experimental',
                             b'hg-git.prune-newly-closed-branches', True):
                ctxs = [c for c in ctxs if not c.closesbranch()]
                if not ctxs:
                    ui.note(logprefix,
                            b"All heads of branch '%s' are closed" % branch)
                    to_prune[gb] = 'closed'  # will be refined later on

            hg_shas = self.branchmap_entry_process_bookmarks(
                entry=ctxs,
                bookmarked=hgshas_with_bookmark_gitlab_ref,
                gitlab_branch=gb,
                allow_bookmarks=allow_bookmarks,
                to_prune=to_prune,
            )
            self.branchmap_entry_process_finalize(
                hg_shas=hg_shas,
                gitlab_refs=gitlab_refs,
                branchmap_branch=branch,
                gitlab_branch=gb,
                allow_multiple=allow_multiple_heads,
                logprefix=logprefix
            )

    def git_branch_for_branchmap_branch(self, topbranch):
        """return Git branch name for hg branch names in branchmap()

        Does in particular the needed sanitizations to make it acceptable
        for a Git branch.

        :param topbranch: can be either a named branch name or follow the
                          branch:topic convention, as returned by branchmap()
        """
        topbranch = topbranch.replace(b' ', b'_')
        try:
            branch, topic = parse_branchmap_branch(topbranch)
        except TopicNameSpaceUnsupported:
            msg = (b'topic namespaces are not yet supported in '
                   b'Heptapod (found in branch "%s")' % topbranch)
            self.ui.status(msg)
            raise error.Abort(msg)

        if topic is not None:
            topic = topic.replace(b'.lock', b'_lock')
            if topic[0] == DOT_BYTE:
                topic = b'_' + topic[1:]
            if topic[-1] == DOT_BYTE:
                topic = topic[:-1] + b'_'
            if b'/' in topic:
                # very unlikely to happen, it has been forbidden by the
                # topic exension for a long time now, and topics are
                # supposed to be transient by nature, but who knows?
                # - some could have just jumped from an ancient version
                # - busy repos tend to have old stuff still lying around
                msg = b"Invalid character '/' in topic name %r. " % topic
                if self.ui.configbool(b'experimental',
                                      b'hg-git.accept-slash-in-topic-name'):
                    msg += (b"Replacing with '-'. Rename before publishing or "
                            b"you'll get serious problems.")
                    topic = topic.replace(b'/', b'-')
                    self.ui.status(msg)
                    self.ui.warn(msg)
                else:
                    self.ui.status(msg)
                    raise error.Abort(msg)

            return b'/'.join((b'topic', branch, topic))
        return b'branch/' + branch

    def heptapod_gate_bookmarks(self, repo, allow, changes):
        """First handling of bookmark changes (refuse or not), return deleted.

        :param repo: passed explicitely because filtering may differ from
                     :attr:`repo`.
        :return: iterable of deleted bookmarks in the form
            (name, previous GitLab hexadecimal SHA)
        """
        if not changes:
            return ()

        ui = repo.ui
        deleted = []
        ui.note(b"heptapod.gitlab.mirror bookmark changes=%r" % changes)
        new_bookmarks = []

        for name, change in changes.items():
            if change[0] is None:
                new_bookmarks.append(name)
            elif change[1] is None:
                deleted.append((name,
                                self.gitlab_sha_from_hg_sha(hex(change[0]))))

        if new_bookmarks and not allow:
            raise error.Abort(_(
                b"Creating bookmarks is forbidden by default in Heptapod "
                b"(got these new ones: %s). "
                b"See https://heptapod.net/pages/faq.html#bookmarks to "
                b"learn why and how to partially lift "
                b"that restriction" % util.format_bytes_list(new_bookmarks)))
        for new_bm_name, (_ign, new_bm_node) in changes.items():
            new_bm_ctx = repo[new_bm_node]
            new_bm_topic = new_bm_ctx.topic()
            if new_bm_topic:
                raise error.Abort(_(
                    b"Creating or updating bookmarks on topic "
                    b"changesets is forbidden"),
                    hint=b"topic '%s' and bookmark '%s' for changeset %s" % (
                        new_bm_topic, new_bm_name, new_bm_ctx.hex()))
        return deleted

    def branchmap_entry_process_bookmarks(self, gitlab_branch,
                                          entry, bookmarked, to_prune,
                                          allow_bookmarks=False):
        """Bookmarks processing for a branchmap entry.

        This remove bookmarked heads from the entry, scheduling the prune
        for ``gitlab_branch`` into ``to_prune`` if no head remains.

        We want to ignore bookmarked changesets because

        - we don't want them to appear in the ``wild`` namespace
        - the bookmarks are translated directly as GitLab branches
        - no further GitLab ref would be relevant for them

        We don't want to prune the branch if

        - bookmarks aren't explicitely allowed,
          because this may be a side effect, potentially disturbing, of
          an implicit bookmark move during a push.
        - ``gitlab_branch`` is the default GitLab branch. That would be
          totally unexpected and very problematic for GitLab.

        :param entry: the branchmap entry, with closed heads already filtered
           out, and given as a list of :class:`changectx` instances.
        :param bookmarked_shas: a set of changesets known to be
           bookmarked, not restricted to be a subset of ``entry`` and given
           as SHAs.
        :returns: set of SHAs, or None
        """
        hg_shas = {c.hex() for c in entry}
        hg_shas.difference_update(bookmarked)
        if hg_shas:
            return hg_shas

        if gitlab_branch == self.get_default_gitlab_branch():
            # branchmap entry are in increasing revno order, but this is
            # not a good time to make that simplification and performance
            # does not matter for this corner case.

            # if all entries are obsolete, we are reaching the best
            # we can do: just not schedule the prune
            rev_ctxs = [(c.rev(), c) for c in entry if not c.obsolete()]
            rev_ctxs.sort()
            for _r, ctx in reversed(rev_ctxs):
                return {ctx.hex()}

        if allow_bookmarks:
            self.repo.ui.note(
                b"HeptapodGitHandler: scheduling prune of GitLab branch '%s' "
                b"because all its potential heads are bookmarked" % (
                    gitlab_branch))
            to_prune[gitlab_branch] = AllHeadsBookmarked()

    def branchmap_entry_process_finalize(self,
                                         hg_shas,
                                         gitlab_refs,
                                         gitlab_branch,
                                         branchmap_branch,
                                         allow_multiple,
                                         logprefix=b""):
        """Final step of storing exportable values for the given branch.

        After all other rules have been applied, this handles the cases
        where there are 0, 1 or several heads for the given branch.
        storing at most one head in ``gitlab_refs`` for the
        given ``branch`` either enforcing the rejection of multiple heads or
        stoging extra heads in the ``wild`` namespace, according to
        configuration.

        :param hg_shas: iterable of Mercurial changeset SHAs candidates that
            remain for the given ``branchmap_branch``
        :param dict gitlab_refs: mapping of GitLab branches to Mercurial
            changeset IDs.
        """
        if not hg_shas:
            return

        ui = self.repo.ui
        if len(hg_shas) == 1:
            result_sha = next(iter(hg_shas))
        elif not allow_multiple:
            # taken straight from `headchecking.enforcesinglehead`
            # that is disabled in Heptapod just to avoid calling
            # the expensive _filter_obsolete_heads twice per branch
            msg = _(b'rejecting multiple heads on branch "%s"')
            msg %= branchmap_branch
            hint = _(b'%d heads: %s')
            hint %= (len(hg_shas), util.format_shas(hg_shas))
            raise error.Abort(msg, hint=hint)
        else:
            result_sha = self.multiple_heads_choose(hg_shas, branchmap_branch)
            if result_sha is None:
                ui.error(logprefix,
                         b"Ignoring %r: none of the given heads %r to choose "
                         b"from could be resolved. Either the branchmap entry "
                         b"is corrupted of there is a bug in its Heptapod "
                         b"assessment." % (branchmap_branch, hg_shas))
                # the inconsistency can be on branch/topics that the end
                # user is not pushing, and perhaps much less important than
                # the current push. Do not block them.
                return

            ui.note(logprefix, b"Multiple heads for branch '%s': %r" % (
                branchmap_branch, util.format_bytes_list(hg_shas)))
            for wild_sha in hg_shas:
                gitlab_refs[wild_sha].heads.add(
                    gitlab_branch_ref(b'wild/' + wild_sha))

            ui.note(logprefix,
                    b"Chose %s out of multiple heads %s "
                    b"for forwarding branch %r" % (
                        result_sha, util.format_bytes_list(hg_shas),
                        branchmap_branch))

        gitlab_refs[result_sha].heads.add(gitlab_branch_ref(gitlab_branch))

    def multiple_heads_choose(self, hg_shas, branchmap_branch):
        """Choose among multiple heads to forward the given branch

        The branch is given in branchmap format, i.e., `branch:topic` or
        `branch`.

        :returns: a Mercurial changeset SHA, in hexadecimal form, or
           ``None`` if nothing satisfactory has been found.

        Currently, we arbitrarily take the one with the highest revision
        number (hence the most recently added to *this* repository).
        The advantage is that the given branch will never disappear
        (confusing to users, and leading to some blocking situations,
        such as heptapod#101).

        This is consistent with what Mercurial does for label-adressing,
        and shouldn't be a problem for Heptapod, since we force-push to
        Git all the time.

        Because the caller typically passes already known SHAs, a ``None``
        return value is to be taken as a data inconsistency.
        """
        if not hg_shas:
            self.repo.ui.warn(b"multiple_heads_choose called with empty "
                              b"set of heads.")
            return

        repo = self.repo
        try:
            rev = repo.revs(b'max(%ls)', hg_shas).first()
        except error.RepoLookupError:
            return None
        return repo[rev].hex()

    def validate_obsolescence(self, txn):
        """Abort if the given transaction creates unwanted obsolescence.

        Most GitLab refs must not be to obsolete changesets, but we don't
        want to create blocking situations for repos with long history
        where this may already be the case.

        See heptapod#393

        We are at the end of the transaction, hence we can assume that
        consequences of new obsmarkers have already been applied (e.g, moving
        a bookmark if possible)
        """
        repo = self.repo
        unfi = self.repo.unfiltered()
        for new_obsmarker in txn.changes[b'obsmarkers']:
            try:
                obsolete_ctx = unfi[new_obsmarker[0]]
            except error.RepoLookupError:
                continue
            bookmarks = obsolete_ctx.bookmarks()
            if bookmarks:
                hint = _(b"If this isn't a mistake, you may need to also "
                         b"update the bookmark(s).")
                msg = _(b"Refusing these changes, as they would make "
                        b"bookmark(s) %s point to the "
                        b"obsolete changeset %s") % (
                            util.format_bytes_list(bookmarks),
                            obsolete_ctx.hex())
                raise error.Abort(msg, hint=hint)

            # performance note: repo.tags() seems to be expensive, but is
            # heavily cached, and also called at the very end anyway.
            # Also the cases here are exceptional
            tags = [t for t in obsolete_ctx.tags()
                    if unfi.tagtype(t) == b'global'
                    and repo.tags().get(t) == obsolete_ctx.node()
                    ]

            if tags:
                # TODO explain why this two-step
                hint = _(b"If this isn't a mistake, you may need to also "
                         b"update the tag(s).")
                msg = _(b"Refusing these changes, as they would make "
                        b"tag(s) %s point to the "
                        b"obsolete changeset %s") % (
                            util.format_bytes_list(tags),
                            obsolete_ctx.hex())

                raise error.Abort(msg, hint=hint)

    def generate_prune_changes(self, to_prune, existing):
        """Generate those pruning GitLab changes that really have to be done.

        :return: a complete list of `HeadPruneReason` instances and
                 a `dict` mapping GitLab refs to the corresponding
                 :class:`GitLabRefChange` instances.

        In a further version, we may get rid of the :class:`GitLabRefChange`
        instances. For now, they would help adding the prune reason logic
        to the GitLab side with minimal disruption.
        """
        changes = {}
        prune_reasons = {}
        prune_previously_closed_branches = self.repo.ui.configbool(
            b'experimental', b'hg-git.prune-previously-closed-branches')
        for gitlab_branch, reason in pycompat.iteritems(to_prune):
            ref = gitlab_branch_ref(gitlab_branch)
            before_sha = existing.get(ref)
            if before_sha is None:
                continue
            if reason == 'closed':
                reason = self.analyse_closed_branch(
                    gitlab_branch, before_sha,
                    prune_previously_closed=prune_previously_closed_branches)
                if reason is None:
                    continue
            changes[ref] = GitLabRefChange(ref=ref,
                                           before=before_sha,
                                           after=ZERO_SHA)
            prune_reasons[gitlab_branch] = reason
        return prune_reasons, changes

    def prune_topic_with_sha(self, reason_cls, branch, topic, hg_sha):
        """Generate a `reason_cls` instance with the GitLab sha for `hg_sha`
        """
        gitlab_sha = self.gitlab_sha_from_hg_sha(hg_sha)
        if gitlab_sha is None:
            # TODO when we won't convert to Git any more, not
            # saying anything to GitLab won't be an option.
            self.repo.ui.warn(
                b"Analysis of topic '%s' for branch '%s' "
                b"that becomes invisible in this transaction "
                b"to report its latest change to GitLab "
                b"found Mercurial changeset %s that has no known "
                b"Git counterpart. Giving up on reporting "
                b"that topic/branch combination to GitLab." % (
                    topic, branch, hg_sha))
            return None
        else:
            return reason_cls(gitlab_sha)

    def prune_closed_branch(self, branch):
        """Generate a `BranchClosed` instance with the wished details.

        See :class:`BranchClosed` for description of the expected details.
        """
        repo = self.repo
        txn = repo.currenttransaction()
        info = []
        orig_repolen = txn.changes[b'origrepolen']
        if orig_repolen >= len(self.repo):
            # it's possible that closing is due to no new changeset:
            # - publication of an existing closing changeset
            # - more indirect cases, such as pruning the only not closed head
            # TODO try and treat some of these cases
            return BranchClosed([])

        for new_closing_rev in self.repo.revs(
                b'%d: and branch(%s) and closed()',
                txn.changes[b'origrepolen'], branch):
            ctx = repo[new_closing_rev]
            parents = []
            for parent_ctx in ctx.parents():
                git_sha = self.gitlab_sha_from_hg_sha(parent_ctx.hex())
                if git_sha is not None:
                    parents.append(git_sha)
            info.append((self.gitlab_sha_from_hg_sha(ctx.hex()), parents))
        return BranchClosed(info)

    def analyse_vanished_refs(self, existing, exportable):
        """Decide what to do of existing Git refs that aren't in exportable.

        All will have to be pruned on the GitLab side, this methods tells
        why.

        :return: dict mapping refs to :class:`HeadPruneReason` instances
        """
        to_prune = {}
        exported_refs = {ref for heads_tags in exportable.values()
                         for ref in heads_tags}
        for ref, before_gitlab_sha in pycompat.iteritems(existing):
            if ref in exported_refs:
                continue

            gitlab_branch = gitlab_branch_from_ref(ref)
            if gitlab_branch is None:
                continue

            if ref.startswith(b'refs/heads/wild/'):
                to_prune[gitlab_branch] = WildHeadResolved(before_gitlab_sha)
            try:
                branch_topic = parse_gitlab_branch(gitlab_branch)
            except InvalidGitLabBranch:
                self.repo.ui.warn(b"Git mirror repo has a bogus branch "
                                  b"ref '%s' "
                                  b"that's not among the exportable ones. "
                                  b"Ignoring it." % ref)
                continue
            if branch_topic is not None and branch_topic[1]:
                branch, topic = branch_topic
                before_hg_sha = self.hg_sha_from_gitlab_sha(before_gitlab_sha)
                prune_reason = self.analyse_vanished_topic(
                    branch, topic, before_hg_sha,
                    log_info={b'ref': ref,
                              b'before_gitlab_sha': before_gitlab_sha},
                )
                if prune_reason is not None:
                    to_prune[gitlab_branch] = prune_reason

        return to_prune

    def analyse_closed_branch(self, gitlab_branch, before_sha,
                              prune_previously_closed=True):
        """Decide whether to prune and provide details.

        :param before_sha: GitLab SHA for latest known head of the branch.
        :return: `None` to avoid pruning, or a :class:`HeadPruneReason` with
                 all expected details.
        """
        hg_branch = parse_gitlab_branch(gitlab_branch)[0]
        self.repo.ui.note(b'Considering prune of branch %r' % hg_branch)
        if prune_previously_closed:
            return BranchClosed()

        before_hg_sha = self.hg_sha_from_gitlab_sha(before_sha)

        # In cases we can't find the Mercurial changeset for the latest known
        # GitLab SHA, we can't really know if the closing is new,
        # but being unknown to Mercurial, it certainly has to be pruned.
        if before_hg_sha is None:
            self.repo.ui.warn(
                b"Pruning closed branch '%s' previous Git sha has no "
                b"known Mercurial counterpart." % gitlab_branch
            )
            return BranchClosed()

        try:
            before_ctx = self.repo[before_hg_sha]
        except error.RepoLookupError:
            self.repo.ui.warn(
                b"Pruning closed branch '%s', whose "
                b"latest Git commit %r corresponds to the unknown "
                b"%s hg sha" % (gitlab_branch, before_sha, before_hg_sha))
            return BranchClosed()

        if before_ctx.closesbranch() and not prune_previously_closed:
            return None

        try:
            return self.prune_closed_branch(hg_branch)
        except Exception:
            ui = self.repo.ui
            ui.traceback()
            ui.warn(b"Could not determine the closing changeset for "
                    b"GitLab branch %r. If the closing changeset was part of "
                    b"a Merge Request, this may result in staleness or wrong "
                    b"status of the Merge Request" % gitlab_branch)
            return BranchClosed()

    def analyse_vanished_topic(self, branch, topic, before_sha,
                               log_info):
        """Compute revision to send GitLab as new topic branch head.

        :param before_sha: Mercurial SHA for the current Git head of the topic
                           GitLab branch. Can be ``None`` if the Git head is
                           actually unknown to Mercurial.
        :param log_info: dict of useful information for logs that we must
                         restrain not to use for other purposes in this method
                         (typically some Git context).
                         Has to be given with bytes keys because
                         `b'%(key)s' % d` looks for b`key` in `d`
        :return: Mercurial SHA, or ``None`` to trigger pruning.
        """
        logprefix = b'HeptapodGitHandler.topic_new_hg_sha '
        ui = self.repo.ui
        initial_import = ui.configbool(b"heptapod", b"initial-import")
        try:
            # TODO case where before_sha is None. same error treatment?
            before_ctx = self.unfiltered_repo[before_sha]
        except error.RepoLookupError:
            log_info[b'before_sha'] = before_sha
            ui.warn(logprefix, b"GitLab '%(ref)s' "
                    b"(gitlab_sha=%(before_gitlab_sha)s, "
                    b"hg_sha=%(before_sha)s) not "
                    b"found in the Mercurial repo (should be due to "
                    b"some half-rollbacked previous transaction), pruning "
                    b"as the topic does not seem "
                    b"to be visible anymore" % log_info)
            return HeadPruneReason()

        if before_ctx.phase() == phases.public:
            latest_sha = self.published_topic_latest_hg_sha(topic, before_ctx)
            if latest_sha is None:
                # this is a corruption: resolving the Git branch for the topic
                # actually gives us a changeset that does not bear that topic!
                # This is what happened in heptapod#265.
                # In that case, we return it unchanged. The changeset
                # surely is an ancestor of the current named branch head
                # GitLab's MR detection should thus work.
                latest_sha = before_sha
            return self.prune_topic_with_sha(
                TopicPublished, branch, topic, latest_sha)
        try:
            succctx = obsutil.latest_unique_successor(before_ctx)
        except error.Abort as exc:
            if initial_import:
                # we don't want to break an initial import because
                # of an exceptional phase divergence, let's keep it unchanged
                # TODO UPSTREAM evolve gives us a message in str instead
                # of the standard bytes for error.Abort
                ui.warn(logprefix + pycompat.sysbytes(exc.args[0]))
                return HeadPruneReason()
            else:
                raise

        if succctx is None:
            ui.note(logprefix,
                    b"scheduling prune of %(ref)s "
                    b"(obsolete, no successor)" % log_info)
            return HeadPruneReason()

        succ_phase = succctx.phase()
        if succ_phase == phases.public:
            latest_sha = None
            if not initial_import:
                latest_sha = self.published_topic_latest_hg_sha(
                    topic, succctx, log_before_ctx=before_ctx)
            if latest_sha is None:
                return HeadPruneReason()
            return self.prune_topic_with_sha(
                TopicPublished, branch, topic, latest_sha)

        elif succ_phase == phases.draft:
            # let's go over some reasons why there's no visible branch/topic
            # head and the former one is obsolete with a draft successor
            succ_brtop = (succctx.branch(), succctx.topic())
            before_brtop = (before_ctx.branch(), before_ctx.topic())
            if succ_brtop != before_brtop:
                log_info.update({b'before': before_ctx.hex(),
                                 b'succ': succctx.hex()})
                ui.note(logprefix,
                        b"pruning '%(ref)s' (hgsha %(before)s), "
                        b"as its successor %(succ)s "
                        b"is on another branch or topic" % log_info)
                # TODO we may want to refine that one
                return HeadPruneReason()

        return HeadPruneReason()

    def published_topic_latest_hg_sha(self, topic, ctx, log_before_ctx=None):
        """Rewrapping of `latest_topic_descendant` returning hg sha.
        """
        ui = self.repo.ui
        try:
            after_ctx = self.latest_topic_descendant(topic, ctx)
        except MultipleDescendants:
            msg = (b"Found several descendants in topic '%s' of the "
                   b"newly published '%s'. Can't have GitLab add them "
                   b"to any related merge request. ") % (topic, ctx)
            ui.warn(msg)
            ui.status(msg)
            # since successor is public, chances to detect merge are good
            return ctx.hex()

        if after_ctx is None:
            ui.warn(b"HeptapodGitHandler.published_topic_latest_hg_sha "
                    b"inspecting public changeset '%s' for topic '%s' gave "
                    b"inconsistent result: it's not in the expected topic. "
                    b"This will trigger immediate pruning of the "
                    b"topic Git branch" % (ctx, topic))
            return None

        ui.note(b'HeptapodGitHandler.published_topic_latest_hg_sha',
                b"updating published '%s' from '%s' to '%s'" % (
                    topic,
                    log_before_ctx if log_before_ctx is not None else ctx,
                    after_ctx))
        return after_ctx.hex()

    def latest_topic_descendant(self, topic, ctx):
        """Return the latest public descendent of ctx in a given topic.

        Although this is not meaningful in regular Mercurial usage,
        it's necessary because we need GitLab to understand what happened to
        a Merge Request on a published topic, and that's not possible if
        its branch vanished.

        This checks that there is one public head of the topic.
        Otherwise the push should be refused as inconsistent.

        The changeset of ctx is assumed *not* to be filtered (aka, obsolete)
        (all current callers already have obsolescence information around).
        If it does not belong to the topic, `None` gets returned.
        """
        revs = self.repo.revs("heads(extra(topic, %s) and descendants(%d))",
                              topic, ctx.rev())
        if len(revs) > 1:
            raise MultipleDescendants(topic, ctx)
        rev = revs.first()
        if rev is None:
            return None
        return self.repo[rev]

    def compare_exportable(self, existing, exportable):
        """Analyse the exportable refs to produce GitLab changes

        :param exportable: a mapping from Git refs to Mercurial SHAs
        :param existing: a mapping of existing Git refs in the target repo
                         to GitLab SHAs
        :returns: a mapping from Git refs to :class:`GitRefChange` objects
        """
        ui = self.repo.ui
        default_git_branch = self.get_default_gitlab_branch()
        to_prune = exportable.pop(ZERO_SHA, {})
        to_prune.update(self.analyse_vanished_refs(existing, exportable))
        prune_default_branch = to_prune.pop(default_git_branch, None)
        if (
                prune_default_branch
                and default_git_branch.startswith(b'branch/')
        ):
            msg = (b"These changes close or prune the Heptapod default "
                   b"branch '%s'. This is forbidden" % default_git_branch)
            ui.note(msg)
            raise error.Abort(msg)

        if prune_default_branch and branch_is_topic(default_git_branch):
            # we cannot put it back on current Heptapod, because GitLab
            # will refuse at the PreReceive stage (default branch deletion,
            # and even circumventing that is not enough, as it is also
            # protected). At some point we might introduce a new
            # Mercurial-specific message (alongside prune reasons),
            # so that GitLab can understand
            # that it is acceptable with certainty.
            self.ui.status(
                b"These changes should make the current "
                b"default Heptapod branch '%(br)s' disappear. This is "
                b"fine for a topic, as long as a suitable replacement "
                b"can be inferred from them (preferably a long-lasting "
                b"value such as 'branch/default').\n"
                b"However, sometimes the topic does not disappear "
                b"server-side as it should. If that is "
                b"the case, you may need to unprotect %(br)s "
                b"in Settings > Repository > Protected Branches "
                b"and subsequent pushes should finally clean it." % {
                    b'br': default_git_branch}
            )

        prune_reasons, changes = self.generate_prune_changes(to_prune,
                                                             existing)

        for hg_sha, refs in pycompat.iteritems(exportable):
            for ref in refs.heads:
                after_sha = self.gitlab_sha_from_hg_sha(hg_sha)
                before_sha = existing.get(ref, ZERO_SHA)
                if after_sha and after_sha != before_sha:
                    changes[ref] = GitLabRefChange(ref=ref,
                                                   before=before_sha,
                                                   after=after_sha)

        if self.is_wiki() and not self.native:
            # GitLab wikis are much hardwired onto 'master' in a Git repo
            on_default = changes.get(gitlab_branch_ref(b'branch/default'))
            if on_default is not None:
                master = gitlab_branch_ref(b'master')
                changes[master] = GitLabRefChange(ref=master,
                                                  before=on_default.before,
                                                  after=on_default.after)

        return prune_reasons, changes

    def heptapod_compare_tags(self, existing):
        """Derived from hg-git's export_hg_tags() for two-phase application.

        Instead of immediate application to the Git repo, like hg-git does,
        we emit a dict of :class:`GitlabRefChange` instances,
        suitable for application between pre- and post-receive.
        """
        changes = {}
        repo = self.repo

        all_tag_refnames = set()
        for tag, sha in pycompat.iteritems(repo.tags()):
            if repo.tagtype(tag) in (b'global', b'git'):
                tag = tag.replace(b' ', b'_')
                target = self.gitlab_sha_from_hg_sha(hex(sha))
                if target is not None:
                    tag_refname = gitlab_tag_ref(tag)
                    all_tag_refnames.add(tag_refname)
                    if check_ref_format(tag_refname):
                        before_sha = existing.get(tag_refname, ZERO_SHA)
                        if before_sha != target:
                            changes[tag_refname] = GitLabRefChange(
                                ref=tag_refname,
                                before=before_sha,
                                after=target)
                    else:
                        repo.ui.warn(
                            b"Skipping export of Mercurial tag '%s' because "
                            b"it has invalid name as a git refname.\n" % tag)
                else:
                    repo.ui.warn(
                        b"Skipping export of tag '%s' because it "
                        b"has no matching git revision.\n" % tag)

        # for removal, it is important that the comparison happens
        # completely on one side of the mapping (here GitLab)
        # see heptapod#464
        for ref, target in existing.items():
            ref_tag = gitlab_tag_from_ref(ref)
            if ref_tag is not None and ref not in all_tag_refnames:
                changes[ref] = GitLabRefChange(ref=ref,
                                               before=target,
                                               after=ZERO_SHA)

        if changes and not is_user_allowed(repo, 'publish'):
            # better to back convert in exceptional case
            # rather than make more work in above loop on all tags
            abridged = [gitlab_tag_from_ref(refname)
                        for refname in itertools.islice(changes, 0, 4)]
            raise error.Abort(
                b"You don't have sufficient permissions "
                b"to create, modify or delete tags",
                hint=b'Found %d GitLab tags affected by those changes, '
                b'including: %s. '
                b'Note that GitLab tag names can be slightly '
                b'different from the Mercurial tags due to escaping rules' % (
                    len(changes),
                    util.format_bytes_list(abridged)))

        return changes

    def heptapod_notify_gitlab(self, hook, prune_reasons, changes,
                               push_options=None,
                               additional_error_message=b"",
                               allow_error=False):
        if not changes and not prune_reasons:
            return

        ui = self.repo.ui
        native = self.native
        ui.note(b"heptapod_notify_gitlab heptapod.native=%r" % native)

        if native and prune_reasons:
            prune_reasons = {gl_branch: reason.convert_native(self)
                             for gl_branch, reason in prune_reasons.items()}
        try:
            converted_changes = {ref: ch.export_for_hook(self, native=native)
                                 for ref, ch in changes.items()}
        except KeyError as exc:
            ui.error(b"The after Git SHA %r has no Mercurial "
                     b"counterpart" % exc.args)
            raise error.Abort("Inconsistency in internal conversion")

        # a verbose log line that will help with issues such as heptapod#278
        ui.note(pycompat.sysbytes(
            "heptapod_notify_gitlab firing hook %r "
            "for changes %r" % (hook, (prune_reasons, converted_changes))))

        payload = [prune_reasons, converted_changes]
        if push_options is not None:
            payload.append(push_options)
        try:
            code, out, err = hook(tuple(payload))
        except Exception as exc:
            ui.error(pycompat.sysbytes(
                "GitLab update error (%s): %r\n%s" % (
                    hook, exc, traceback.format_exc())))
            if allow_error:
                # that's an error in py-heptapod, could be a network failure
                # once we call the internal API directly, for instance
                return
            else:
                raise

        if code != 0:
            # bytes conversion for hg ui methods and exceptions
            err = pycompat.sysbytes(err)
            ui.error(b"Got code %s while sending GitLab '%s' "
                     b"hook details=%s" % (
                         pycompat.sysbytes(repr(code)), hook, err))
            quiet = ui.quiet
            ui.quiet = False
            msg = b"GitLab update error: '%s', %s" % (err,
                                                      additional_error_message)
            ui.status(msg)
            ui.quiet = quiet
            if not allow_error:
                raise hook.error_cls(err.strip())

        # useful messages such as motd, merge requests links etc.
        quiet = ui.quiet
        ui.quiet = False
        # out is already given as bytes, that was the point of much
        # of the py3 conversion for the Hook class
        ui.status(out)
        ui.quiet = quiet

    def extract_hg_convert_refs(self, ref_name_parser, refs, fallback=None):
        """Generator emitting typed ref names and hg targets from given refs.

        :param refs: a :class:`dict`, or any object with a ``as_dict()``
           method, mapping full ref paths to GitLab SHAs targets.
        :param ref_name_parser: relevant callable that returns a short typed
           ref name (e.g., `branch/default` for branches), or ``None`` if
           a given ref is not of the appropriate type.
        :param fallback: control what happens if a GitLab SHA cannot be
           converted to a Mercurial SHA. Possible values are:
           - ``None``: the ref is skipped
           - ``REF_TARGET_PASS_THROUGH``: the input SHA is emitted
           - ``REF_TARGET_UNKNOWN_RAISE``: raises ``LookupError(GitLab SHA)``.
        :returns: iterator of (typed name ref, Mercurial SHA target) pairs.
           The Mercurial SHA can be ``None`` if the GitLab SHA is unknown. It
           is then up to the caller to decide what to do.
        """
        if not isinstance(refs, dict):
            refs = refs.as_dict()
        for ref, sha in refs.items():
            name = ref_name_parser(ref)
            if name is None:
                continue

            hg_sha = self.hg_sha_from_gitlab_sha(sha)
            if hg_sha is None:
                if fallback is None:
                    continue
                elif fallback is REF_TARGET_PASS_THROUGH:
                    yield name, sha
                elif fallback is REF_TARGET_UNKNOWN_RAISE:
                    raise LookupError(sha)

            yield name, hg_sha

    def gitlab_branches_hg_shas(self, refs):
        """Extracts GitLab branches from refs and ensure SHAs are Mercurial.

        This is useful to store the GitLab branches state file for Mercurial
        native repos.

        Non branch refs are just ignored.
        """
        return {name: hg_sha
                for name, hg_sha in self.extract_hg_convert_refs(
                    gitlab_branch_from_ref, refs)
                }

    def gitlab_tags_hg_shas(self, refs):
        """Extracts GitLab tags from refs and ensure SHAs are Mercurial.

        This is useful to store the GitLab tags state file for Mercurial
        native repos.

        Non tag refs are just ignored.
        """
        return {name: hg_sha
                for name, hg_sha in self.extract_hg_convert_refs(
                    gitlab_tag_from_ref, refs)
                }

    def gitlab_special_refs_hg_shas(self, refs):
        """Extracts GitLab special refs from refs convering SHAs to Mercurial

        This is useful to store the GitLab special refs state
        file for Mercurial native repos.

        Other refs are just ignored.
        """
        return {name: hg_sha
                for name, hg_sha in self.extract_hg_convert_refs(
                    parse_special_ref, refs)
                }

    def gitlab_keep_arounds(self, refs):
        return {hg_sha for _sha, hg_sha in self.extract_hg_convert_refs(
            parse_keep_around_ref, refs)
        }

    def update_gitlab_references(self):
        """Update or create refs in the target storage for Mercurial changes.

        This is either a Git repo in the hg-git case or simply the
        GitLab branches state file for native Mercurial projects.

        This fires or schedules all appropriate notifications (GitLab hooks)
        """
        existing = self.gitlab_refs
        if not isinstance(existing, dict):
            existing = existing.as_dict()
        changes = self.heptapod_compare_tags(existing)
        prune_reasons, compared = self.compare_exportable(
            existing, self.extract_all_gitlab_refs())
        if None in compared:
            self.ui.warn(
                b"A `None` key found its way in compare_exportable results "
                b"Full values: prune_reasons=%r, compared=%r" % (
                    prune_reasons, compared))
        changes.update(compared)
        self.heptapod_apply_changes(prune_reasons, changes)

    def heptapod_apply_changes(self, prune_reasons, changes):
        self.heptapod_notify_gitlab(PreReceive(self.repo),
                                    prune_reasons, changes)
        gitlab_refs = self.gitlab_refs
        for change in pycompat.itervalues(changes):
            if change.after == ZERO_SHA:
                del gitlab_refs[change.ref]
            else:
                gitlab_refs[change.ref] = change.after
        self.update_default_gitlab_branch(changes)
        write_gitlab_branches(self.repo,
                              self.gitlab_branches_hg_shas(self.gitlab_refs))
        write_gitlab_tags(self.repo,
                          self.gitlab_tags_hg_shas(self.gitlab_refs))

        def post_receive(push_opts=None):
            self.heptapod_notify_gitlab(
                PostReceive(self.repo),
                prune_reasons, changes,
                additional_error_message=(
                    b"Because of this, some changes may not be visible "
                    b"in the interface, and some expected server-side actions "
                    b"may not have been triggered."),
                push_options=push_opts if push_opts else None)

        txn = self.repo.currenttransaction()
        if txn is None:
            post_receive(None)
        else:
            push_opts = extract_push_options(txn)
            self.repo._afterlock(
                lambda success: post_receive(push_opts=push_opts))

    def is_filtered(self, sha):
        hg_sha = self.hg_sha_from_gitlab_sha(sha)
        try:
            self.repo[hg_sha]
        except error.FilteredRepoLookupError:
            return True
        return False

    def update_default_gitlab_branch(self, changes):
        """Update GitLab default branch if needed

        :param changes: changes of GitLab refs currently being applied

        Right after repo creation, HEAD is typically initialized
        as refs/heads/master, which doesn't exist,
        and probably won't after our push. If we don't correct it
        quickly, something on the GitLab side, even
        before post-receive treatment actually begins will set it to
        a random value - we don't want it to select topics if possible
        and if it previously has, we want that to change.
        """
        default_ref = self.get_default_gitlab_ref()
        default_exists = default_ref in self.gitlab_refs
        if default_exists and not ref_is_topic(default_ref):
            return

        # The default GitLab branch might not have been set on Wikis
        # when they went native, see heptapod#1987. For Wikis, the choice
        # is always 'branch/default'.
        branch_default_ref = gitlab_branch_ref(b'branch/default')
        if default_ref is None and self.is_wiki() and self.native:
            change = changes.get(branch_default_ref)
            exists = branch_default_ref in self.gitlab_refs
            if change is not None:
                # mutating boolean clearer than very long condition in `if`
                exists &= not change.is_deletion()
                exists |= change.is_creation()
            if exists:
                self.set_default_gitlab_ref(branch_default_ref)
                return

        new_named_branch_refs = set()
        fallback_new_refs = set()
        for ref, change in pycompat.iteritems(changes):
            if not change.is_creation():
                continue
            if ref_is_named_branch(ref):
                new_named_branch_refs.add(ref)
            elif not ref_is_wild_branch(ref):
                fallback_new_refs.add(ref)

        self.ui.note(
            b"Analysis to set default branch. "
            b"Named branch candidates: %r, fallback_new_refs: %r" % (
                new_named_branch_refs, fallback_new_refs))
        candidate_refs = new_named_branch_refs or fallback_new_refs
        if not candidate_refs:
            if self.is_filtered(self.gitlab_refs[default_ref]):
                raise error.Abort(
                    b"These changes would obsolete the current "
                    b"Heptapod default branch '%s' "
                    b"(given here as GitLab full ref path)."
                    b"and provide no new suitable replacement." % default_ref,
                    hint=b"To secure your repository for Heptapod, "
                    b"consider pushing a public changeset first, even if "
                    b"almost empty; `hg push -r` can help to avoid pushing "
                    b"unwanted ones at the same time."
                )
            return

        if branch_default_ref in candidate_refs:
            new_default_ref = branch_default_ref
        else:
            new_default_ref = candidate_refs.pop()

        if ref_is_topic(new_default_ref):
            topic = gitlab_branch_from_ref(new_default_ref)
            self.ui.status(
                b"WARNING: this repository does not have a long-lasting "
                b"Heptapod branch yet!\n"
                b"WARNING: Setting temporarily '%s' as Heptapod default "
                b"branch.\n"
                b"WARNING: This state is not recommended: "
                b"it can lead to severe problems, such as"
                b"https://foss.heptapod.net/"
                b"heptapod/heptapod/-/issues/1716\n"
                b"RECOMMENDATION: please consider pushing a public changeset "
                b"soon to get off this unhealthy condition. "
                b"The content of the changeset does not matter as long "
                b"as it is public. For example, "
                b"an almost empty `.hgignore` would be be enough.\n" % topic
            )
            if default_exists:
                if self.is_filtered(self.gitlab_refs[default_ref]):
                    self.ui.warn(b"Default ref %r still in `gitlab_refs` "
                                 b"but is obsolete\n" % default_ref)
                else:
                    # No need to further endanger the repo, by changing
                    # default branch to another topic or rewrite the
                    # same value. GitLab is not
                    # designed for default branch changing at each push
                    return
        else:
            # wild branches are already excluded above. The remaining
            # possibilities are bookmarks and named branches.
            branch = gitlab_branch_from_ref(new_default_ref)
            self.ui.status(
                b"Setting '%s' as Heptapod default branch.\n"
                b"This can be changed if needed in "
                b"Settings > Repositoy > Branch Defaults\n"
                b"Note: the Heptapod branch is automatically protected, "
                b"users may want to unprotect the former Heptapod "
                b"default branch after changing it\n." % branch
            )
        self.set_default_gitlab_ref(new_default_ref)


def extract_push_options(transaction):
    PUSH_VAR_PREFIX = b'USERVAR_'
    prefix_len = len(PUSH_VAR_PREFIX)
    encoding = cli_encoding.decode()
    return {k[prefix_len:].decode(encoding).lower(): v.decode(encoding)
            for k, v in transaction.hookargs.items()
            if k.startswith(PUSH_VAR_PREFIX)
            }
