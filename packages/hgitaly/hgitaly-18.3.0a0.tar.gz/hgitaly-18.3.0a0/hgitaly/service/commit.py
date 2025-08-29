# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import itertools
import logging

from grpc import StatusCode
from google.protobuf.timestamp_pb2 import Timestamp
from mercurial import (
    error,
    pycompat,
    logcmdutil,
    hgweb,
    node as nodemod,
)
from mercurial.node import nullrev as NULL_REVISION

from hgext3rd.heptapod.branch import get_default_gitlab_branch

from .. import (
    manifest,
    message,
)
from ..errors import (
    not_implemented,
    structured_abort,
)
from ..file_context import (
    git_perms,
)
from ..git import (
    OBJECT_MODE_TREE,
    GitPathSpec,
    GitLiteralPathSpec,
)
from ..logging import LoggerAdapter
from ..oid import (
    tree_oid,
    blob_oid,
)
from ..pagination import (
    extract_limit,
)
from ..revision import (
    VISIBLE_CHANGESETS,
    RevisionNotFound,
    gitlab_revision_changeset,
    resolve_revspecs_positive_negative,
)
from ..revset import (
    FollowNotImplemented,
    changeset_descr_regexp,
    revset_from_git_revspec,
)
from ..servicer import HGitalyServicer
from ..stream import (
    concat_resplit,
    WRITE_BUFFER_SIZE,
)
from ..stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitIsAncestorResponse,
    TreeEntryRequest,
    TreeEntryResponse,
    CheckObjectsExistRequest,
    CheckObjectsExistResponse,
    CountCommitsRequest,
    CountCommitsResponse,
    CountDivergingCommitsRequest,
    CountDivergingCommitsResponse,
    GetTreeEntriesError,
    GetTreeEntriesRequest,
    GetTreeEntriesResponse,
    TreeEntry,
    ListFilesRequest,
    ListFilesResponse,
    FindCommitRequest,
    FindCommitResponse,
    CommitStatsRequest,
    CommitStatsResponse,
    FindAllCommitsRequest,
    FindAllCommitsResponse,
    FindCommitsError,
    FindCommitsRequest,
    FindCommitsResponse,
    RawBlameError,
    RawBlameRequest,
    RawBlameResponse,
    LastCommitForPathRequest,
    LastCommitForPathResponse,
    ListLastCommitsForTreeRequest,
    ListLastCommitsForTreeResponse,
    CommitsByMessageRequest,
    CommitsByMessageResponse,
    ListCommitsByOidRequest,
    ListCommitsByOidResponse,
    ListCommitsRequest,
    ListCommitsResponse,
    ListCommitsByRefNameRequest,
    ListCommitsByRefNameResponse,
    FilterShasWithSignaturesRequest,
    FilterShasWithSignaturesResponse,
    GetCommitSignaturesRequest,
    GetCommitSignaturesResponse,
    GetCommitMessagesRequest,
    GetCommitMessagesResponse,
)
from ..stub.errors_pb2 import (
    PathError,
    PathNotFoundError,
    ResolveRevisionError,
)
from ..stub.commit_pb2_grpc import CommitServiceServicer
from ..util import (
    chunked,
    chunked_with_cursor,
)

base_logger = logging.getLogger(__name__)

NULL_REV = nodemod.nullrev
PSEUDO_REVS = (nodemod.wdirrev, nodemod.nullrev)
PSEUDO_REVLOG_NODES = {
    nodemod.nullid,
    nodemod.wdirid,
}
PSEUDO_REVLOG_NODES.update(nodemod.wdirfilenodeids)


class CommitServicer(CommitServiceServicer, HGitalyServicer):

    STATUS_CODE_STORAGE_NOT_FOUND = StatusCode.INVALID_ARGUMENT

    def CommitIsAncestor(self,
                         request: CommitIsAncestorRequest,
                         context) -> CommitIsAncestorResponse:
        logger = LoggerAdapter(base_logger, context)
        # The question is legit for filtered changesets and that
        # happens in MR rebase scenarios, before the Rails app realizes
        # the MR has to be updated.
        repo = self.load_repo(request.repository, context).unfiltered()
        # TODO status.Errorf(codes.InvalidArgument, "Bad Request
        # (empty ancestor sha)") and same for child
        try:
            ancestor = repo[request.ancestor_id.encode()]
            child = repo[request.child_id.encode()]
        except error.RepoLookupError as exc:
            # Gitaly just returns False. This is probably an inconsistency
            # in the client, so let's log it to help.
            logger.warning(
                "CommitIsAncestor for child_id=%r, ancestor_id=%r, got %r",
                request.ancestor_id, request.child_id, exc)
            result = False
        else:
            result = ancestor.isancestorof(child)

        return CommitIsAncestorResponse(value=result)

    def TreeEntry(self, request: TreeEntryRequest,
                  context) -> TreeEntryResponse:
        """Return an entry of a tree.

        The name could be confusing with the entry for a tree: the entry
        can be of any type.

        Actually, it always yields one response message, using the empty
        response in case the given path does not resolve.
        """
        repo = self.load_repo(request.repository, context).unfiltered()
        changeset = gitlab_revision_changeset(repo, request.revision)
        if changeset is None:
            # As of v15.8.0, Gitaly error details don't give up anything
            context.abort(StatusCode.NOT_FOUND, "tree entry not found")

        sha = changeset.hex().decode('ascii')
        # early testing shows that even for leaf files, Gitaly ignores
        # trailing slashes
        path = request.path.rstrip(b'/')

        try:
            filectx = changeset.filectx(path)
        except error.ManifestLookupError:
            filectx = None

        # TODO investigate why it's not the usual WRITE_BUFFER_SIZE
        # The only occurrence we could find so far was a 16384 in grpc Golang
        # lib (size of HTTP/2 frames).
        # Could be because Gitaly implementation uses CopyN to send to
        # its chunker (in `streamio.go`) and CopyN has a buffer.
        buffer_size = 16384
        if filectx is not None:
            otype = TreeEntryResponse.ObjectType.BLOB
            oid = blob_oid(repo, sha, path)
            mode = git_perms(filectx)
            size = filectx.size()
            max_size = request.max_size
            if max_size != 0 and size > request.max_size:
                context.abort(
                    StatusCode.FAILED_PRECONDITION,
                    "object size (%d) is bigger than the maximum "
                    "allowed size (%d)" % (size, max_size))

            data = filectx.data()

            limit = request.limit
            if limit != 0:
                data = data[:limit]

            offset = 0
            while offset < size:
                # only the first response of the stream carries the metadata
                if offset:
                    resp = TreeEntryResponse()
                else:
                    resp = TreeEntryResponse(type=otype,
                                             oid=oid,
                                             size=size,
                                             mode=mode)

                resp.data = data[offset:offset+buffer_size]
                offset += buffer_size

                yield resp
            return

        subtrees, file_paths = manifest.miner(changeset).ls_dir(path)
        if not subtrees and not file_paths:
            context.abort(StatusCode.NOT_FOUND, "tree entry not found")

        # path is an actual directory

        # size computation to match Git response.
        # The formula for size computation is meant to match the size
        # returned by Git, which is actually the size of the raw Git Tree
        # object as returned by `git-cat-file` with `<type>` parameter.
        #
        # The raw Git Tree object is a simple concatenation of entries, each
        # one being made of
        # - mode (octal representation): 6 bytes for blobs (e.g 100644),
        #                                5 bytes for subtrees (40000)
        # - 0x20 (separator): 1 byte
        # - name of the entry
        # - 0x00 (separator): 1 byte
        # - binary SHA-1 of the object referenced by the entry: 20 bytes
        # Hence the total length per entry is 27 + (name length) for subtrees
        # and 28 + (name length) for blobs.
        # Finally, our `ls_dir` returns full paths from the root, so the
        # have to substract `len(path + b'/')`, hence `len(path) + 1`
        # for each entry.
        size = (
            28 * len(file_paths) + 27 * len(subtrees)
            + sum(len(s) for s in subtrees) + sum(len(f) for f in file_paths)
            - (len(subtrees) + len(file_paths)) * (len(path) + 1)
        )
        # max_size does not apply here (see Gitaly comparison test)
        yield TreeEntryResponse(
            type=TreeEntryResponse.ObjectType.TREE,
            oid=tree_oid(repo, sha, path),
            mode=OBJECT_MODE_TREE,
            size=size,
        )

    def CountCommits(self,
                     request: CountCommitsRequest,
                     context) -> CountCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        # TODO: yet to finish this method to support all lookups
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        # revision can be a pseudo range, like b'12340f9b5..a5f36b6a53012',
        # (see CommitsBetween for how we handle that)
        # (used in MR widget)
        if revision:
            if b'..' in revision:
                # TODO also case of ... (3 dots), I suppose
                ctx_start, ctx_end = [gitlab_revision_changeset(repo, rev)
                                      for rev in revision.split(b'..')]
                if ctx_start is None or ctx_end is None:
                    logger.warning(
                        "CountCommits for %r: one of these revisions "
                        "could not be found", revision)
                    return CountCommitsResponse()

                if ctx_end.obsolete() or ctx_start.obsolete():
                    repo = repo.unfiltered()

                revs = repo.revs('only(%s, %s)',
                                 ctx_end.hex(), ctx_start.hex())
            else:
                ctx = gitlab_revision_changeset(repo, revision)
                if ctx is None:
                    logger.warning(
                        "CountCommits revision %r could not be found",
                        revision)
                    return CountCommitsResponse()
                revs = repo.unfiltered().revs('::%s', ctx)
            count = len(revs)
        elif not request.all:
            # note: `revision` and `all` are mutually exclusive
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "empty Revision and false All")
        else:
            # Note: if revision is not passed, we return all revs for now.
            # TODO not really exact, should be non obsolete and ::keeparounds
            count = len(repo)
        max_count = request.max_count
        if max_count and count > max_count:
            # TODO better to limit the revsets before hand
            count = max_count
        return CountCommitsResponse(count=count)

    # CountDivergingCommits counts the diverging commits between from and to.
    # Important to note that when --max-count is applied, the counts are not
    # guaranteed to be accurate.

    def CountDivergingCommits(self,
                              request: CountDivergingCommitsRequest,
                              context) -> CountDivergingCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        rev_from = gitlab_revision_changeset(repo, getattr(request, 'from'))
        rev_to = gitlab_revision_changeset(repo, getattr(request, 'to'))
        max_count = request.max_count
        if rev_from is None:
            logger.warning("cannot resolve 'from' revision in %r",
                           message.Logging(request))
        if rev_to is None:
            logger.warning("cannot resolve 'to' revision in %r",
                           message.Logging(request))
        if rev_from is None or rev_to is None:
            return CountDivergingCommitsResponse(left_count=0, right_count=0)
        left = rev_from.rev()
        right = rev_to.rev()

        # Switching to unfiltered repo view, only if really needed.
        # using the unfiltered repo should not change the result given that
        # the revisions are fully resolved, but let's not take the risk.
        if rev_from.obsolete() or rev_to.obsolete():
            repo = repo.unfiltered()

        branchpoint = repo.revs(b"ancestor(%d, %d)" % (left, right)).first()
        if branchpoint is None:
            left_revset = b'::%d' % left
            right_revset = b'::%d' % right
        else:
            left_revset = b"%d::%d - %d" % (branchpoint, left, branchpoint)
            right_revset = b"%d::%d  - %d" % (branchpoint, right, branchpoint)
        left_count = len(repo.revs(left_revset))
        right_count = len(repo.revs(right_revset))

        if max_count and (left_count + right_count) > max_count:
            delta = (left_count + right_count) - max_count
            if left_count >= delta:
                left_count -= delta
            else:
                delta -= left_count
                left_count = 0
                right_count -= delta
        return CountDivergingCommitsResponse(left_count=left_count,
                                             right_count=right_count)

    def GetTreeEntries(self, request: GetTreeEntriesRequest,
                       context) -> GetTreeEntriesResponse:
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        changeset = gitlab_revision_changeset(repo, revision)
        if changeset is None:
            structured_abort(
                context,
                StatusCode.INVALID_ARGUMENT,
                "invalid revision or path",
                GetTreeEntriesError(resolve_tree=ResolveRevisionError(
                    revision=request.revision)))

        repo = repo.unfiltered()
        sha = changeset.hex().decode('ascii')
        if not request.path:
            structured_abort(
                context,
                StatusCode.INVALID_ARGUMENT, "empty path",
                GetTreeEntriesError(
                    path=PathError(path=request.path,
                                   error_type=PathError.ERROR_TYPE_EMPTY_PATH))
            )
        path = request.path.rstrip(b'/')  # same as in TreeEntry
        if path == b'.':  # special case, means the top directory
            path = b''

        blob_type = TreeEntry.EntryType.BLOB
        tree_type = TreeEntry.EntryType.TREE
        miner = manifest.miner(changeset)

        if request.recursive:
            entries = ((epath, is_dir, b'')
                       for epath, is_dir in miner.iter_dir_recursive(path))
        elif request.skip_flat_paths:
            trees, files = miner.ls_dir(path)
            entries = itertools.chain(
                ((epath, True, b'') for epath in trees),
                ((epath, False, b'') for epath in files),
            )
        else:
            entries = miner.iter_dir_with_flat_paths(path)

        # TODO request.sort == SortBy.TREES_FIRST
        limit = extract_limit(request)
        if limit == 0:
            return  # simplify things (next_cursor computation notably)

        # voids the advantages of iteration, but there's few choice
        # in the matter with sort and pagination
        if request.sort == GetTreeEntriesRequest.SortBy.TREES_FIRST:
            # each entry is (path, is_dir (bool), flat_path)
            # where flat_path is ignored for sorting purposes.
            # TODO OPTIM is it an improvement to avoid this post-processing
            # sort by making ManifestMiner already provide directories first?
            # to get an advantage, we'd need to avoid at least a list
            # construction
            entries = sorted(
                entries,
                key=lambda entry: (1 if entry[1] else 2, entry[0]))
        else:
            # TODO OPTIM because Mercurial manifests are stored in
            # lexicographical ordering, this sort is probably unnecessary.
            # In first impl of sorting and pagination, probably not worth
            # the risk.
            # Also would be neat to avoid consuming the iterator into
            # a least, but is it worth the added complexity if it can't
            # be done in the TREES_FIRST case?
            # What if GitLab introduces a sort direction anyway ?
            entries = sorted(entries)  # sorts lexicographically by path

        if not entries:
            # there is no such thing as an empty directory in Mercurial
            try:
                changeset.filectx(path)
            except error.ManifestLookupError:
                if request.recursive:
                    err_code = StatusCode.NOT_FOUND
                else:
                    err_code = StatusCode.INVALID_ARGUMENT
                structured_abort(
                    context,
                    err_code,
                    "invalid revision or path",
                    GetTreeEntriesError(resolve_tree=ResolveRevisionError(
                        revision=request.revision))
                )
            else:
                structured_abort(
                    context,
                    StatusCode.INVALID_ARGUMENT,
                    "path not treeish",
                    GetTreeEntriesError(resolve_tree=ResolveRevisionError(
                        revision=request.revision))
                )

        def entry_oid(path, is_dir):
            return (tree_oid if is_dir else blob_oid)(repo, sha, path)

        page_token = request.pagination_params.page_token
        if page_token:
            for offset, (path, is_dir, _) in enumerate(entries):
                if entry_oid(path, is_dir) == page_token:
                    break
            else:
                context.abort(StatusCode.INTERNAL,
                              "could not find starting OID: %s" % page_token)

            entries = entries[offset+1:]

        if limit < len(entries):
            entries = entries[:limit]
            last_path, last_is_dir = entries[-1][:2]
            next_cursor = entry_oid(last_path, last_is_dir)
        else:
            next_cursor = ''

        yield from chunked_with_cursor(
            GetTreeEntriesResponse,
            entries,
            next_cursor=next_cursor,
            builder=lambda chunk: dict(
                entries=(
                    TreeEntry(
                        path=path,
                        type=tree_type if is_dir else blob_type,
                        oid=entry_oid(path, is_dir),
                        commit_oid=revision,
                        mode=(OBJECT_MODE_TREE if is_dir else
                              git_perms(changeset.filectx(path))),
                        flat_path=flat_path,
                    )
                    for path, is_dir, flat_path in chunk)
                )
        )

    def ListFiles(self, request: ListFilesRequest,
                  context) -> ListFilesResponse:
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        mf = ctx.manifest()
        for paths in chunked(mf.iterkeys()):
            yield ListFilesResponse(paths=paths)

    def CommitStats(self, request: CommitStatsRequest,
                    context) -> CommitStatsResponse:
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            context.abort(StatusCode.INTERNAL,
                          "failed to get commit stats: object not found.")

        ctxp1 = ctx.p1()
        statsgen = hgweb.webutil.diffstatgen(repo.ui, ctx, ctxp1)
        # stats format:
        #   (list_of_stats_per_file, maxname,
        #    maxtotal, addtotal, removetotal, binary)
        # we only need addtotal and removetotal for our use case
        stats = next(statsgen)
        addtotal, removetotal = stats[-3], stats[-2]
        return CommitStatsResponse(
            oid=ctx.hex(),
            additions=addtotal,
            deletions=removetotal,
        )

    def FindCommit(self,
                   request: FindCommitRequest, context) -> FindCommitResponse:
        logger = LoggerAdapter(base_logger, context)
        revision = request.revision
        if not revision:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty revision")

        repo = self.load_repo(request.repository, context)
        ctx = gitlab_revision_changeset(repo, revision)

        if ctx is None:
            logger.warning("FindCommit revision %r could not be found",
                           revision)
            return FindCommitResponse()

        if ctx.rev() == NULL_REV:
            return FindCommitResponse()

        commit = message.commit(ctx)
        return FindCommitResponse(commit=commit)

    def FindAllCommits(self, request: FindAllCommitsRequest,
                       context) -> FindAllCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        if revision:
            # If false, return all commits reachable by any branch in the repo
            ctx = gitlab_revision_changeset(repo, revision)
            if ctx is None:
                logger.warning(
                    "FindAllCommits revision %r could not be found",
                    revision)
                return FindAllCommitsResponse()
            revset = b"reverse(::%s)" % ctx
            # if ctx is an obsolete changeset, its repo is unfiltered.
            # this is legitimate if revision is a direct hash or a GitLab
            # special ref and should not happen otherwise
            repo = ctx.repo()
        else:
            revset = b'reverse(all())'

        revs = repo.revs(revset)
        offset = request.skip
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        if request.max_count:
            revs = revs.slice(0, request.max_count)
        if request.order == FindAllCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
        elif request.order == FindAllCommitsRequest.DATE:
            revs = repo.revs(b"reverse(sort(%ld, date))", revs)
        for chunk in chunked(revs):
            yield FindAllCommitsResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def FindCommits(self, request: FindCommitsRequest,
                    context) -> FindCommitsResponse:

        logger = LoggerAdapter(base_logger, context)
        req_log = message.Logging(request)

        if request.limit == 0:
            return

        repo = self.load_repo(request.repository, context)
        pats = request.paths
        # XXX: raise error if one of the path given is an empty string
        if pats:
            pats = list(map(lambda p: repo.root + b'/' + p, pats))

        repo, opts = parse_find_commits_request_opts(request, context, repo)

        if request.revision and not opts[b'rev'][0]:
            logger.debug(
                "Request %r, revision could not be found", req_log)
            structured_abort(
                context, StatusCode.NOT_FOUND, "commits not found",
                FindCommitsError())

        walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
        revs, _ = logcmdutil.getrevs(repo, walk_opts)

        if request.offset > 0:
            revs = revs.slice(request.offset, len(revs))

        if request.order == FindCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
            if request.all:
                revs = repo.revs(b"reverse(%ld)", revs)

        # investigation log for heptapod#1365
        if len(revs) == 0:
            logger.info("Empty commit list for walk_opts=%r", walk_opts)
#            context.abort(StatusCode.NOT_FOUND, "commits not found")

        incl_ref_by = request.include_referenced_by

        with_short_stats = request.include_shortstat
        for chunk in chunked(revs):
            yield FindCommitsResponse(
                commits=(message.commit(repo[rev],
                                        include_referenced_by=incl_ref_by,
                                        with_short_stats=with_short_stats)
                         for rev in chunk))

    def RawBlame(self, request: RawBlameRequest,
                 context) -> RawBlameResponse:
        repo = self.load_repo(request.repository, context)
        filepath = request.path
        if not filepath:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty Path")

        if request.range:
            lstart, lend = [int(x) for x in request.range.split(b',')]
            lstart -= 1
        else:
            lstart, lend = 0, None

        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        try:
            for data in concat_resplit(blamelines(repo, ctx, filepath,
                                                  lstart=lstart,
                                                  lend=lend,
                                                  ),
                                       WRITE_BUFFER_SIZE):
                yield RawBlameResponse(data=data)
        except error.ManifestLookupError:
            structured_abort(
                context, StatusCode.NOT_FOUND,
                "path not found in revision",
                RawBlameError(path_not_found=PathNotFoundError(path=filepath))
            )
        except BlameRangeError as exc:
            structured_abort(
                context,
                StatusCode.INVALID_ARGUMENT,
                "range is outside of the file length",
                RawBlameError(out_of_range=RawBlameError.OutOfRangeError(
                    actual_lines=exc.actual_lines())))

    def LastCommitForPath(self,
                          request: LastCommitForPathRequest,
                          context) -> LastCommitForPathResponse:
        repo = self.load_repo(request.repository, context)
        revision, path = request.revision, request.path
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None or ctx.rev() == NULL_REVISION:
            context.abort(StatusCode.INTERNAL,
                          "logging last commit for path: exit status 128")

        changeset = latest_changeset_for_path(
            path, ctx,
            literal_pathspec=(request.global_options.literal_pathspecs
                              or request.literal_pathspec)
        )

        return LastCommitForPathResponse(
            commit=message.commit(changeset),
        )

    def ListLastCommitsForTree(self, request: ListLastCommitsForTreeRequest,
                               context) -> ListLastCommitsForTreeResponse:
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        from_ctx = gitlab_revision_changeset(repo, revision)
        if from_ctx is None or from_ctx.rev() == NULL_REVISION:
            context.abort(StatusCode.INTERNAL, "exit status 128")

        offset, limit = request.offset, request.limit
        if limit == 0:
            return

        if limit < 0:
            context.abort(StatusCode.INVALID_ARGUMENT, 'limit negative')
        if offset < 0:
            context.abort(StatusCode.INVALID_ARGUMENT, 'offset negative')

        req_path = request.path

        if req_path in (b'.', b'/', b'./'):
            req_path = b''

        if req_path and not req_path.endswith(b'/'):
            if offset > 0:
                return

            changeset = latest_changeset_for_path(req_path, from_ctx,
                                                  literal_pathspec=True)
            if changeset:
                yield ListLastCommitsForTreeResponse(
                    commits=[message.commit_for_tree(changeset, req_path)])
            return

        # subtrees first, then regular files, each one in lexicographical order
        subtrees, file_paths = manifest.miner(from_ctx).ls_dir(req_path)
        end = offset + limit
        nb_subtrees = len(subtrees)
        if nb_subtrees > end:
            subtrees = subtrees[offset:end]
            file_paths = ()
        else:
            subtrees = subtrees[offset:end]
            file_paths = file_paths[max(offset-nb_subtrees, 0):end-nb_subtrees]

        changesets = latest_changesets_for_paths(subtrees, file_paths,
                                                 from_ctx)
        all_paths = subtrees
        all_paths.extend(file_paths)
        for chunk in chunked(all_paths):
            yield ListLastCommitsForTreeResponse(
                commits=[
                    message.commit_for_tree(
                        changesets[path],
                        path
                    )
                    for path in chunk
                ])

    def CommitsByMessage(self, request: CommitsByMessageRequest,
                         context) -> CommitsByMessageResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        query = request.query
        if not query:
            return CommitsByMessageResponse()
        pats = []
        opts = {}
        if request.path:
            path = repo.root + b'/' + request.path
            pats.append(path)
        if request.limit:
            opts[b'limit'] = request.limit
        if request.revision:
            revset = revset_from_git_revspec(repo, request.revision)
            repo = repo.unfiltered()
            if revset is None:
                logger.debug(
                    "CommitsByMessage revision %r could not be found",
                    request.revision)
                return CommitsByMessageResponse()
        else:
            revision = get_default_gitlab_branch(repo)
            # XXX: return error if no default branch found
            revset = revset_from_git_revspec(repo, revision)
        # Instead of sending 'query' as a key:value pair ('keyword': query) in
        # `opts`, appending the query to `revset` as "...and keyword('query')"
        # to make sure it perform an intersetion of two, instead of a union.
        revset = revset + b" and keyword('%b')" % query.encode()
        opts[b'rev'] = [revset]
        walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
        revs, _ = logcmdutil.getrevs(repo, walk_opts)
        offset = request.offset
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        for chunk in chunked(revs):
            yield CommitsByMessageResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def CheckObjectsExist(self, request: CheckObjectsExistRequest,
                          context) -> CheckObjectsExistResponse:
        not_implemented(context, issue=101)  # pragma no cover

    def ListCommits(self, request: ListCommitsRequest,
                    context) -> ListCommitsResponse:
        """Implementation of ListCommits, with some differences with Gitaly.

        Orderings
        ~~~~~~~~~
        As recalled in `commit.proto` comment, Git default ordering (and
        hence Gitaly's) is by date BUT that means actually first by
        parentship, then by date (actually CommitDate, not AuthorDate).
        Quoting git-log(1):

         --date-order
             Show no parents before all of its children are shown, but
             otherwise show commits in the commit timestamp order.

        I could check that this commit timestamp is the `CommitDate` field.

        On the other hand, Mercurial's date ordering ignores
        the graph completely, and there's no mixed ordering similar to Git's
        (although perhaps the `topo.firstbranch` could be used for this.

        NONE (default)
        --------------
        By default, instead of Git's (parentship, CommitDate) we're using
        the rev number: it respects parentship, and is conceptually close
        to the CommitDate ordering, which is by default the actual date of
        this exact commit creation (for instance, it is updated by
        `git commit --amend` whereas AuthodDate is not). CommitDate can be
        forced on a Git repository, but there's no Mercurial equivalent of
        that. The end result will be something akin to a PushDate field if
        there was any.

        There is hopefully no logic that really depends on the ordering on
        the client side, as long as it respects the parentship. As of this
        writing, this call is used for Merge Requests list of commits.
        Respecting the parentship is important, CommitDate on the Git side
        vs PushDate on the Mercurial side is probably not.

        TOPO
        ----

        These behave the same way between Git and Mercurial, the client
        will have to consider the choice of parent to present first to
        be arbitrary anyway

        DATE
        ----

        As explained above, Mercurial's date ordering is quite different
        from Git's. For now we choose to use it nevertheless if explicitely
        requested, but this could change if we identify trouble.
        """
        revisions = request.revisions
        if not revisions:
            context.abort(StatusCode.INVALID_ARGUMENT, "missing revisions")

        repo = self.load_repo(request.repository, context)
        revisions = (pycompat.sysbytes(r) for r in revisions)
        try:
            positive, negative = resolve_revspecs_positive_negative(
                repo, revisions)
        except RevisionNotFound as exc:
            context.abort(StatusCode.INTERNAL,
                          "Revision %r could not be resolved" % exc.args[0])

        walk = not request.disable_walk

        if positive is VISIBLE_CHANGESETS:
            # do not switch to unfiltered view!
            if negative:
                revset = b'not ::%ls'
            else:
                revset = b'all()'
        else:
            # now that resolution is done, we can and have to switch to
            # the unfiltered view, because the resulting hashes can be of
            # obsolete changesets.
            repo = repo.unfiltered()
            if negative:
                revset = b'only(%ls, %ls)'
            elif walk:
                revset = b'::%ls'
            else:
                revset = b'%ls'

        msg_patterns = request.commit_message_patterns
        ignore_case = request.ignore_case
        if msg_patterns:
            # TODO all kinds of painful escapings (should be in lib)
            greps = [changeset_descr_regexp(pattern, ignore_case=ignore_case)
                     for pattern in msg_patterns]
            if len(greps) > 1:
                revset += b' and (%s)' % b' or '.join(greps)
            else:
                revset += b' and ' + greps[0]

        after = request.after.ToSeconds()
        before = request.before.ToSeconds()
        date = getdate(after, before)
        if date is not None:
            revset += b" and date('%s')" % date.encode('ascii')

        author = request.author
        if author:
            revset += b" and user(r're:%s')" % author

        # no octopuses in Mercurial, hence max_parents > 1 does not filter
        # anything
        if request.max_parents == 1:
            revset += b" and not merge()"

        Order = ListCommitsRequest.Order
        reverse = request.reverse

        if request.order == Order.NONE:
            # default Git ordering is Mercurial's reversed
            sort_key = b'rev' if reverse else b'-rev'
        elif request.order == Order.TOPO:
            sort_key = b'-topo' if reverse else b'topo'
        elif request.order == Order.DATE:
            # See docstring about this approximative choice
            sort_key = b'-date' if reverse else b'date'

        revset = b'sort(%s, %s)' % (revset, sort_key)

        try:
            if positive is VISIBLE_CHANGESETS:
                if negative:
                    revs = repo.revs(revset, negative)
                else:
                    revs = repo.revs(revset)
            elif negative:
                revs = repo.revs(revset, positive, negative)
            else:
                revs = repo.revs(revset, positive)
        except error.ParseError as exc:
            # no point trying to mimic Gitaly's error message, as it is
            # very dependent on internal details. Example for invalid regexp
            # with Gitaly 15.4:
            #  iterating objects: re...e command: exit status 128,
            #  stderr: "fatal: command line, '[]': Unmatched [, [^, [:, [.,
            #  or [=\n"
            context.abort(StatusCode.INTERNAL, "Invalid filter: " + str(exc))

        # `skip` has to be interpreted before pagination
        # smartset.slice insists on having a "last" value:
        # it constructs a list internally, which would be a performance
        # issue to skip the first 3 revisions of a million-sized revset.
        # Too bad there is no cheap way to consume the revset as an iterator.
        # Anyway we'd do that in a Rust implementation if ever needed.
        if request.skip > 0:
            revs = revs.slice(request.skip, len(revs))

        # according to protocol comment, the page token
        # is the last commit OID already sent (similar to blob/tree requests)
        cursor = request.pagination_params.page_token
        if not cursor:
            offset = 0
        else:
            # TODO perf it would probably be much faster to use the index
            # directly rather than to construct contexts
            for offset, rev in enumerate(revs):
                sha = repo[rev].hex().decode()
                if sha == cursor:
                    offset = offset + 1
                    break
        limit = extract_limit(request)
        revs = revs.slice(offset, offset + limit)
        if not revs:
            return

        for chunk in chunked(revs):
            yield ListCommitsResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def ListCommitsByOid(self, request: ListCommitsByOidRequest,
                         context) -> ListCommitsByOidResponse:
        repo = self.load_repo(request.repository, context)
        repo = repo.unfiltered()
        lookup_error_classes = (error.LookupError, error.RepoLookupError)
        for chunk in chunked(pycompat.sysbytes(oid) for oid in request.oid):
            try:
                chunk_commits = [message.commit(repo[rev])
                                 for rev in repo.revs(b'%ls', chunk)
                                 if rev not in PSEUDO_REVS]
            except lookup_error_classes:
                # lookup errors aren't surprising: the client uses this
                # method for prefix resolution
                # The reference Gitaly implementation tries them one after
                # the other (as of v13.4.6)
                chunk_commits = []
                for oid in chunk:
                    try:
                        # TODO here, something only involving the nodemap
                        # would be in order
                        revs = repo.revs(b'%s', oid)
                    except lookup_error_classes:
                        # ignore unresolvable oid prefix
                        pass
                    else:
                        if len(revs) == 1:
                            rev = revs.first()
                            if rev in PSEUDO_REVS:
                                continue
                            chunk_commits.append(message.commit(repo[rev]))
            if chunk_commits:
                yield ListCommitsByOidResponse(commits=chunk_commits)

    def ListCommitsByRefName(self, request: ListCommitsByRefNameRequest,
                             context) -> ListCommitsByRefNameResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        ref_names = request.ref_names

        commits = []
        for ref_name in ref_names:
            ctx = gitlab_revision_changeset(repo, ref_name)
            if ctx is None:
                logger.warning(
                    "ListCommitByRefName ref %r could not be "
                    "resolved to a changeset",
                    ref_name)
                continue
            commits.append([ref_name, ctx])
        CommitForRef = ListCommitsByRefNameResponse.CommitForRef
        for chunk in chunked(commits):
            yield ListCommitsByRefNameResponse(
                commit_refs=(CommitForRef(
                    commit=message.commit(ctx),
                    ref_name=ref_name
                ) for ref_name, ctx in chunk)
            )

    def FilterShasWithSignatures(self,
                                 request: FilterShasWithSignaturesRequest,
                                 context) -> FilterShasWithSignaturesResponse:
        not_implemented(context, issue=24)  # pragma no cover

    def GetCommitSignatures(self, request: GetCommitSignaturesRequest,
                            context) -> GetCommitSignaturesResponse:
        not_implemented(context, issue=24)  # pragma no cover

    def GetCommitMessages(self, request: GetCommitMessagesRequest,
                          context) -> GetCommitMessagesResponse:
        repo = self.load_repo(request.repository, context)
        results = {}
        for commit_id in request.commit_ids:
            commit_id = pycompat.sysbytes(commit_id)
            ctx = gitlab_revision_changeset(repo, commit_id)
            if ctx is None:
                # should not be an "internal" error, but
                # that's what Gitaly does anyway
                context.abort(
                    StatusCode.INTERNAL,
                    "failed to get commit message: object not found.")

            results[commit_id] = ctx.description()
        for commit_id, msg in results.items():
            yield GetCommitMessagesResponse(commit_id=commit_id,
                                            message=msg)


def parse_find_commits_request_opts(request, context, repo):
    """Interpred FindCommitRequestAttributes

    :return: (repo, options for logcmdutil.parseopts). Returning the repo
      is important because we often (but not always) need to switch to
      the unfiltered repo.
    """
    logger = LoggerAdapter(base_logger, context)
    opts = {
        b'follow': request.follow,
        b'no_merges': request.skip_merges,
        b'limit': request.limit + request.offset,
    }
    # TODO: implement 'request.first_parent' option
    # khanchi97: found that its counterpart follow-first in "hg log" is
    # deprecated and give wrong results with other options like revision,
    # all, etc.
    if request.author:
        opts[b'user'] = [request.author]
    after = request.after.ToSeconds()
    before = request.before.ToSeconds()
    date = getdate(after, before)
    if date is not None:
        opts[b'date'] = date

    revision = request.revision
    # `revision` and `all` are mutually exclusive,
    # if both present `all` gets the precedence
    if request.all:
        opts[b'rev'] = [b'0:tip']
        return repo, opts

    if not revision:
        revision = get_default_gitlab_branch(repo)

    if revision:
        try:
            revset = revset_from_git_revspec(repo, revision,
                                             for_follow=request.follow)
        except FollowNotImplemented:
            logger.warning("Ignoring `follow: true` (not implemented with "
                           "this revspec) for %r", message.Logging(request))
            revset = revset_from_git_revspec(repo, revision)
            opts[b'follow'] = False

        opts[b'rev'] = [revset]
    return repo.unfiltered(), opts


def getdate(after, before):
    if after and before:
        after = _isoformat_from_seconds(after)
        before = _isoformat_from_seconds(before)
        return "%s UTC to %s UTC" % (after, before)
    elif after:
        after = _isoformat_from_seconds(after)
        return ">%s UTC" % after
    elif before:
        before = _isoformat_from_seconds(before)
        return "<%s UTC" % before
    return None


def _isoformat_from_seconds(secs):
    ts = Timestamp()
    ts.FromSeconds(int(secs))
    dt = ts.ToDatetime()
    return dt.isoformat()


def ancestors_inclusive(changeset):
    yield changeset
    yield from changeset.ancestors()


def latest_changeset_for_path(path, seen_from, literal_pathspec=False):
    """Return latest ancestor of ``seen_from`` that touched the given path.

    :param bytes path: subdir or file
    :param seen_from: changectx
    """
    if not path or path in (b'.', b'/', b'./'):
        # interpeted as a directory, this would be the repository root, which
        # all changesets change.
        # TODO comment above is wrong, as empty changesets do exist!
        # The question would be what Gitaly does in this case, if we care.
        return seen_from

    if literal_pathspec:
        match = GitLiteralPathSpec(path).match
    else:
        match = GitPathSpec(path).match

    for changeset in ancestors_inclusive(seen_from):
        if any(match(fp) for fp in changeset.files()):
            return changeset


def latest_changesets_for_paths(subdirs, file_paths, seen_from):
    """Return latest ancestor of ``seen_from`` that touched the given path.

    :param bytes path: subdir or file
    :param seen_from: changectx
    """
    dir_prefixes = set(d.rstrip(b'/') + b'/' for d in subdirs)
    file_paths = set(file_paths)

    latest_changesets = {}

    for changeset in ancestors_inclusive(seen_from):
        if not dir_prefixes and not file_paths:
            break

        for cfp in changeset.files():
            # TODO some performance improvement possible with a binary
            # search if changeset files are guaranteed to be sorted
            # but it'd probably make more of a difference in a Rust impl
            for dp in dir_prefixes:
                if cfp.startswith(dp):
                    latest_changesets[dp.rstrip(b'/')] = changeset
                    dir_prefixes.discard(dp)
                    break
            else:
                for fp in file_paths:
                    if fp == cfp:
                        latest_changesets[fp] = changeset
                        break
                else:
                    continue
                file_paths.discard(fp)
                continue

            dir_prefixes.discard(dp)

    return latest_changesets


class BlameRangeError(RuntimeError):
    def actual_lines(self):
        return self.args[0]


def blamelines(repo, ctx, file, lstart=0, lend=None):
    """Yield blame lines of a file.
    """
    fctx = ctx[file]
    # fctx.annotate() does not seem to be able to be linited to
    # a range, and is not even an iterator (as of Mercurial 6.6).
    # All we can do is use islice for the day it would become an iterator.
    # so that, e.g.,  annotating only the first line of a very large file
    # is less expensive than annotating the whole
    annotated = fctx.annotate()
    if lstart >= len(annotated):
        raise BlameRangeError(len(annotated))

    for line_no, line in enumerate(
            itertools.islice(fctx.annotate(), lstart, lend),
            start=1):
        old_line_no = line.lineno
        # required blame line format that get parsed by Rails:
        #   '<hash_id> <old_line_no> <line_no>\n\t<line_text>'
        yield b'%s %d %d\n\t%s' % (line.fctx.hex(), old_line_no, line_no,
                                   line.text)
