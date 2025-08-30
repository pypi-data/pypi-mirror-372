# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import StatusCode
import logging
import os
import time

from mercurial.merge import merge
from mercurial.mergestate import mergestate
from mercurial.node import nullhex as NULL_NODE_HEX
from mercurial.phases import (
    public as PUBLIC,
)
from mercurial import util as hgutil

from heptapod.gitlab.branch import (
    NAMED_BRANCH_PREFIX,
    gitlab_branch_ref,
)

from .. import message
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
)
from ..workdir import (
    ClientMismatch,
    reserve_prepare_workdir,
    release_workdir_by_id,
)
from ..stub.errors_pb2 import (
    MergeConflictError,
    ReferenceUpdateError,
)
from ..stub.mercurial_operations_pb2 import (
    CensorRequest,
    CensorResponse,
    MercurialPermissions,
    MergeAnalysisRequest,
    MergeAnalysisResponse,
    MergeBranchError,
    MergeBranchRequest,
    MergeBranchResponse,
    PreCheckUpdateError,
    PublishChangesetError,
    PublishChangesetRequest,
    PublishChangesetResponse,
    ReleaseWorkingDirectoryRequest,
    ReleaseWorkingDirectoryResponse,
    GetWorkingDirectoryRequest,
    GetWorkingDirectoryResponse,
)
from ..stub.mercurial_operations_pb2_grpc import (
    MercurialOperationsServiceServicer,
)
from ..stub.operations_pb2 import (
    OperationBranchUpdate,
)
from ..stub.shared_pb2 import (
    User,
)
from ..servicer import HGitalyServicer

base_logger = logging.getLogger(__name__)

MERCURIAL_VERSION = hgutil.versiontuple()
MERGE_CONFLICTS_LABELS = [b'working copy', b'merge rev', b'common ancestor']


class ConflictError(RuntimeError):
    """Raised by merge helpers and catched by service method"""


class MercurialOperationsServicer(MercurialOperationsServiceServicer,
                                  HGitalyServicer):
    """MercurialOperationService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def GetWorkingDirectory(self,
                            request: GetWorkingDirectoryRequest,
                            context) -> GetWorkingDirectoryResponse:
        gl_repo = request.repository
        rev = request.revision
        repo = self.load_repo(gl_repo, context)
        workdirs_root = self.repo_workdirs_root(gl_repo, context)
        changeset = gitlab_revision_changeset(repo, rev)
        if changeset is None:
            context.abort(StatusCode.NOT_FOUND, "Revision not found")

        wd = reserve_prepare_workdir(workdirs_root, repo,
                                     client_id=request.client_id,
                                     incarnation_id=request.incarnation_id,
                                     changeset=changeset)
        # TODO wd_rpath should be a method on WorkingDirectory
        repos_root = os.fsdecode(self.storage_root_dir(gl_repo.storage_name,
                                                       context))
        wd_rpath = str(wd.path.relative_to(repos_root))

        return GetWorkingDirectoryResponse(working_directory_id=wd.id,
                                           relative_path=wd_rpath)

    def ReleaseWorkingDirectory(self,
                                request: ReleaseWorkingDirectoryRequest,
                                context) -> ReleaseWorkingDirectoryResponse:
        gl_repo = request.repository
        repo = self.load_repo(gl_repo, context)
        wd_id = request.working_directory_id
        try:
            release_workdir_by_id(repo, wd_id, request.client_id)
        except ClientMismatch:
            context.abort(
                StatusCode.PERMISSION_DENIED,
                f"Not the owner of the lease on working directory {wd_id}"
            )
        return ReleaseWorkingDirectoryResponse()

    def MergeAnalysis(self,
                      request: MergeAnalysisRequest,
                      context) -> MergeAnalysisResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        source_cs = gitlab_revision_changeset(repo, request.source_revision)
        if source_cs is None:
            context.abort(
                StatusCode.INVALID_ARGUMENT,
                "Source revision %r not found" % request.source_revision)
        target_cs = gitlab_revision_changeset(repo, request.target_revision)
        if target_cs is None:
            context.abort(
                StatusCode.INVALID_ARGUMENT,
                "Target revision %r not found" % request.target_revision)

        source_branch = source_cs.branch()
        target_branch = target_cs.branch()
        logger.info("Merge Analysis: source branch %r, target branch %r",
                    source_branch, target_branch)
        is_ff = (ancestor(source_cs, target_cs) == target_cs.rev()
                 and source_branch == target_branch)

        has_obsolete = has_unstable = False
        for cs in merge_content(source_cs, target_cs):
            if not has_obsolete:
                has_obsolete = cs.obsolete()
            if not has_unstable:
                has_unstable = cs.isunstable()
            if has_obsolete and has_unstable:
                break

        has_conflicts = False
        if not (is_ff
                or has_obsolete or has_unstable
                or request.skip_conflicts_check):
            with self.working_dir(gl_repo=request.repository,
                                  repo=repo,
                                  context=context,
                                  changeset=target_cs) as wd:
                has_conflicts = not wd_merge(wd, source_cs)

        res = MergeAnalysisResponse(
            is_fast_forward=is_ff,
            has_obsolete_changesets=has_obsolete,
            has_unstable_changesets=has_unstable,
            has_conflicts=has_conflicts,
            target_is_public=target_cs.phase() == PUBLIC,
            target_node_id=target_cs.hex().decode('ascii'),
            target_branch=target_cs.branch(),
            target_topic=target_cs.topic(),
            source_node_id=source_cs.hex().decode('ascii'),
            source_branch=source_cs.branch(),
            source_topic=source_cs.topic(),
        )
        logger.info("MergeAnalysis result %r", message.Logging(res))
        return res

    def PublishChangeset(self,
                         request: PublishChangesetRequest,
                         context) -> PublishChangesetResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')

        gl_rev = request.gitlab_revision
        if not gl_rev:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty gitlab_revision")

        to_publish = gitlab_revision_changeset(repo, request.gitlab_revision)
        if to_publish is None:
            context.abort(
                StatusCode.INVALID_ARGUMENT,
                f"could not resolve revision {repr(request.gitlab_revision)}"
            )

        # TODO PermissionDenied, then
        if request.hg_perms < MercurialPermissions.PUBLISH:
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "Publish permission not passed")

        logger.info("publishing %r, mirroring to Git=%r", to_publish,
                    with_hg_git)

        with operation_error_treatment(context, PublishChangesetError,
                                       logger=logger):
            self.repo_command(repo, context, 'phase',
                              public=True,
                              draft=False,
                              secret=False,
                              force=False,
                              rev=[str(to_publish.rev()).encode('ascii')])
        return PublishChangesetResponse()

    def Censor(self, request: CensorRequest, context) -> CensorResponse:
        # censor won't even change a hash, still let's follow the usual
        # procedure, in case there turned out to be a side effect
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        node_id = request.changeset_node_id
        changeset = changeset_by_commit_id_abort(repo, node_id, context)
        if changeset is None:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          f"Changeset {node_id} not found")
        # it is essential that the censored file is not checked out.
        # normally, the repository should already be at the null revision,
        # but let's be really sure:
        self.repo_command(repo, context, 'update', NULL_NODE_HEX)

        if MERCURIAL_VERSION >= (6, 7):
            rev_arg = [changeset.rev()]  # hg>=6.7
        else:
            rev_arg = changeset.hex()  # hg<6.7

        self.repo_command(repo, context, 'censor',
                          b'/'.join((repo.root, request.file_path)),
                          rev=rev_arg,
                          tombstone=request.tombstone)
        return CensorResponse()

    def MergeBranch(self,
                    request: MergeBranchRequest,
                    context) -> MergeBranchResponse:
        logger = LoggerAdapter(base_logger, context)

        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')

        target_branch = request.branch
        if not target_branch:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty branch name")
        if not target_branch.startswith(NAMED_BRANCH_PREFIX):
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "Heptapod merges are currently targeting "
                          "named branches only (no topics nor bookmarks)")

        if request.hg_perms < MercurialPermissions.PUBLISH:
            context.abort(StatusCode.PERMISSION_DENIED,
                          "Publish permission not passed")

        if not request.message:
            # would not be necessary if we turn out to fast-forward
            # but that cannot be known by the caller in advance
            context.abort(StatusCode.INVALID_ARGUMENT, "empty message")

        to_merge = changeset_by_commit_id_abort(
            repo, request.commit_id, context)
        if to_merge is None:
            context.abort(
                StatusCode.INTERNAL,
                f'checking for ancestry: invalid commit: "{request.commit_id}"'
            )

        old_id = request.expected_old_oid
        if old_id and not validate_oid(old_id):
            context.abort(StatusCode.INVALID_ARGUMENT,
                          f'cannot parse commit ID: "{old_id}"')

        current_head = gitlab_branch_head(repo, request.branch)
        # TODO mutualize as a check_obsolete_instability()
        # or check_publishable()
        for cs in merge_content(to_merge, current_head):
            if cs.obsolete():
                abort_pre_check_changeset(
                    context, cs,
                    cause=PreCheckUpdateError.OBSOLETE_CHANGESET,
                    error_cls=MergeBranchError
                )
            if cs.isunstable():
                abort_pre_check_changeset(
                    context, cs,
                    cause=PreCheckUpdateError.UNSTABLE_CHANGESET,
                    error_cls=MergeBranchError
                )

        current_head_id = current_head.hex().decode('ascii')
        if old_id and old_id != current_head_id:
            # We did not need to resolve before this, but now we do because
            # Gitaly has a specific error if resolution fails
            if changeset_by_commit_id_abort(repo, old_id, context) is None:
                context.abort(StatusCode.INVALID_ARGUMENT,
                              "cannot resolve expected old object ID: "
                              "reference not found")
            structured_abort(
                context,
                StatusCode.FAILED_PRECONDITION,
                "reference update: reference does not point to "
                "expected object",
                MergeBranchError(
                    reference_check=ReferenceUpdateError(
                        reference_name=gitlab_branch_ref(request.branch),
                        old_oid=old_id,
                        # Gitaly would set `new_oid` to the just created
                        # merge commit id. We cannot do that, let's put
                        # something potentially useful
                        new_oid=current_head_id,
                    )))

        same_branch = to_merge.branch() == current_head.branch()
        linear = ancestor(to_merge, current_head) == current_head.rev()
        if same_branch and linear and not request.semi_linear:
            # fast-forwardable!
            logger.info("This is actually a fast-forward, all checks "
                        "passed, now publishing %r, mirroring to Git=%r",
                        to_merge, with_hg_git)
            self.publish(to_merge, context)
            return MergeBranchResponse(
                branch_update=OperationBranchUpdate(
                    commit_id=to_merge.hex().decode('ascii'),
                ))
        elif request.semi_linear and not linear:
            structured_abort(
                context, StatusCode.FAILED_PRECONDITION,
                "Not fast-forwardable",
                MergeBranchError(
                    pre_check=PreCheckUpdateError.NOT_FAST_FORWARD)
            )

        # actual merge
        with self.working_dir(gl_repo=request.repository,
                              repo=repo,
                              changeset=current_head,
                              context=context) as wd:
            # `allowunstable=no` protects us against all instabilities,
            # in particular against orphaning dependent topics.
            # TODO this setting should probably be set in all mutations
            wd.repo.ui.setconfig(b'experimental.evolution', b'allowunstable',
                                 False)
            # allowing so-called oedipian merge (for semi-linear use case)
            wd.repo.ui.setconfig(b'experimental', b'topic.linear-merge',
                                 b'allow-from-bare-branch')
            if not request.HasField('timestamp'):
                unix_ts = int(time.time())
            else:
                unix_ts = request.timestamp.seconds
            # TODO we should do everything in a single transaction
            # (even ideally including the checks) but this is already so much
            # better than the several `hg` processes that this method replaces
            # that we can postpone that to a later move.

            # Passing as revision number will reacquire the changeset, which
            # is really needed as we are now in a different repo (share).
            try:
                # TODO test we don't wait on some impossible user input
                with operation_error_treatment(context, MergeBranchError,
                                               logger=logger):
                    new_changeset = self.merge(working_dir=wd,
                                               source_changeset=to_merge,
                                               user=request.user,
                                               message=request.message,
                                               unix_timestamp=unix_ts,
                                               context=context)
            except ConflictError as exc:
                unresolved = exc.args[0]
                structured_abort(
                    context,
                    StatusCode.FAILED_PRECONDITION,
                    "merging commits: merge: there are conflicting files",
                    MergeBranchError(
                        conflict=MergeConflictError(
                            conflicting_commit_ids=[
                                cs.hex().decode('ascii')
                                for cs in (current_head, to_merge)
                            ],
                            conflicting_files=unresolved
                        )
                    )
                )

            self.publish(new_changeset, context)
            return MergeBranchResponse(
                branch_update=OperationBranchUpdate(
                    commit_id=new_changeset.hex().decode('ascii'),
                ))

    def merge(self, working_dir, context, source_changeset,
              user: User, message, unix_timestamp):
        """Merge changeset with given revno in working repository.

        The working repositoy is assumed to be already updated in a
        meaningful way.
        """
        working_repo = working_dir.repo
        if not wd_merge(working_dir, source_changeset):
            unresolved = list(mergestate.read(working_repo).unresolved())
            self.repo_command(working_repo, context, 'merge', abort=True)
            raise ConflictError(unresolved)
        # TODO user timezone (symbolic or UTC offset?)
        self.repo_command(working_repo, context, 'commit',
                          user=b'%s <%s>' % (user.name, user.email),
                          date=b'%d 0' % unix_timestamp,
                          message=message)
        return working_repo[b'.']


def wd_merge(working_dir, source_cs):
    """Merge source_cs in the given a working directory (repo share).

    :source_cs: a :class:`changectx`, usually not tied to ``working_dir`` but
      to its share source or a share sibling.
    :return: whether it suceeded
    """
    # re-evalutate the changectx in the context of working_dir,
    # as `merge()` will read the repo from it
    repo = working_dir.repo
    source_for_wd = repo[source_cs.rev()]

    overrides = {(b'ui', b'forcemerge'): b'internal:merge3',
                 (b'ui', b'interactive'): b'off'}
    with repo.ui.configoverride(overrides, b'merge'):
        # not sure labels are really necessary, but it is
        # possible that the merge tools require them.
        stats = merge(source_for_wd,
                      labels=MERGE_CONFLICTS_LABELS)
        return not stats.unresolvedcount


def abort_pre_check_changeset(context, changeset, cause, error_cls):
    structured_abort(
        context,
        StatusCode.FAILED_PRECONDITION,
        changeset.hex().decode('ascii'),
        error_cls(pre_check=cause)
    )
