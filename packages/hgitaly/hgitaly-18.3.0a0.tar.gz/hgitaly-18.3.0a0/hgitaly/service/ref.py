# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging
from grpc import StatusCode

from mercurial import (
    error as hgerror,
)

from heptapod.gitlab.branch import (
    GITLAB_BRANCH_REF_PREFIX,
    gitlab_branch_from_ref,
    gitlab_branch_ref,
)
from heptapod.gitlab.tag import (
    GITLAB_TAG_REF_PREFIX,
)
from hgext3rd.heptapod.branch import get_default_gitlab_branch
from hgext3rd.heptapod.typed_ref import GITLAB_TYPED_REFS_MISSING
from hgext3rd.heptapod.special_ref import (
    parse_special_ref,
    special_refs,
    write_special_refs,
)
from hgext3rd.heptapod.keep_around import (
    parse_keep_around_ref,
    iter_keep_arounds,
    init_keep_arounds,
)

from ..errors import (
    not_implemented,
    structured_abort,
)
from ..logging import LoggerAdapter
from ..pagination import (
    extract_limit,
)
from ..revision import (
    CHANGESET_HASH_BYTES_REGEXP,
    ZERO_SHA,
    ZERO_SHA_STR,
    gitlab_revision_hash,
)
from ..stream import (
    chunked_limit,
)
from ..stub.shared_pb2 import (
    Branch,
    SortDirection,
)
from ..stub.errors_pb2 import (
    ReferenceNotFoundError,
    ReferenceStateMismatchError,
)
from ..stub.ref_pb2 import (
    FindDefaultBranchNameRequest,
    FindDefaultBranchNameResponse,
    FindLocalBranchesRequest,
    FindLocalBranchesResponse,
    FindAllBranchesRequest,
    FindAllBranchesResponse,
    FindAllTagsRequest,
    FindAllTagsResponse,
    FindRefsByOIDRequest,
    FindRefsByOIDResponse,
    FindTagError,
    FindTagRequest,
    FindTagResponse,
    FindAllRemoteBranchesRequest,
    FindAllRemoteBranchesResponse,
    RefExistsRequest,
    RefExistsResponse,
    FindBranchRequest,
    FindBranchResponse,
    DeleteRefsRequest,
    DeleteRefsResponse,
    UpdateReferencesError,
    UpdateReferencesRequest,
    UpdateReferencesResponse,
    ListBranchNamesContainingCommitRequest,
    ListBranchNamesContainingCommitResponse,
    ListTagNamesContainingCommitRequest,
    ListTagNamesContainingCommitResponse,
    GetTagSignaturesRequest,
    GetTagSignaturesResponse,
    GetTagMessagesRequest,
    GetTagMessagesResponse,
    ListRefsRequest,
    ListRefsResponse,
)
from ..stub.ref_pb2_grpc import RefServiceServicer

from ..branch import (
    BranchSortBy,
    gitlab_branch_head,
    iter_gitlab_branches,
    iter_gitlab_branches_as_refs,
    sorted_gitlab_branches_as_refs,
)
from ..gitlab_ref import (
    ensure_special_refs,
    has_keep_around,
    iter_gitlab_special_refs_as_refs,
    iter_keep_arounds_as_refs,
)
from ..tag import (
    EXCLUDED_TAG_TYPES,
    iter_gitlab_tags,
    iter_gitlab_tags_as_refs,
)
from .. import message
from ..servicer import HGitalyServicer
from ..util import chunked

base_logger = logging.getLogger(__name__)
DEFAULT_BRANCH_FILE_NAME = b'default_gitlab_branch'
FIND_LOCAL_BRANCHES_SORT_BY_TO_INNER = {
    FindLocalBranchesRequest.SortBy.NAME: BranchSortBy.FULL_REF_NAME,
    FindLocalBranchesRequest.SortBy.UPDATED_ASC: BranchSortBy.UPDATED_ASC,
    FindLocalBranchesRequest.SortBy.UPDATED_DESC: BranchSortBy.UPDATED_DESC
}

FIND_REFS_BY_OID_SORT_FIELD_TO_LIST_REFS = dict(
    refname=ListRefsRequest.SortBy.REFNAME,
    creatordate=ListRefsRequest.SortBy.CREATORDATE,
    authordate=ListRefsRequest.SortBy.AUTHORDATE,
)
"""keys are amenable fields in git-for-each-ref(1)

Not many such keys actually map to a SortBy value for ListRefsRequest.
"""


class RefServicer(RefServiceServicer, HGitalyServicer):
    """RefService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def FindDefaultBranchName(
            self,
            request: FindDefaultBranchNameRequest,
            context) -> FindDefaultBranchNameResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)

        branch = get_default_gitlab_branch(repo)
        if branch is None or gitlab_branch_head(repo, branch) is None:
            # Very coincidental, but this ends up as empty GitLab branch name
            # which the chain of || in app/models/concerns/repository
            # that eventually turns this in `nil`, which is the marker
            # used in the hg_fixup_default_branch in PostReceive…
            # TODO now that we have richer notifications, make a clear one
            # for that case
            logger.warning("FindDefaultBranchName: no information stored "
                           "for repo at %r, returning hempty response",
                           repo)
            return FindDefaultBranchNameResponse()

        return FindDefaultBranchNameResponse(name=gitlab_branch_ref(branch))

    def FindLocalBranches(self,
                          request: FindLocalBranchesRequest,
                          context) -> FindLocalBranchesResponse:
        repo = self.load_repo(request.repository, context)
        limit = extract_limit(request)
        if limit == 0:
            # util.chunk consider this means no limit,
            # shared.proto defines it to mean an empty response
            return

        after = request.pagination_params.page_token
        # TODO encoding?
        after = after.encode('utf-8') if after else None
        sort_by = FIND_LOCAL_BRANCHES_SORT_BY_TO_INNER.get(request.sort_by)

        for chunk in chunked(sorted_gitlab_branches_as_refs(repo,
                                                            sort_by=sort_by,
                                                            after=after),
                             limit=limit):
            yield FindLocalBranchesResponse(
                local_branches=(message.branch(name, head)
                                for name, head in chunk)
            )

    def FindAllBranches(self,
                        request: FindAllBranchesRequest,
                        context) -> FindAllBranchesResponse:
        Branch = FindAllBranchesResponse.Branch
        repo = self.load_repo(request.repository, context)
        for chunk in chunked(sorted_gitlab_branches_as_refs(
                repo,
                sort_by=BranchSortBy.FULL_REF_NAME
        )):
            yield FindAllBranchesResponse(
                branches=(Branch(name=name, target=message.commit(head))
                          for name, head in chunk))

    def FindAllTags(self,
                    request: FindAllTagsRequest,
                    context) -> FindAllTagsResponse:
        repo = self.load_repo(request.repository, context)
        for chunk in chunked(iter_gitlab_tags(repo)):
            yield FindAllTagsResponse(tags=[message.tag(name, ctx)
                                            for name, ctx in chunk])

    def FindTag(self,
                request: FindTagRequest,
                context) -> FindTagResponse:
        repo = self.load_repo(request.repository, context)
        name = request.tag_name
        if repo.tagtype(name) in EXCLUDED_TAG_TYPES:
            structured_abort(
                context, StatusCode.NOT_FOUND, "tag does not exist",
                FindTagError(tag_not_found=ReferenceNotFoundError(
                    reference_name=b'refs/tags/' + name)))

        node = repo.tags()[name]
        return FindTagResponse(tag=message.tag(name, repo[node]))

    def FindAllRemoteBranches(self,
                              request: FindAllRemoteBranchesRequest,
                              context) -> FindAllRemoteBranchesResponse:
        """There is no concept of "remote branch" in Mercurial."""
        return iter(())

    def RefExists(self,
                  request: RefExistsRequest,
                  context) -> RefExistsResponse:
        ref = request.ref
        if not ref.startswith(b'refs/'):
            context.abort(StatusCode.INVALID_ARGUMENT, "invalid refname")

        # TODO protect here
        repo = self.load_repo(request.repository, context)

        gl_branch = gitlab_branch_from_ref(ref)
        if gl_branch is not None:
            return RefExistsResponse(
                value=gitlab_branch_head(repo, gl_branch) is not None)

        gl_tag = gitlab_tag_from_ref(ref)
        if gl_tag is not None:
            return RefExistsResponse(
                value=repo.tagtype(gl_tag) not in EXCLUDED_TAG_TYPES)

        special = parse_special_ref(ref)
        if special is not None:
            srefs = special_refs(repo)
            if srefs is GITLAB_TYPED_REFS_MISSING:
                srefs = ensure_special_refs(repo)

            return RefExistsResponse(value=special in srefs)

        keep_around = parse_keep_around_ref(ref)
        if keep_around is not None:
            return RefExistsResponse(value=has_keep_around(repo, keep_around))
        return RefExistsResponse(value=False)

    def FindBranch(self,
                   request: FindBranchRequest,
                   context) -> FindBranchResponse:
        repo = self.load_repo(request.repository, context)
        name = request.name
        if name.startswith(b'refs/'):
            name = gitlab_branch_from_ref(request.name)

        if name is None:
            # TODO SPEC check if we really must exclude other refs
            return FindBranchResponse(branch=None)

        head = gitlab_branch_head(repo, name)
        if head is None:
            return FindBranchResponse(branch=None)

        return FindBranchResponse(
            branch=Branch(name=name, target_commit=message.commit(head)))

    def UpdateReferences(self,
                         request: UpdateReferencesRequest,
                         context) -> UpdateReferencesResponse:
        self.STATUS_CODE_STORAGE_NOT_FOUND = StatusCode.INVALID_ARGUMENT
        first = True
        special_changes = []
        ka_changes = []
        for req in request:
            if first:
                # blobs are given by oid, hence as in direct changeset Node
                # IDs, the unfiltered repo is the right one for the task
                repo = self.load_repo(req.repository, context).unfiltered()
                first = False

            for upd in req.updates:
                if len(upd.new_object_id) != 40:
                    oid = upd.new_object_id.decode('ascii', 'replace')
                    context.abort(StatusCode.INVALID_ARGUMENT,
                                  "validating new object ID: "
                                  f'invalid object ID: "{oid}", '
                                  f"expected length 40, got {len(oid)}")

                ref_path = upd.reference
                change = (upd.old_object_id, upd.new_object_id)
                if change[0] == change[1]:
                    # let's not waste resources for this
                    continue

                # consider only special refs and keep-arounds, as other refs
                # (branches and tags) are only reflecting changesets content,
                # setting them independently makes no sense with Mercurial
                special_ref = parse_special_ref(ref_path)
                if special_ref is not None:
                    special_changes.append((special_ref, change))
                    continue

                ka = parse_keep_around_ref(upd.reference)
                if ka is not None:
                    if (
                            upd.new_object_id != ZERO_SHA
                            and ka != upd.new_object_id
                    ):
                        context.abort(StatusCode.INVALID_ARGUMENT,
                                      "Inconsistent keep-around.")
                    ka_changes.append(change)

        with repo.lock():
            # keeping promise of atomicity of this method
            special_existing = special_refs(repo)
            if special_existing is GITLAB_TYPED_REFS_MISSING:
                special_existing = {}
            for name, (old_id, new_id) in special_changes:
                existing = special_existing.get(name)
                if old_id == ZERO_SHA and existing is not None:
                    context.abort(StatusCode.INTERNAL,
                                  "committing update: "
                                  "reference already exists")
                elif old_id and old_id != ZERO_SHA and existing != old_id:
                    Mismatch = ReferenceStateMismatchError  # just too long!
                    structured_abort(
                        context, StatusCode.ABORTED,
                        "reference does not point to expected object",
                        UpdateReferencesError(
                            reference_state_mismatch=Mismatch(
                                reference_name=b'refs/' + name,
                                expected_object_id=old_id,
                                actual_object_id=existing)))
                elif new_id == ZERO_SHA:
                    del special_existing[name]
                else:
                    special_existing[name] = new_id

            # TODO make a collect_keep_arounds() or keep_arounds_set()
            ka_existing = set(iter_keep_arounds(repo))
            ka_existing.discard(GITLAB_TYPED_REFS_MISSING)
            for old_id, new_id in ka_changes:
                # bogus requests have already been prohibited
                if new_id == ZERO_SHA:
                    ka_existing.discard(old_id)
                else:
                    ka_existing.add(new_id)

            write_special_refs(repo, special_existing)
            init_keep_arounds(repo, ka_existing)

        return UpdateReferencesResponse()

    def DeleteRefs(self,
                   request: DeleteRefsRequest,
                   context) -> DeleteRefsResponse:
        except_prefix = request.except_with_prefix
        refs = request.refs
        if refs and except_prefix:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "ExceptWithPrefix and Refs are mutually exclusive")

        repo = self.load_repo(request.repository, context)
        srefs = special_refs(repo)
        if srefs is GITLAB_TYPED_REFS_MISSING:
            srefs = ensure_special_refs(repo)
        if refs:
            # Using copy() to avoid doing anything (natural rollback) if
            # one of the ref is bogus.
            # It's not really important right now because we have
            # no cache of loaded repos, but that will change sooner or later.
            srefs = srefs.copy()
            err = remove_special_refs(srefs, refs)
            if err is not None:
                return DeleteRefsResponse(git_error=err)

        if except_prefix:
            srefs = special_refs_matching_prefixes(srefs, except_prefix)

        write_special_refs(repo, srefs)
        return DeleteRefsResponse()

    def ListBranchNamesContainingCommit(
            self,
            request: ListBranchNamesContainingCommitRequest,
            context) -> ListBranchNamesContainingCommitResponse:
        repo = self.load_repo(request.repository, context)

        gl_branches_by_heads = {}
        for gl_branch, head in iter_gitlab_branches(repo):
            rev = head.rev()
            gl_branches_by_heads.setdefault(rev, []).append(gl_branch)

        repo = repo.unfiltered()
        heads = repo.revs(b'%ld and %s::', gl_branches_by_heads,
                          request.commit_id)
        # TODO SPEC since there's a limit, we'll have to know what is
        # the expected ordering.
        #
        # In Gitaly sources, this is in refnames.go, which in turns call
        # `git for-each-ref` without a `sort` option. Then according to
        # the man page:
        #  --sort=<key>
        #      A field name to sort on. Prefix - to sort in descending order
        #      of the value. When unspecified, refname is used.
        for chunk in chunked((gl_branch
                              for head in heads
                              for gl_branch in gl_branches_by_heads[head]),
                             limit=request.limit):
            yield ListBranchNamesContainingCommitResponse(
                branch_names=chunk)

    def ListTagNamesContainingCommit(
            self,
            request: ListTagNamesContainingCommitRequest,
            context) -> ListTagNamesContainingCommitResponse:
        # TODO support ordering, see similar method for branches
        repo = self.load_repo(request.repository, context)

        try:
            revs = repo.revs("%s:: and tag()", request.commit_id)
        except hgerror.FilteredRepoLookupError:
            revs = []

        tag_names = (name for rev in revs for name in repo[rev].tags()
                     if repo.tagtype(name) not in EXCLUDED_TAG_TYPES)
        for chunk in chunked(tag_names, limit=request.limit):
            yield ListTagNamesContainingCommitResponse(tag_names=chunk)

    def GetTagSignatures(self,
                         request: GetTagSignaturesRequest,
                         context) -> GetTagSignaturesResponse:
        not_implemented(context, issue=75)  # pragma no cover

    def GetTagMessages(self,
                       request: GetTagMessagesRequest,
                       context) -> GetTagMessagesResponse:
        """Return messages of the given tags.

        In Mercurial, all tags have messages, and these are descriptions
        of the changests that give them values.

        For now, we'll consider that the id of a tag is the nod id of the
        changeset that gives it its current value.
        """
        repo = self.load_repo(request.repository, context)
        # TODO check that the given id is indeed for a tag, i.e. a
        # changeset that affects .hgtags?
        for tag_id in request.tag_ids:
            yield GetTagMessagesResponse(tag_id=tag_id,
                                         message=repo[tag_id].description())

    def ListNewCommits(self, request, context):
        """Not relevant for Mercurial

        From ``ref.proto``:
            Returns commits that are only reachable from the ref passed

        But actually, the request has a ``commit_id`` field, and it's not
        ``bytes``, hence can't be used for a ref.

        The reference Gitaly implementation is in `list_new_commits.go`.
        It boils down to::

          git rev-list --not --all ^oid

        with ``oid`` being ``request.commit id`` (not really a ref, then).
        additional comment: "the added ^ is to negate the oid since there is
        a --not option that comes earlier in the arg list"

        Note that ``--all`` includes Git refs that are descendents of the
        given commit. In other words, the results are ancestors of the
        given commit that would be garbage collected unless they get a ref
        soon.

        In the whole of the GitLab FOSS code base (as of GitLab 12.10),
        this is used only in pre-receive changes checks, i.e, before any ref
        has been assigned to commits that are new, indeed.

        We'll need a Mercurial specific version of the pre-receive check
        anyway.

        With HGitaly, all Mercurial changesets are at least ancestors of
        a GitLab branch head, the only exception not being closed heads,
        which are not mapped, so the results should boil down to something like
        ``reverse(::x and ::(heads() and closed()))``
        """
        raise NotImplementedError(
            "Not relevant for Mercurial")  # pragma: no cover

    def ListNewBlobs(self, request, context):
        """Not relevant for Mercurial.

        This is the same as :meth:`ListNewCommits()`, returning the blobs.
        In Gitaly sources, this is done by adding ``--objects`` to the
        otherwise same call to ``git rev-list`` as for :meth:`ListNewCommits`.

        As of GitLab 12.10, this is used only in
        ``GitAccess#check_changes_size`` (enforcing size limits for pushes).
        """
        raise NotImplementedError(
            "Not relevant for Mercurial")  # pragma: no cover

    def iter_refs(self, repo, request: ListRefsRequest, context):
        """"Generator yielding refernece names and target shas.

        For very direct use in ListRefs and similar.
        """
        patterns = request.patterns

        refs = []
        if patterns == [b'refs/'] and len(repo):
            refs.append((b'ALL', ZERO_SHA_STR))
        if request.head:
            branch = get_default_gitlab_branch(repo)
            if branch is not None:
                head = gitlab_branch_head(repo, branch)
                if head is not None:
                    refs.append((b'HEAD', head.hex().decode('ascii')))
        if patterns == [GITLAB_BRANCH_REF_PREFIX]:
            refs.extend(iter_gitlab_branches_as_refs(repo, deref=False))
        elif patterns == [GITLAB_TAG_REF_PREFIX]:
            refs.extend(iter_gitlab_tags_as_refs(repo, deref=False))
        else:
            if patterns:
                patterns = tuple(pat.split(b'/') for pat in patterns)
            refs.extend(iter_gitlab_branches_as_refs(repo,
                                                     deref=False,
                                                     patterns=patterns))
            refs.extend(iter_gitlab_tags_as_refs(repo,
                                                 deref=False,
                                                 patterns=patterns))
            refs.extend(iter_gitlab_special_refs_as_refs(repo,
                                                         deref=False,
                                                         patterns=patterns))
            refs.extend(iter_keep_arounds_as_refs(repo,
                                                  deref=False,
                                                  patterns=patterns))

        pointing_at = request.pointing_at_oids
        if pointing_at:
            refs = [r for r in refs
                    if r[1].encode('ascii') in pointing_at or r[0] == b'HEAD']

        # ignore `peel_tags`:
        # Mercurial has no real equivalent of Git's annotated tags. The
        # closest notion would be the tagging changeset, but that is not
        # well-defined. Hence Mercurial tags always point to the target commit.
        # We could force the `peeled_target` attribute of the `Reference`
        # messages, but that would not bring us to better compliance: the
        # protocol comment states explicitely that it should stay empty if
        # the object is not an annotated tag, and this is confirmed by
        # Gitaly Comparison tests (tag created by hg-git in this case).
        # On the contrary, filling-in `peeled_target` could very well make
        # clients believe that the tag is annotated, leading to dedicated
        # actions that can only go wrong.

        if len(refs) < (2 if request.head else 1):
            # avoid yielding an empty response, as Gitaly does not.
            # TODO consider doing that in the `chunked()` helper,
            # this looks to be rather systematic.
            # also in this case, even if `head` is `True`, in the Gitaly
            # impl, it looks like nothing being read from Git does not
            # trigger any sending, even though the sender created by
            # `newListRefsWriter` would emit HEAD first in any case… if it
            # emitted anything. See Gitaly Comparison test for validation of
            # this.
            return

        sort_by = request.sort_by
        if sort_by.key == ListRefsRequest.SortBy.Key.REFNAME:
            sort_key_fun = None
        else:
            # Some references can point to obsolete changesets
            # (e.g, keep-arounds). In any case it is certainly not the
            # role of this method to prevent one to do so.
            unfi = repo.unfiltered()

            # all other choices are about dates, and we have no other choice
            # that conflating them with the commit date of the ref target
            def sort_key_fun(ref_tuple):
                sha = ref_tuple[1]
                return unfi[sha].date()

        refs.sort(key=sort_key_fun,
                  reverse=sort_by.direction == SortDirection.DESCENDING)

        for chunk in chunked(refs):
            yield chunk

    def ListRefs(self, request: ListRefsRequest,
                 context) -> ListRefsResponse:
        repo = self.load_repo(request.repository, context)
        Reference = ListRefsResponse.Reference
        for chunk in self.iter_refs(repo, request, context):
            yield ListRefsResponse(
                references=(Reference(name=name, target=target)
                            for name, target in chunk))

    def FindRefsByOID(self, request: FindRefsByOIDRequest,
                      context) -> FindRefsByOIDResponse:
        repo = self.load_repo(request.repository, context)
        oid = request.oid.encode('utf8')
        if not CHANGESET_HASH_BYTES_REGEXP.match(oid):
            # a bit wider than needed, would probably be more
            # efficient to query nodemap directly, but we'll consider this
            # the day we reimplement in RHGitaly
            oid = gitlab_revision_hash(repo, oid)
        sort_by = FIND_REFS_BY_OID_SORT_FIELD_TO_LIST_REFS.get(
            request.sort_field, ListRefsRequest.SortBy.REFNAME)

        patterns = request.ref_patterns
        if patterns:
            patterns = [pat.encode('utf8') for pat in patterns]
        else:
            patterns = [b'refs/heads/', b'refs/tags/']

        limit = request.limit
        if limit == 0:  # said to mean no limit in protocol comment
            limit = None

        refs = []
        for chunk in chunked_limit(self.iter_refs(
                repo,
                ListRefsRequest(
                    repository=request.repository,
                    pointing_at_oids=[oid],
                    patterns=patterns,
                    sort_by=ListRefsRequest.SortBy(key=sort_by),
                ),
                context), limit):
            refs.extend(name for name, _tgt in chunk)
        return FindRefsByOIDResponse(refs=refs)


def gitlab_tag_from_ref(ref):
    if ref.startswith(GITLAB_TAG_REF_PREFIX):
        return ref[len(GITLAB_TAG_REF_PREFIX):]


def remove_special_refs(special_refs, to_remove):
    """Remove given elements of the ``special_refs`` mapping.

    :param dict special_refs: the special refs to remove from, whose keys
       are the shortened special ref name.
    :param to_remove: iterable of full ref names to remove.
    :returns: ``None`` if ok, else an error message.

    It is not an error to remove an absent ref, but it is one to request
    removal of a ref that is not a special ref.
    """
    for ref in to_remove:
        name = parse_special_ref(ref)
        if name is None:
            return (
                "Only special refs, such as merge-requests (but "
                "not keep-arounds) can be directly deleted in Mercurial, "
                "got %r" % ref)
        special_refs.pop(name, None)


def special_refs_matching_prefixes(special_refs, prefixes):
    """Return a sub-mapping of special refs matching given prefixes

    :param prefixes: given as full ref names, e.g. `refs/pipelines`.
        Any such prefix that would not be a special ref is simply ignored.
    """
    # Don't use parse_special_ref here, even if tempting: it would
    # not accept prefixes without trailing slashes, such as `refs/pipelines`
    # nor more partial prefixes, such as `refs/pipe`. Currently all used
    # prefixes are full with trailing slash, but if upstream developers
    # ever use a more partial prefix, this would result in data loss
    short_prefixes = {pref[5:] for pref in prefixes
                      if pref.startswith(b'refs/')}

    return {name: target for name, target in special_refs.items()
            if any(name.startswith(prefix) for prefix in short_prefixes)}
