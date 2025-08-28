# Copyright 2019 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Server side Heptapod extension.

This extension should enclose all Mercurial modifications and commands
needed for Heptapod server operations.
"""

from base64 import b64encode, b64decode
import botocore
import collections
import json

from hgext import clonebundles
from io import BytesIO
from mercurial.i18n import _
from mercurial import (
    bundlecaches,
    cmdutil,
    commands,
    config,
    demandimport,
    error,
    exthelper,
    extensions,
    exchange,
    pycompat,
    registrar,
    scmutil,
    subrepo,
    ui as uimod,
    util,
)
from mercurial.utils import procutil
import os
import sys
import tarfile

from heptapod import (
    obsutil,
)
from heptapod import clone_bundles as hpd_clone_bundles
from heptapod.clone_bundles import BUCKET_URL_PREFIX
from . import (
    topic as topicmod,
    git,
    no_git,
)
from .branch import DEFAULT_GITLAB_BRANCH_FILE_NAME

clonebundles.__doc__  # force actual import

ASYNC_HEPTAPOD_CLONE_BUNDLE_GENERATE = b'hpd::generate-specified-clone-bundle'

# these have conditional imports and subsequent `None` testing in
# (urllib3 and/or requests). In other words, hgdemandimport breaks `requests`
demandimport.IGNORES.update([
    'brotli',
    'simplejson',
    # used in JWT token generation. With `demandimport`, we get errors such as
    #  ValueError: module object for
    #  'cryptography.hazmat.primitives.asymmetric.types' substituted
    #  in sys.modules during a lazy load
    'cryptography.hazmat.primitives.asymmetric.types',
    'cryptography.hazmat.primitives.ciphers.algorithms',
])

try:
    from hgext3rd import hggit
    # forcing demandimport to import it
    hggit.__doc__  # pragma no cover
except ImportError:  # pragma no cover (fallback for hg-git < 0.11)
    try:
        import hggit
        hggit.__doc__
    except ImportError:
        hggit = None

eh = exthelper.exthelper()

if util.safehasattr(registrar, 'configitem'):

    configtable = {}
    configitem = registrar.configitem(configtable)
    configitem(b'heptapod', b'repositories-root')
    configitem(b'heptapod', b'gitlab-shell')
    configitem(b'heptapod', b'mirror-path')
    # Strips all bookmarks exchange by lying about peer capabilities
    configitem(b'heptapod', b'exchange-ignore-bookmarks', False)

    # The following items affect other config items recognized by the core
    # or by extensions. The default value should be inert, i.e., would not
    # change anything, in particular would not revert to Heptapod defaults
    # (as in `required.hgrc`) what local configuration or command-line options
    # say.
    configitem(b'heptapod', b'initial-import', False)
    configitem(b'heptapod', b'allow-multiple-heads')
    configitem(b'heptapod', b'allow-bookmarks')
    configitem(b'heptapod', b'native', False)
    configitem(b'heptapod', b'clone-bundles.s3.tls', True)
    configitem(b'heptapod', b'clone-bundles.s3.endpoint', b'')
    configitem(b'heptapod', b'clone-bundles.s3.bucket', b'')
    configitem(b'heptapod', b'clone-bundles.s3.access_key', b'')
    configitem(b'heptapod', b'clone-bundles.s3.secret_key', b'')
    configitem(b'heptapod', b'clone-bundles.s3.region', b'')
    configitem(b'heptapod', b'clone-bundles.s3.public.with-acl', False)
    configitem(b'heptapod', b'clone-bundles.s3.private.url-expiry-seconds',
               7200)

cmdtable = {}
command = registrar.command(cmdtable)

# alias that used to be a compatibility wrapper (and is revivable)
wrap_function = extensions.wrapfunction


def uipopulate(ui):
    if ui.configbool(b'heptapod', b'initial-import'):
        ui.note(b'hgext3rd.heptapod',
                b"setting config options for initial import")
        ui.setconfig(b'heptapod', b'allow-multiple-heads', True)
        ui.setconfig(b'experimental',
                     b'topic.publish-bare-branch', False)
        ui.setconfig(b'experimental',
                     b'hg-git.bookmarks-on-named-branches', True)
        ui.setconfig(b'experimental', b'hg-git.accept-slash-in-topic-name',
                     True)
        ui.setconfig(b'hggit', b'heptapod.initial-import', True)

    if ui.configbool(b'heptapod', b'allow-bookmarks'):
        ui.setconfig(b'experimental',
                     b'hg-git.bookmarks-on-named-branches', True)

    auto_publish = ui.config(b'heptapod', b'auto-publish')
    if auto_publish is not None:
        auto_publish = auto_publish.lower()
    if auto_publish == b'nothing':
        ui.setconfig(b'experimental', b'topic.publish-bare-branch', False)
    elif auto_publish == b'all':
        ui.setconfig(b'phases', b'publish', True)

    clone_bundles = ui.config(b'heptapod', b'clone-bundles')
    if clone_bundles is not None:
        clone_bundles = clone_bundles.lower()
        if clone_bundles in (b'disabled', b'explicit'):
            ui.setconfig(b'clone-bundles', b'auto-generate.on-change', False)
        elif clone_bundles == b'on-change':
            ui.setconfig(b'clone-bundles', b'auto-generate.on-change', True)

    # here it would be tempting to use pop() but this is called twice
    # for each `hg` invocation, and apparently the default is reapplied between
    # the two calls.
    env_native = ui.environ.get(b'HEPTAPOD_HG_NATIVE', None)
    if env_native is not None:
        ui.setconfig(b'heptapod', b'native', env_native)


@command(
    b"pull-force-topic",
    [(b'f', b'force', None,
      _(b'run even when remote repository is unrelated')),
     (b'r', b'rev', [], _(b'a remote changeset intended to be imported'),
      _(b'REV')),
     ] + cmdutil.remoteopts,
    _(b'[-r] [-f] TARGET_TOPIC')
)
def pull_force_topic(ui, repo, topic, source=b"default",
                     force=False, **opts):
    """Pull changesets from remote, forcing them to drafts with given topic.

    This is intended to import pull requests from an external system, such
    as Bitbucket. In many case, the changesets to import would have been
    made in a private fork, and could be public, most commonly shadowing the
    default branch.

    TARGET_TOPIC is the topic to set on the pulled changesets
    """
    pull_rev = opts.get('rev')
    logged_revs = b'' if pull_rev is None else b' [%s]' % b', '.join(pull_rev)
    ui.status(b"Pulling%s from '%s', forcing new changesets to drafts with "
              b"topic %s\n" % (logged_revs, source, topic))
    topic = topic.strip()
    if not topic:
        raise error.Abort(
            _(b"topic name cannot consist entirely of whitespace"))
    scmutil.checknewlabel(repo, topic, b'topic')
    return topicmod.pull_force(ui, repo, source, pull_rev, topic,
                               force=force, **opts)


@command(b'gitlab-mirror')
def gitlab_mirror(ui, repo):
    """Export changesets as Git commits in the GitLab repository."""
    if ui.configbool(b'heptapod', b'native'):
        repo.ui.note(b'GitLab sync without Git export')
        no_git.NoGitStateMaintainer(ui, repo).sync()
    else:
        repo.ui.note(b'GitLab sync with Git export')
        git.HeptapodGitHandler(repo, repo.ui).export_commits()


@command(b'move-hg-git-repo-out-of-gitaly-reach')
def move_hg_git_repo_out_of_gitaly_reach(ui, repo):
    """Export changesets as Git commits in the GitLab repository."""
    if not ui.configbool(b'heptapod', b'native'):
        raise error.Abort(b"This should not be run on a repository based "
                          b"on hg-git: the point is to expose them to Gitaly")

    handler = git.HeptapodGitHandler(repo, repo.ui)
    handler.native_project_ensure_set_git_dir()
    return 0


@command(b'hpd-ensure-gitlab-branches')
def ensure_gitlab_branches(ui, repo):
    """Ensure that GitLab branches state file is present.

    If present, nothing happens.
    If not, it is initialized from the auxiliary Git repository.

    See py-heptapod#8

    :returns: ``None` if the file was already present. Otherwise,
       new :class:`dict` of branches.
    """
    return git.HeptapodGitHandler(repo, ui).ensure_gitlab_branches()


@command(b'hpd-ensure-gitlab-default-branch')
def ensure_gitlab_default_branch(ui, repo):
    """Ensure that GitLab default branch file is present.

    If present, nothing happens.
    If not, it is initialized from the auxiliary Git repository.

    :returns: ``None` if the file was already present. Otherwise,
       new Gitlab default branch :class:`bytes`.
    """
    return git.HeptapodGitHandler(repo, ui).ensure_gitlab_default_branch()


@command(b'hpd-ensure-gitlab-tags')
def ensure_gitlab_tags(ui, repo):
    """Ensure that GitLab tags state file is present.

    If present, nothing happens.
    If not, it is initialized from the auxiliary Git repository.

    See py-heptapod#8

    :returns: ``None` if the file was already present. Otherwise,
       new :class:`dict` of tags.
    """
    return git.HeptapodGitHandler(repo, ui).ensure_gitlab_tags()


@command(b'hpd-ensure-gitlab-special-refs')
def ensure_gitlab_special_refs(ui, repo):
    """Ensure that GitLab special refs state file is present.

    If present, nothing happens.
    If not, it is initialized from the auxiliary Git repository.

    See heptapod#431

    :returns: ``None` if the file was already present. Otherwise,
       new :class:`dict` of special refs.
    """
    return git.HeptapodGitHandler(repo, ui).ensure_gitlab_special_refs()


@command(b'hpd-ensure-gitlab-keep-arounds')
def ensure_gitlab_keep_arounds(ui, repo):
    """Ensure that GitLab keep-arounds state file is present.

    If present, nothing happens.
    If not, it is initialized from the auxiliary Git repository.

    See heptapod#431

    :returns: ``None` if the file was already present. Otherwise,
       :class:`set` of new keep-arounds.
    """
    return git.HeptapodGitHandler(repo, ui).ensure_gitlab_keep_arounds()


@command(
    b'hpd-ensure-all-gitlab-specific-state-files'
    b'|hpd-ensure-all-gitlab-refs'
)
def ensure_all_gitlab_specific_state_files(ui, repo):
    """Ensure that all ref files are present.

    Equivalent to calling ``ensure-gitlab-branches``, ``ensure-gitlab-tags``
    etc.
    """
    ensure_gitlab_branches(ui, repo)
    ensure_gitlab_tags(ui, repo)
    ensure_gitlab_special_refs(ui, repo)
    ensure_gitlab_keep_arounds(ui, repo)
    ensure_gitlab_default_branch(ui, repo)


@command(b'hpd-unique-successor',
         [(b'r', b'rev', b'', _(b'specified revision'), _(b'REV')),
          ])
def unique_successor(ui, repo, rev=None, **opts):
    """Display the node ID of the obsolescence successor of REV if unique.

    This can be useful after a simple rebase or fold, as a direct way to
    find the resulting changeset.

    If REV isn't obsolete, the output is REV.
    If there is any divergence, the command will fail.

    The same functionality can be accomplished with
    ``hg log -T {successorsets}`` but the latter

    1. won't fail on divergence
    2. will present as with ``{rev}:{node|short}``, making a second ``hg log``
       call necessary to get the full hash.

    In the context of the Rails app 1) could be almost acceptable by
    detecting multiple results and refusing them (that's already some parsing),
    but together with 2) that's too much, we'll have a
    better robustness with this simple, fully tested command.

    See also: https://foss.heptapod.net/mercurial/evolve/issues/13
    """
    if not rev:
        raise error.Abort(_(b"Please specify a revision"))
    # rev would typically be an obsolete revision, we need to see them
    ctx = scmutil.revsingle(repo.unfiltered(), rev)
    succ_ctx = obsutil.latest_unique_successor(ctx)
    ui.write(succ_ctx.hex())


@command(b'hpd-versions',
         [],
         norepo=True,
         intents={registrar.INTENT_READONLY},
         )
def versions(ui):
    """Output most relevant version information as JSON.

    The provided versions are those we deemed to be of interest for
    the Rails application:
    Python, Mercurial, important extensions.
    """
    py_tuple = tuple(sys.version_info)[:3]
    sysstr = pycompat.sysstr
    versions = dict(python='.'.join(str(i) for i in py_tuple),
                    mercurial=sysstr(util.version()),
                    )
    all_exts = {sysstr(name): sysstr(extensions.moduleversion(module))
                for name, module in extensions.extensions()}
    for ext in ('evolve', 'topic', 'hggit'):
        versions[ext] = all_exts.get(ext)
    ui.write(pycompat.sysbytes(json.dumps(versions)))


@command(b'hpd-backup-additional', [], _(b'OUTPUT_PATH'))
def backup_additional(ui, repo, output_path):
    """Produce a tar file with everything needing backup and not in bundle.

    The result is a plain, uncompressed tar at the given OUTPUT_PATH. The
    file format is totally independent from the file name.
    """
    with tarfile.open(output_path, 'w') as tarf:
        def add_file(fpath):
            relpath = os.fsdecode(os.path.relpath(fpath, repo.path))
            print(relpath)
            tarf.add(fpath, arcname=relpath)

        # locking, as we will be reading only but we need a consistent state
        # ideally should be also consistent with the bundle, but that's
        # something we can improve on later (GitLab locks the project anyway
        # when its backup starts TODO recheck that).
        with repo.wlock(), repo.lock():
            vfs, svfs = repo.vfs, repo.svfs
            vfs_file_names = [
                DEFAULT_GITLAB_BRANCH_FILE_NAME,
                git.HeptapodGitHandler.map_file,
            ]
            vfs_file_names.extend(fname for fname in vfs.listdir()
                                  if fname.startswith(b'hgrc'))

            for fname in vfs_file_names:
                fpath = vfs.join(fname)
                if not os.path.exists(fpath):
                    # can happen, e.g, for default branch file on empty repo
                    continue
                add_file(fpath)
            for fname in svfs.listdir():
                if fname.startswith(b'gitlab.'):
                    add_file(svfs.join(fname))


@command(b'hpd-restore-additional', [], _(b'ADDITIONAL_BACKUP_PATH'))
def restore_additional(ui, repo, additional_backup_path):
    """Restore from a tar file produced by hpd-backup-additional.
    """
    with repo.wlock(), repo.lock():
        with tarfile.open(additional_backup_path) as tarf:
            for mname in tarf.getnames():
                if mname.startswith('/') or '..' in mname:
                    raise error.Abort(
                        b"Prohibited member '%s' in tar file at '%s'" % (
                            os.fsencode(mname), additional_backup_path))
            tarf.extractall(os.fsdecode(repo.path))


@command(b'hpd-git-resync|hpd-export-native-to-git', [], )
def git_resync(ui, repo):
    """Silently resynchronize the Git repo.

    This command is applicable for Projects in which the Mercurial
    content (including its refs) is the reference for the
    Rails application yet still need to use the Git repository.

    It converts all missing changesets to Git and resets the Git references
    from the GitLab state files in the Mercurial repository, without firing
    any Git hook.

    No permissions are involved: all the refs changes are already presented
    by the Mercurial repository.

    The main use case used to be to switch back a Project to hg-git after it
    has been migrated to native.
    Nowadays, it is to update converted Git repositories that are being used
    for remote pushes.
    """
    handler = git.HeptapodGitHandler(repo, repo.ui)
    with repo.wlock(), repo.lock():
        handler.native_project_ensure_set_git_dir()
        handler.export_git_objects()
        handler.save_map(handler.map_file)
        handler.force_git_refs_from_gitlab_files()


@command(
    b'hpd-clone-bundles-refresh',
    [
        (b'', b'project-namespace-full-path', b'',
         b'Full Heptapod applicative path of the namespace of the project',
         ),
        (b'', b'public', False,
         b'Whether the repository is public (can be anonymously cloned)',
         ),
    ],
    b'',
)
def clone_bundles_refresh(ui, repo,
                          project_namespace_full_path=None,
                          public=False):
    """Refresh clone bundles and put them in appropriate storage
    """
    # We would need a proper gRPC call to provide correct user feedback
    if ui.config(b'heptapod', b'clone-bundles') == b'disabled':
        repo.ui.note(
            b"Clone bundles are disabled by config for this repository")
        return

    refresh = cmdutil.findcmd(b'admin::clone-bundles-refresh',
                              commands.table)[1][0]
    environ = repo.ui.environ
    ns_path = project_namespace_full_path
    if ns_path:
        environ[b'HEPTAPOD_PROJECT_NAMESPACE_FULL_PATH'] = ns_path
    if public:
        environ[b'HEPTAPOD_PUBLIC_REPOSITORY'] = b'true'

    # see heptapod#2082: obsolescence markers in clone bundles are
    # actually harmful for some clients.
    overrides = {
        (b'experimental', b'evolution.bundle-obsmarker'): False
    }
    with repo.ui.configoverride(overrides):
        refresh(ui, repo)


def runsystem(orig, ui, cmd, environ, cwd, out):
    heptapod_env = {k: v for k, v in ui.environ.items()
                    if k.startswith(b'HEPTAPOD_')}
    if environ is None:
        environ = heptapod_env
    else:
        heptapod_env.update(environ)
    return orig(ui, cmd, environ=heptapod_env, cwd=cwd, out=out)


wrap_function(uimod.ui, '_runsystem', runsystem)


def hggit_parse_hgsub(orig, lines):
    """A more robust version of .hgsub parser

    See heptapod#310 for an example where the conversion to Git fails
    because of the ``[subpaths]`` section.

    This version simply uses the general Mercurial config parser, as
    is done in :func:`mercurial.subrepoutil.state` and reconverts to
    to :class:`ordereddict.OrderedDict`. A previous version used
    direct access of the parse result, but these were complemented with
    unwanted details (for us) in Mercurial 5.8.
    """
    parsed = config.config()
    parsed.parse(b'.hgsub', b"\n".join(lines))
    return collections.OrderedDict(parsed.items(b''))


if hggit is not None:
    wrap_function(hggit.util, 'parse_hgsub', hggit_parse_hgsub)


def forbid_subrepo_get(orig, *args, **kwargs):
    raise error.Abort(b"Updating subrepos on the server side is "
                      b"not supported in this version of Heptapod and "
                      b"would be actually harmful. "
                      b"This may be reenabled in a subsequent version.")


def bookmarks_op_override(orig, op, *args, **kwargs):
    '''Wrap command to never pull/push bookmarks'''

    ui = op.repo.ui
    ignore_bookmarks = ui.configbool(b"heptapod", b"exchange-ignore-bookmarks")
    if not ignore_bookmarks:
        return orig(op, *args, **kwargs)
    # Not sure how important this is, but it's done in the original function
    # for the pushop in case of early return
    op.stepsdone.add(b'bookmarks')


wrap_function(subrepo.hgsubrepo, 'get', forbid_subrepo_get)
wrap_function(subrepo.gitsubrepo, 'get', forbid_subrepo_get)
wrap_function(subrepo.svnsubrepo, 'get', forbid_subrepo_get)


def async_generate_clone_bundle(orig, repo, bundle):
    """We need to pass over HGRCPATH and the variables from WSGI env.

    :param bundle: a `RequestedBundle` object.

    Aside from the environment variables (main reason), this override
    is also trimmed down for simplicity to avoid useless user feedback:
    given that Heptapod manages everything, it is pointless writing
    back to the client. Server logs should be preferred.
    """
    src_env = repo.ui.environ
    data = util.pickle.dumps(bundle)

    env = procutil.shellenviron()

    hgrc_path = src_env.get(b'HEPTAPOD_HGRC')
    if hgrc_path is not None:
        # typical of WSGI environment, hence we need to forward to process
        # environment. TODO use one of the wsgi_ vars for detection
        env[b'HGRCPATH'] = hgrc_path
        env.update((k, v) for k, v in src_env.items()
                   if k.startswith(b'HEPTAPOD_'))
        env[b'GL_REPOSITORY'] = src_env[b'GL_REPOSITORY']

    env[b'HEPTAPOD_HG_BUNDLE_SPEC'] = b64encode(data)
    # TODO use the HG environment variable if available, like
    # procutil.hgexecutable() does
    hg = os.path.join(os.path.dirname(sys.executable), 'hg')
    cmd = [os.fsencode(hg),
           b'--cwd', repo.path,
           ASYNC_HEPTAPOD_CLONE_BUNDLE_GENERATE]

    repo.ui.note(b"clone-bundles: starting async bundle generation, "
                 b"type: %r, cmd=%r\n" % (bundle.bundle_type, cmd))
    procutil.runbgcommand(cmd, env)


@command(ASYNC_HEPTAPOD_CLONE_BUNDLE_GENERATE, [], b'')
def async_clone_bundle_generate_subprocess(ui, repo):
    # this is meant to be run in a detached child process and be its
    # only duty so we do not hesitate to savagely patch procutil
    # we need to restore it in tests though, because they do not run
    # this in a subprocess
    orig_stdin = procutil.stdin
    bundle_data = ui.environ[b'HEPTAPOD_HG_BUNDLE_SPEC']
    procutil.stdin = BytesIO(b64decode(bundle_data))
    refresh = cmdutil.findcmd(clonebundles.INTERNAL_CMD,
                              commands.table)[1][0]
    # see heptapod#2082: obsolescence markers in clone bundles are
    # actually harmful for some clients.
    repo.ui.setconfig(b'experimental', b'evolution.bundle-obsmarker', False)
    try:
        return refresh(ui, repo)
    finally:
        procutil.stdin = orig_stdin


def clone_bundle_s3_details(repo, basename):
    """return everything needed"""
    env = repo.ui.environ
    # separating public and private base URLs should help keeping access
    # rights simple and secure, especially to avoid discoverabiliy issues.
    # We will also set permissions at the bucket level, hence have
    # a separate bucket for private clone bundles.
    # It also allows more offloading for public URLs, since we wil
    # typically have private clone bundles go through Workhorse.
    # TODO something to accept true, ok, yes etc?
    public = env.get(b'HEPTAPOD_PUBLIC_REPOSITORY') == b'true'
    ns_full_path = env.get(b'HEPTAPOD_PROJECT_NAMESPACE_FULL_PATH')
    gl_repo = env.get(b'GL_REPOSITORY')

    bucket_rpath = b'/'.join((ns_full_path, gl_repo, basename))
    client, bucket = hpd_clone_bundles.s3_client_bucket(repo, public=public)
    return client, public, bucket, bucket_rpath


def upload_clone_bundle(orig, repo, bundle):
    """Perform the upload directly with the relevant method for Heptapod.

    The clonebundles extension provides the option to use an external
    command, but that is very cumbersome in our context:

    We would need to either make it – very atrtificially a Mercurial
    command or generate it each time in a temptoary file (persisting it
    is a very bad idea, as it will depend on things that can change, such
    as project visibility, etc.
    """
    filepath = bundle.filepath
    basename = repo.vfs.basename(filepath)
    client, public, bucket, bucket_rpath = clone_bundle_s3_details(
        repo, basename)

    pub_acl = public and repo.ui.configbool(
        b'heptapod',
        b'clone-bundles.s3.public.with-acl'
    )

    s3_upload_clone_bundle(client, os.fsdecode(filepath),
                           bucket,
                           bucket_rpath.decode('utf-8'),
                           pub_acl=pub_acl)
    if public:
        base_url = repo.ui.config(b'heptapod',
                                  b'clone-bundles.public-base-url')
        url = b'/'.join((base_url, bucket_rpath))

    else:
        url = BUCKET_URL_PREFIX + bucket_rpath

    return bundle.uploaded(url, basename)


def delete_clone_bundle(orig, repo, bundle):
    """Delete a bundle from the storage used by Heptapod."""
    assert bundle.ready

    client, _pub, bucket, bucket_rpath = clone_bundle_s3_details(
        repo, bundle.basename)
    try:
        client.delete_object(Bucket=bucket, Key=bucket_rpath.decode('utf-8'))
    except botocore.exceptions.ClientError as exc:
        # as stated by doc of the clonebundles extension, removals
        # must not crash if file does not exist. This is stronger,
        # it should be ok.
        repo.ui.warn(b"Error removing clone bundle %r: %r" % (
            bundle.basename,
            exc))


def s3_upload_clone_bundle(client, src_path, bucket, bucket_rpath,
                           pub_acl=False):
    # The bucket policy is assumed to be appropriate: anonymous
    # readonly for public repos, completely closed for private repos
    # (the latter not implemented yet as of this writing)
    extra = {}
    if pub_acl:
        extra['ACL'] = 'public-read'
    client.upload_file(src_path, bucket, bucket_rpath, ExtraArgs=extra)


def alter_bundle_url(orig, repo, url):
    client, bucket = hpd_clone_bundles.s3_client_bucket(repo)

    prefix = BUCKET_URL_PREFIX
    if url.startswith(prefix):
        bucket_rpath = url[len(prefix):].decode('utf-8')
        return client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': bucket_rpath},
            ExpiresIn=repo.ui.configint(
                b'heptapod',
                b'clone-bundles.s3.private.url-expiry-seconds'
            ),
        ).encode('ascii')
    else:
        return url


def extsetup(ui):
    """Tweaks after all extensions went though their `uisetup`

    hgext3rd.heptapod is meant to be terminal, the only (debatable)
    exception being HGitaly, which could well adopt the whole of `heptapod`
    and `hgext3rd.heptapod` in the future.
    """
    wrap_function(exchange, '_pullbookmarks', bookmarks_op_override)
    wrap_function(exchange, '_pushbookmark', bookmarks_op_override)
    wrap_function(exchange, '_pushb2bookmarkspart', bookmarks_op_override)
    wrap_function(clonebundles, 'upload_bundle', upload_clone_bundle)
    wrap_function(clonebundles, 'delete_bundle', delete_clone_bundle)
    wrap_function(clonebundles, 'start_one_bundle',
                  async_generate_clone_bundle)
    wrap_function(bundlecaches, 'alter_bundle_url', alter_bundle_url)
