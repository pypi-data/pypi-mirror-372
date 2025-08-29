# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from base64 import b64decode
import logging
import os
import time

from grpc import StatusCode

from mercurial import (
    cmdutil,
    commands,
    node,
    scmutil,
)

from heptapod import (
    obsutil,
)

from heptapod.gitlab.branch import (
    NAMED_BRANCH_PREFIX,
    parse_gitlab_branch,
)

from ..branch import (
    gitlab_branch_head
)
from ..changelog import (
    ancestor,
    merge_content,
)
from ..errors import (
    operation_error_treatment,
    structured_abort,
)
from ..logging import LoggerAdapter
from ..revision import (
    changeset_by_commit_id_abort,
    gitlab_revision_changeset,
    validate_oid,
    ZERO_SHA,
)
from ..servicer import HGitalyServicer

from ..stub.operations_pb2 import (
    OperationBranchUpdate,
    UserCommitFilesActionHeader,
    UserCommitFilesError,
    UserCommitFilesRequest,
    UserCommitFilesResponse,
    UserFFBranchError,
    UserFFBranchRequest,
    UserFFBranchResponse,
    UserSquashRequest,
    UserSquashResponse,
    UserSquashError,
)
from ..stub.errors_pb2 import (
    IndexError,
    ReferenceUpdateError,
    ResolveRevisionError,
)
from ..stub.operations_pb2_grpc import OperationServiceServicer


base_logger = logging.getLogger(__name__)
ActionType = UserCommitFilesActionHeader.ActionType


DOUBLE_SLASH = b'//'
DOUBLE_PARSEP = (os.path.sep * 2).encode()  # in case it's not double slash
DIRECTORY_CLIMB_UP = (os.path.pardir + os.path.sep).encode()

FORBIDDEN_IN_PATHS = tuple(set((DOUBLE_SLASH,
                                DOUBLE_PARSEP,
                                DIRECTORY_CLIMB_UP,
                                )))


def index_error(context, status_code, error_type, msg, path=b''):
    """Abort with IndexError structued error.

    :param str status_code: name of the gRPC status code
    :param str error_type: name of the IndexError type enum
    """
    structured_abort(
        context,
        getattr(StatusCode, status_code),
        msg,
        UserCommitFilesError(
            index_update=IndexError(
                error_type=getattr(IndexError.ErrorType, error_type),
                path=path
            )
        )
    )


class OperationServicer(OperationServiceServicer, HGitalyServicer):
    """OperationsServiceService implementation.
    """

    def UserSquash(self,
                   request: UserSquashRequest,
                   context) -> UserSquashResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')
        # Gitaly's squash is merge-centric, start_sha is actually the
        # merge target, whereas end_sha is the head of the MR being accepted
        # TODO check that there are no public changesets for a nicer
        # user feedback.
        start_sha, end_sha = request.start_sha, request.end_sha
        if not start_sha:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty StartSha")
        if not end_sha:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty EndSha")
        start_rev, end_rev = start_sha.encode('ascii'), end_sha.encode('ascii')
        start_ctx = gitlab_revision_changeset(repo, start_rev)
        end_ctx = gitlab_revision_changeset(repo, end_rev)

        for (ctx, rev, error_label) in (
                (start_ctx, start_rev, 'start'), (end_ctx, end_rev, 'end')
        ):
            if ctx is None:
                structured_abort(
                    context,
                    StatusCode.INVALID_ARGUMENT,
                    f'resolving {error_label} revision: reference not found',
                    UserSquashError(resolve_revision=ResolveRevisionError(
                        revision=rev))
                )

        revset = (f"ancestor({start_sha}, {end_sha})::{end_sha}"
                  f"- ancestor({start_sha}, {end_sha})").encode('ascii')
        end_ctx = gitlab_revision_changeset(repo, end_sha.encode('ascii'))
        logger.info("Folding revset %s, mirroring to Git=%r",
                    revset, with_hg_git)
        # TODO add the hg_git flag or maybe let servicer do it.
        message = request.commit_message
        if not message:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty CommitMessage")

        # Mercurial does not distinguish between author (actual author of
        # the work) and committer (could be just someone with commit rights
        # relaying the original work). In case an author is provided, it
        # feels right to derive the Mercurial author from it, as preserving
        # the actual work metadata (and copyright) should have priority.
        # This is what `HgGitRepository` used to do on the Rails side.
        author = request.author
        if not author.name:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty Author")

        # timestamp is supposed to be for the committer, but Mercurial does
        # not have such a distinction, hence it will become the commit date.
        if not request.HasField('timestamp'):
            unix_ts = int(time.time())
        else:
            unix_ts = request.timestamp.seconds

        opts = {'from': False,  # cannot be used as regular kwarg
                'exact': True,
                'rev': [revset],
                'message': message,
                'user': b'%s <%s>' % (author.name, author.email),
                'date': b'%d 0' % unix_ts,
                }
        # Comment taken from `hg_git_repository.rb`:
        #   Note that `hg fold --exact` will fail unless the revset is
        #   "an unbroken linear chain". That fits the idea of a Merge Request
        #   neatly, and should be unsuprising to users: it's natural to expect
        #   squashes to stay simple.
        #   In particular, if there's a merge of a side topic, it will be
        #   unsquashable.
        # Not 100% sure we need a workdir, but I don't see
        #   an explicit "inmemory" option as there is for `hg rebase`. What
        #   I do see is user (status) messages as in updates, so…
        # If we update the workdir to "end" changeset, then the fold will
        #   look like an extra head and be rejected (probably because it is
        #   kept active by being the workdir parent).
        #   On the other hand, the "start" changeset is by design of the
        #   method not to be folded and is probably close enough that we
        #   get a reasonable average efficiency.
        with self.working_dir(gl_repo=request.repository,
                              repo=repo,
                              changeset=start_ctx,
                              context=context) as wd:
            # `allowunstable=no` protects us against all instabilities,
            # in particular against orphaning dependent topics.
            # TODO this setting should probably be set in all mutations
            wd.repo.ui.setconfig(b'experimental.evolution', b'allowunstable',
                                 False)
            with operation_error_treatment(context, UserSquashError,
                                           logger=logger):
                retcode = self.repo_command(wd.repo, context, 'fold', **opts)
                if retcode == 1:
                    revs = wd.repo.revs(revset)
                    if len(revs) == 1:
                        rev = next(iter(revs))
                        self.repo_command(wd.repo, context, 'update', rev)
                        self.repo_command(
                            wd.repo, context, 'amend',
                            message=message,
                            note=(b"Description changed for squash request "
                                  b"for a single changeset"),
                        )
                    else:  # pragma no cover
                        # This block is currently unreachable from tests
                        # and is here in case of unexpected behaviour change
                        # in the `fold` command.
                        context.abort(
                            StatusCode.INTERNAL,
                            "Internal return code 1, but zero or more than "
                            "one changeset for revset %r" % revset
                        )
            self.repo_command(wd.repo, context, 'update', start_ctx.hex())
            # The workdir repo does not have to be reloaded, whereas the
            # main repo would. We just need to regrab the end changeset
            # (now obsolete)
            end_ctx = wd.repo.unfiltered()[end_ctx.rev()]
            folded = obsutil.latest_unique_successor(end_ctx)

        return UserSquashResponse(squash_sha=folded.hex().decode('ascii'))

    def UserFFBranch(self,
                     request: UserFFBranchRequest,
                     context) -> UserFFBranchResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')

        to_publish = changeset_by_commit_id_abort(
            repo, request.commit_id, context)
        if to_publish is None:
            context.abort(
                StatusCode.INTERNAL,
                f'checking for ancestry: invalid commit: "{request.commit_id}"'
            )

        old_id = request.expected_old_oid
        if old_id and not validate_oid(old_id):
            context.abort(StatusCode.INVALID_ARGUMENT,
                          f'cannot parse commit ID: "{old_id}"')

        if not request.branch:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty branch name")

        if not request.branch.startswith(NAMED_BRANCH_PREFIX):
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "Heptapod fast forwards are currently "
                          "for named branches only (no topics nor bookmarks)")

        current_head = gitlab_branch_head(repo, request.branch)
        if to_publish.branch() != current_head.branch():
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "not a fast-forward (Mercurial branch differs)")

        fail = False
        for cs in merge_content(to_publish, current_head):
            if cs.obsolete():
                fail = True
                fail_msg = "is obsolete"
            if cs.isunstable():
                fail = True
                fail_msg = "is unstable"
        if fail:
            context.abort(StatusCode.FAILED_PRECONDITION,
                          f"not a fast-forward (changeset "
                          f"{cs.hex().decode('ascii')} {fail_msg})")

        if old_id and old_id != current_head.hex().decode('ascii'):
            # We did not need to resolve before this, but now we do because
            # Gitaly has a specific error if resolution fails
            if changeset_by_commit_id_abort(repo, old_id, context) is None:
                context.abort(StatusCode.INVALID_ARGUMENT,
                              "cannot resolve expected old object ID: "
                              "reference not found")
            # no point trying to match the Gitaly error details: we
            # have the much better structured error
            structured_abort(context,
                             StatusCode.FAILED_PRECONDITION,
                             "expected_old_oid mismatch",
                             UserFFBranchError(
                                 reference_update=ReferenceUpdateError(
                                     # Gitaly doesn't fill in `reference_name`
                                     old_oid=old_id,
                                     new_oid=to_publish.hex().decode('ascii'),
                                 )))

        if ancestor(to_publish, current_head) != current_head.rev():
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "not fast forward")

        # TODO use phases.advanceboundary directly? Check cache invalidations
        # carefully. ('phases' command is a pain to call and does lots of
        # unnecessary stuff).
        logger.info("All checks passed, now publishing %r, "
                    "mirroring to Git=%r", to_publish, with_hg_git)
        self.publish(to_publish, context)
        return UserFFBranchResponse(branch_update=OperationBranchUpdate(
            commit_id=to_publish.hex().decode('ascii'),
        ))

    def UserCommitFiles(self,
                        request: UserCommitFilesRequest,
                        context) -> UserCommitFilesResponse:
        logger = LoggerAdapter(base_logger, context)
        first_req = next(request)
        if not first_req.HasField('header'):
            context.abort(
                StatusCode.INVALID_ARGUMENT,
                "empty UserCommitFilesRequestHeader"
            )
        commit_header = first_req.header
        grpc_repo = commit_header.repository
        repo = self.load_repo(grpc_repo, context,
                              for_mutation_by=commit_header.user)
        repo_created = branch_created = False

        gl_branch = commit_header.branch_name
        if not gl_branch:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "empty BranchName")

        start_sha = commit_header.start_sha
        if start_sha:
            start_rev = start_sha.encode('ascii')
        elif commit_header.start_branch_name:
            start_rev = commit_header.start_branch_name
        else:
            start_rev = gl_branch

        parsed = parse_gitlab_branch(gl_branch)
        if parsed is None:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "Only named branches and topics are supported "
                          "(not bookmarks in particular)")
        hg_branch, topic = parsed
        to_publish = (topic is None
                      and repo.ui.configbool(b'experimental',
                                             b'topic.publish-bare-branch'))

        old_oid = commit_header.expected_old_oid.encode('ascii')
        start_ctx = gitlab_revision_changeset(repo, start_rev)
        if start_ctx is None:
            if len(repo) > 0 and old_oid != ZERO_SHA:
                context.abort(StatusCode.INTERNAL,
                              "Unresolvable start ref or commit")
            else:
                repo_created = branch_created = True
        # now that sanity checks are done, we can normalize to null
        # changeset if needed.
        if start_ctx is None and old_oid == ZERO_SHA:
            start_ctx = repo[ZERO_SHA]
        if commit_header.branch_name:
            old_oid = commit_header.expected_old_oid.encode('ascii')
            if old_oid and start_ctx.hex() != old_oid:
                context.abort(StatusCode.INVALID_ARGUMENT,
                              "wrong old oid")

        if to_publish and self.heptapod_permission != 'publish':
            context.abort(
                StatusCode.PERMISSION_DENIED,
                "insufficient permissions for publication",
            )

        topic_cmd = cmdutil.findcmd(b'topics', commands.table)[1][0]
        with self.working_dir(gl_repo=grpc_repo,
                              repo=repo,
                              changeset=start_ctx,
                              context=context) as wd:
            ui = wd.repo.ui
            # TODO should be set for all mutations
            ui.setconfig(b'experimental.evolution', b'allowunstable', False)

            logger.info("Preparing commit in working directory %s", wd.path)
            if start_ctx is None or start_ctx.branch() != hg_branch:
                logger.debug("Setting Mercurial branch to %r", hg_branch)
                wd.repo.dirstate.setbranch(hg_branch, None)
                branch_created = True
            if topic is not None and (start_ctx is None
                                      or start_ctx.topic() != topic):
                logger.debug("Setting topic to %r", topic)
                topic_cmd(ui, wd.repo, topic)
                branch_created = True

            content_handler = None
            changed_files = set()
            for req in request:
                if not req.HasField('action'):
                    context.abort(
                        StatusCode.INTERNAL,  # See Comparison Test
                        "unhandled action payload type: <nil>"
                    )
                action = req.action
                if action.HasField('content'):
                    if content_handler is None:
                        context.abort(
                            StatusCode.INTERNAL,  # See Comparison Test
                            "content sent before action"
                        )
                    else:
                        logger.debug("UserCommitFiles content=%r",
                                     action.content)
                        content_handler.write(action.content)
                elif action.HasField('header'):
                    logger.info("UserCommitFiles action header: %r",
                                action.header)
                    if content_handler is not None:
                        content_handler.close()
                        content_handler = None
                    header = action.header
                    UserCommitFilesAction(
                        context=context,
                        header=header,
                        working_dir=wd,
                        changed_files=changed_files,
                    )()

                    if header.action in (ActionType.CREATE,
                                         ActionType.UPDATE):
                        content_handler = UserCommitFilesContent(
                            context, wd, header
                        )
                    else:
                        content_handler = None

            if content_handler is not None:
                content_handler.close()

            def do_commit(ui, repo, message, match, opts):
                commit_user = b'%s <%s>' % (
                    commit_header.commit_author_name,
                    commit_header.commit_author_email
                )
                return repo.commit(message,
                                   commit_user,
                                   (time.time(), 0),
                                   match=match,
                                   editor=False,
                                   extra=None,
                                   )

            logger.info("Performing commit")
            with wd.repo.wlock(), wd.repo.lock():
                try:
                    new_node = cmdutil.commit(
                        ui, wd.repo, do_commit,
                        changed_files,
                        {b'addremove': True,
                         b'message': commit_header.commit_message}
                    )
                    if to_publish and new_node is not None:
                        logger.info("Commit done, now publishing (no topic)")
                        self.publish(wd.repo[new_node], context)
                except Exception as exc:
                    msg = str(exc)
                    code = StatusCode.INTERNAL
                    if 'multiple heads' in msg:  # shame but not much better
                        code = StatusCode.INVALID_ARGUMENT
                        context.abort(code, msg)

        if new_node is None:
            return UserCommitFilesResponse()

        return UserCommitFilesResponse(
            branch_update=OperationBranchUpdate(
                commit_id=node.hex(new_node).decode('ascii'),
                repo_created=repo_created,
                branch_created=branch_created,
            )
        )


def validate_checkout_path(context, relpath):
    # absolute paths are interpreted by Gitaly as relative to the
    # root of checkout.
    relpath = relpath.lstrip(b'/')

    for p in FORBIDDEN_IN_PATHS:
        if p in relpath:
            relpath_str = relpath.decode('utf-8', 'surrogateescape')

            if p == DIRECTORY_CLIMB_UP:
                # ill-named by upstream
                error_type = 'ERROR_TYPE_DIRECTORY_TRAVERSAL'
                msg = 'Path cannot include directory traversal'
            else:
                error_type = 'ERROR_TYPE_INVALID_PATH'
                msg = f'invalid path: "{relpath_str}"'

            index_error(context,
                        status_code='INVALID_ARGUMENT',
                        error_type=error_type,
                        msg=msg,
                        path=relpath)
    return relpath


class UserCommitFilesAction:

    def __init__(self, context, header, working_dir, changed_files):
        self.context = context
        self.header = header
        self.changed_files = changed_files

        wd = self.working_dir = working_dir
        self.relpath = validate_checkout_path(context, header.file_path)
        self.abspath = wd.file_path(self.relpath)

    def __call__(self):
        action = self.header.action
        if action == ActionType.CREATE:
            return self.create()
        elif action == ActionType.CREATE_DIR:
            return self.create_dir()
        elif action == ActionType.UPDATE:
            return self.update()
        elif action == ActionType.MOVE:
            return self.move()
        elif action == ActionType.DELETE:
            return self.delete()
        elif action == ActionType.CHMOD:
            return self.chmod()

    def create(self):
        if os.path.exists(self.abspath):
            index_error(
                self.context,
                status_code='ALREADY_EXISTS',
                error_type='ERROR_TYPE_FILE_EXISTS',
                msg="A file with this name already exists",
                path=self.relpath,
            )
        # Gitaly does this as well
        os.makedirs(os.path.dirname(self.abspath), exist_ok=True)
        self.changed_files.add(self.abspath)
        # actual creation to be done by content handler opening the file

    def require_file_existence(self, abspath=None, relpath=None):
        if abspath is None:
            abspath = self.abspath
            relpath = self.relpath

        if not os.path.exists(abspath):
            index_error(
                self.context,
                status_code='NOT_FOUND',
                error_type='ERROR_TYPE_FILE_NOT_FOUND',
                msg="A file with this name doesn't exist",
                path=relpath
            )

    def require_file_absence(self, abspath=None, relpath=None):
        if abspath is None:
            abspath = self.abspath
            relpath = self.relpath

        if os.path.exists(abspath):
            if os.path.isdir(abspath):
                error_type = 'ERROR_TYPE_DIRECTORY_EXISTS'
                kind = "directory"
            else:
                error_type = 'ERROR_TYPE_FILE_EXISTS'
                kind = "file"
            index_error(
                self.context,
                status_code='ALREADY_EXISTS',
                error_type=error_type,
                msg=f"A {kind} with this name already exists",
                path=relpath,
            )

    def update(self):
        self.require_file_existence()
        self.changed_files.add(self.abspath)
        # writing to be done by content handler

    def create_dir(self):
        """Create a directory by putting an empty file in it."""
        self.require_file_absence()
        abspath = self.abspath

        os.makedirs(abspath, exist_ok=False)
        keep = os.path.join(abspath, b'.hgkeep')
        open(keep, 'ab').close()
        self.changed_files.add(keep)

    def move(self):
        self.require_file_absence()
        abspath = self.abspath
        prev_relpath = validate_checkout_path(self.context,
                                              self.header.previous_path)
        prev_abspath = self.working_dir.file_path(prev_relpath)
        self.require_file_existence(abspath=prev_abspath,
                                    relpath=prev_relpath)

        repo = self.working_dir.repo
        with repo.wlock(), repo.dirstate.changing_files(repo):
            cmdutil.copy(repo.ui, repo, [prev_abspath, abspath],
                         opts={}, rename=True)
        self.changed_files.add(prev_abspath)
        self.changed_files.add(abspath)

    def delete(self):
        self.require_file_existence()

        repo = self.working_dir.repo
        with repo.wlock(), repo.dirstate.changing_files(repo):
            m = scmutil.match(repo[None], [self.abspath], {})
            uipathfn = scmutil.getuipathfn(repo,
                                           legacyrelativevalue=True)
            cmdutil.remove(repo.ui, repo, m,
                           prefix=b"", uipathfn=uipathfn,
                           after=False, force=False,
                           subrepos=None, dryrun=False,
                           )
        self.changed_files.add(self.abspath)

    def chmod(self):
        self.require_file_existence()
        set_hg_executable(self.abspath, self.header.execute_filemode)
        self.changed_files.add(self.abspath)


class UserCommitFilesContent:

    def __init__(self, context, workdir, header):
        relpath = validate_checkout_path(context, header.file_path)
        self.file_path = workdir.file_path(relpath)
        self.fobj = open(self.file_path, 'wb')
        self.make_hg_executable = (header.action == ActionType.CREATE
                                   and header.execute_filemode)
        self.base64 = header.base64_content

    def close(self):
        self.fobj.close()
        if self.make_hg_executable:
            set_hg_executable(self.file_path, True)

    def write(self, content):
        if self.base64:
            content = b64decode(content)
        self.fobj.write(content)


def set_hg_executable(path, executable):
    # only the executable bit is actually tracked by Mercurial
    os.chmod(path, 0o700 if executable else 0o600)
