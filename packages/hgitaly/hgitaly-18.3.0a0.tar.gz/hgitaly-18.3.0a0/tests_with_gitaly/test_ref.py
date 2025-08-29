# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from base64 import b64encode, b64decode
import pytest
import time

import py.path
from hgext3rd.heptapod.branch import set_default_gitlab_branch
from hgext3rd.heptapod.keep_around import (
    KEEP_AROUND_REF_PREFIX,
)
from hgext3rd.heptapod.special_ref import (
    special_refs,
)
from hgitaly.revision import (
    ZERO_SHA,
)
from hgitaly.stub.shared_pb2 import (
    PaginationParameter,
)
from hgitaly.stub.commit_pb2 import (
    FindCommitRequest,
)
from hgitaly.stub.ref_pb2 import (
    FindBranchRequest,
    FindDefaultBranchNameRequest,
    FindRefsByOIDRequest,
    FindTagError,
    FindTagRequest,
    FindAllBranchesRequest,
    FindAllTagsRequest,
    FindLocalBranchesRequest,
    ListRefsRequest,
    UpdateReferencesError,
    UpdateReferencesRequest,
    DeleteRefsRequest,
    RefExistsRequest,
)
from hgitaly.stub.shared_pb2 import (
    SortDirection,
)
from hgitaly.stub.ref_pb2_grpc import RefServiceStub
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from . import skip_comparison_tests
from .comparison import (
    normalize_commit_message,
)
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip

parametrize = pytest.mark.parametrize


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_branch(gitaly_rhgitaly_comparison,
                             hg_server):
    fixture = gitaly_rhgitaly_comparison
    git_repo = fixture.git_repo

    fixture.hg_repo_wrapper.write_commit('foo', message="Some foo")
    gl_branch = b'branch/default'

    # mirror worked
    assert git_repo.branch_titles() == {gl_branch: b"Some foo"}

    def normalize_response(rpc_helper, resp, **kw):
        normalize_commit_message(resp.branch.target_commit)

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindBranch',
        request_cls=FindBranchRequest,
        response_sha_attrs=['branch.target_commit.id'],
        normalizer=normalize_response,
    )

    rpc_helper.assert_compare(name=gl_branch)
    rpc_helper.assert_compare(name=b'unknown')

    # invalid case
    rpc_helper.assert_compare_errors(name=gl_branch, repository=None,
                                     same_details=False)


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_update_references(gitaly_rhgitaly_comparison,
                           server_repos_root,
                           hg_server):
    fixture = gitaly_rhgitaly_comparison
    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='UpdateReferences',
        streaming_request_field='updates',
        request_sha_attrs=['updates[].old_object_id',
                           'updates[].new_object_id'],
        request_cls=UpdateReferencesRequest,
    )
    Update = UpdateReferencesRequest.Update

    def ref_exists(vcs, ref):
        # FindCommit resolves keep-arounds directly, without
        # even opening the file, hence we need something more
        # representative.
        if vcs == 'hg':
            repo = rpc_helper.comparison.hgitaly_repo
        else:
            repo = rpc_helper.comparison.gitaly_repo

        return rpc_helper.stubs[vcs].RefExists(
            RefExistsRequest(repository=repo, ref=ref)
        ).value

    def commit_normalizer(rpc_helper, response, **kw):
        if response.HasField('commit'):
            normalize_commit_message(response.commit)

    find_commit_helper = fixture.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='FindCommit',
        request_cls=FindCommitRequest,
        request_sha_attrs=['revision'],
        response_sha_attrs=['commit.id', 'commit.parent_ids[]'],
        normalizer=commit_normalizer,
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors
    error_to_git = rpc_helper.structured_errors_git_converter((
        dict(hg_field='reference_state_mismatch',
             subfields=('expected_object_id', 'actual_object_id')),
    ))

    errors_handler = dict(git_cls=UpdateReferencesError,
                          hg_cls=UpdateReferencesError,
                          to_git=error_to_git)

    wrapper = fixture.hg_repo_wrapper
    sha0 = wrapper.write_commit('afoo', message="Some foo").hex()
    sha1 = wrapper.write_commit('afoo', message="Some foo").hex()
    default_branch = b'branch/default'
    # Gitaly checks that it is a full hash (INVALID_ARGUMENT), so that is
    # guaranteed for impl
    default_rev = sha0

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {default_branch: b"Some foo"}

    pipeline_1 = b'refs/pipelines/1'

    # validation errors
    assert_compare_errors(  # not a sha
        updates=[Update(reference=pipeline_1, new_object_id=default_branch)]
    )

    assert_compare(
        updates=[Update(reference=pipeline_1, new_object_id=default_rev)]
    )
    assert ref_exists('hg', pipeline_1) == ref_exists('git', pipeline_1)
    find_commit_helper.assert_compare(revision=pipeline_1)

    # actual call and state errors
    assert_compare(updates=[Update(reference=pipeline_1,
                                   old_object_id=default_rev,
                                   new_object_id=sha0)])
    find_commit_helper.assert_compare(revision=pipeline_1)
    assert_compare_errors(updates=[Update(reference=pipeline_1,
                                   old_object_id=ZERO_SHA,
                                   new_object_id=default_rev)])
    find_commit_helper.assert_compare(revision=pipeline_1)
    assert_compare_errors(updates=[Update(reference=pipeline_1,
                                          old_object_id=sha1,
                                          new_object_id=sha0)],
                          structured_errors_handler=errors_handler)

    # edge case equivalent to no-op
    assert_compare(updates=[Update(reference=pipeline_1,
                                   old_object_id=sha0,
                                   new_object_id=sha0)])

    ka_ref0 = KEEP_AROUND_REF_PREFIX + sha0
    assert_compare(updates=[Update(reference=ka_ref0,
                                   new_object_id=sha0)])
    assert ref_exists('hg', ka_ref0)

    # Gitaly does not prevent wreaking havoc with keep-arounds
    # (not so surprising given that they are to be dropped).
    # Hence comparing errors when trying to change a keep-around
    # target does not work.

    assert_compare(updates=[Update(reference=ka_ref0,
                                   old_object_id=sha0,
                                   new_object_id=ZERO_SHA,
                                   )])
    assert not ref_exists('hg', ka_ref0)

    # unknown storage
    fixture.gitaly_repo.storage_name = 'unknown'
    fixture.hgitaly_repo.storage_name = 'unknown'
    assert_compare_errors(updates=[Update(reference=b'refs/pipelines/37',
                                          new_object_id=default_rev)],
                          same_details=False)


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_default_branch_name(gitaly_rhgitaly_comparison,
                                          hg_server):
    fixture = gitaly_rhgitaly_comparison
    git_repo = fixture.git_repo

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindDefaultBranchName',
        request_cls=FindDefaultBranchNameRequest,
    )

    # empty repo
    rpc_helper.assert_compare()

    fixture.hg_repo_wrapper.write_commit('foo', message="Some foo")
    gl_branch = b'branch/default'

    # mirror worked
    assert git_repo.branch_titles() == {gl_branch: b"Some foo"}

    rpc_helper.assert_compare()
    # invalid case
    rpc_helper.assert_compare_errors(repository=None,
                                     same_details=False)


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_default_branch_name_fallbacks(
        gitaly_rhgitaly_comparison,
        hg_server
):
    fixture = gitaly_rhgitaly_comparison
    git_repo = fixture.git_repo

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindDefaultBranchName',
        request_cls=FindDefaultBranchNameRequest,
    )

    # empty repo, but with default branch set
    branch_name = b'branch/maybe_later'
    set_default_gitlab_branch(fixture.hg_repo_wrapper.repo, branch_name)
    # git_repo.set_symref needs a `py.path` path, not a `pathlib.Path`
    git_repo = fixture.git_repo
    git_repo.path = py.path.local(git_repo.path)
    git_repo.set_symref('HEAD', 'refs/heads/' + branch_name.decode('ascii'))
    rpc_helper.assert_compare()

    # non-empty repo, Gitaly will return the first existing branch it finds
    # (actually works because mirroring/state_maintainer fixes the default
    # branch to be an existing one)
    fixture.hg_repo_wrapper.write_commit('foo', message="Some foo")
    gl_branch = b'branch/default'

    # mirror worked
    assert git_repo.branch_titles() == {gl_branch: b"Some foo"}
    rpc_helper.assert_compare()


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_ref_exists(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    wrapper = fixture.hg_repo_wrapper

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='RefExists',
        request_cls=RefExistsRequest,
        )

    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    # empty repo, when state files don't exist yet
    assert_compare(ref=b'refs/heads/branch/default')
    assert_compare(ref=b'refs/keep-around/' + b'1234' * 10)

    ctx0 = wrapper.commit_file('foo')
    wrapper.command('tag', b'start-tag', rev=ctx0.hex())
    ctx1 = wrapper.commit_file('foo', topic='sampletop')
    fixture.invalidate()

    mr_ref_path, _ = fixture.write_special_ref(b'merge-requests/2/train',
                                               ctx1.hex())
    hg_ka_ref_path, git_ka_ref_path = fixture.create_keep_around(ctx1.hex())

    assert_compare(ref=b'refs/heads/branch/default')
    assert_compare(ref=b'refs/heads/topic/default/sampletop')
    assert_compare(ref=b'refs/heads/not-found')
    assert_compare(ref=b'refs/tags/start-tag')
    assert_compare(ref=b'refs/tags/unknown-tag')
    assert_compare(ref=b'refs/merge-requests/2/train')
    assert_compare(ref=b'refs/merge-requests/3/head')  # result is False
    assert_compare(ref=b'refs/')
    assert_compare(ref=b'refs/tags')
    assert_compare(ref=b'refs/tags/')
    # assert_compare() not being able to convert the keep-around ref path from
    # Mercurial to Git on the fly, we need to go lower level
    hg_resp = rpc_helper.rpc('hg', ref=hg_ka_ref_path)
    git_resp = rpc_helper.rpc('git', ref=git_ka_ref_path)
    assert hg_resp == git_resp

    assert_compare(ref=b'refs/keep-around/not-even-a-hash')

    assert_compare_errors(ref=b'refs')
    assert_compare_errors(ref=b'HEAD')
    assert_compare_errors(ref=b'notrefs/something')


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_local_branches(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    wrapper = fixture.hg_repo_wrapper

    # make three branches with the 3 possible orderings differ
    now = time.time()
    commit_ages = {0: 30, 1: 40, 2: 20}
    for i in range(3):
        wrapper.commit_file('foo', branch='br%02d' % i, return_ctx=False,
                            utc_timestamp=now - commit_ages[i])
    # mirror worked
    assert set(fixture.git_repo.branch_titles().keys()) == {
        b'branch/br%02d' % i for i in range(3)}

    def normalize_response(rpc_helper, resp, **kw):
        for chunk in resp:
            for branch in chunk.local_branches:
                normalize_commit_message(branch.target_commit)

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindLocalBranches',
        request_cls=FindLocalBranchesRequest,
        streaming=True,
        response_sha_attrs=['local_branches[].target_commit.id',
                            'local_branches[].target_commit.parent_ids[]',
                            ],
        normalizer=normalize_response,
    )

    def assert_compare(limit=0, page_token='', pagination=True, **kw):
        if pagination:
            pagination_params = PaginationParameter(limit=limit,
                                                    page_token=page_token)
        else:
            pagination_params = None

        rpc_helper.assert_compare(pagination_params=pagination_params, **kw)

    for limit in (0, 3, 8, -1):
        assert_compare(limit=limit)

    # case without any pagination parameters
    assert_compare(123, pagination=False)

    orig_kwargs_to_git = rpc_helper.request_kwargs_to_git

    def pagination_kwargs_to_git(hg_kwargs):
        git_kwargs = orig_kwargs_to_git(hg_kwargs)
        hg_pagination = hg_kwargs['pagination_params']
        git_kwargs['pagination_params'] = PaginationParameter(
            limit=hg_pagination.limit,
            page_token=('refs/heads/'
                        + b64decode(hg_pagination.page_token).decode()),
        )
        return git_kwargs

    if hg_server == 'hgitaly':
        page_token = 'refs/heads/branch/br01'
    else:
        page_token = b64encode(b'branch/br01').decode('ascii')
        rpc_helper.request_kwargs_to_git = pagination_kwargs_to_git

    assert_compare(10, page_token=page_token)
    rpc_helper.request_kwargs_to_git = orig_kwargs_to_git

    # sort options
    for sort_by in FindLocalBranchesRequest.SortBy.values():
        assert_compare(10, sort_by=sort_by)


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_all_branches(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    wrapper = fixture.hg_repo_wrapper

    # make three branches with the 3 possible orderings differ
    now = time.time()
    commit_ages = {0: 30, 1: 40, 2: 20}
    for i in range(3):
        wrapper.commit_file('foo', branch='br%02d' % i, return_ctx=False,
                            utc_timestamp=now - commit_ages[i])
    # mirror worked
    assert set(fixture.git_repo.branch_titles().keys()) == {
        b'branch/br%02d' % i for i in range(3)}

    def normalize_response(rpc_helper, resp, **kw):
        for chunk in resp:
            for branch in chunk.branches:
                normalize_commit_message(branch.target)

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindAllBranches',
        request_cls=FindAllBranchesRequest,
        streaming=True,
        response_sha_attrs=['branches[].target.id',
                            'branches[].target.parent_ids[]',
                            ],
        normalizer=normalize_response,
    )

    rpc_helper.assert_compare()


# Testing just RHGitaly, as we would otherwise need to implement
# sorting in Python impl, that will be deprecated immediately by Rust impl
def test_find_all_tags(gitaly_rhgitaly_comparison):
    fixture = gitaly_rhgitaly_comparison
    hg_wrapper = fixture.hg_repo_wrapper

    # make three branches with the 3 possible orderings differ
    now = time.time()
    commit_ages = {0: 30, 1: 40, 2: 20}
    commit_tags = {0: b'1.2', 1: b'v0.8', 2: b'not-a-version'}
    for i in range(3):
        hg_wrapper.commit_file('foo', return_ctx=False,
                               utc_timestamp=now - commit_ages[i])
        hg_wrapper.command('tag', commit_tags[i], rev=b'.')
    hg_wrapper.command('gitlab-mirror')

    # mirror worked
    assert fixture.git_repo.tags() == {b'1.2', b'v0.8', b'not-a-version'}

    def normalize_response(rpc_helper, resp, **kw):
        for chunk in resp:
            for tag in chunk.tags:
                normalize_commit_message(tag.target_commit)

    rpc_helper = fixture.rpc_helper(
        hg_server='rhgitaly',
        stub_cls=RefServiceStub,
        method_name='FindAllTags',
        request_cls=FindAllTagsRequest,
        streaming=True,
        response_sha_attrs=['tags[].target_commit.id',
                            'tags[].target_commit.parent_ids[]',
                            'tags[].id',
                            ],
        normalizer=normalize_response,
    )

    rpc_helper.assert_compare()

    SortBy = FindAllTagsRequest.SortBy
    for direction in (SortDirection.ASCENDING, SortDirection.DESCENDING):
        for key in SortBy.Key.values():
            rpc_helper.assert_compare(
                sort_by=SortBy(key=key, direction=direction),
            )


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_find_tag(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    hg_wrapper = fixture.hg_repo_wrapper

    hg_wrapper.commit_file('foo')
    hg_wrapper.command('tag', b'v3.3', rev=b'.')
    hg_wrapper.command('gitlab-mirror')

    # mirror worked
    assert fixture.git_repo.tags() == {b'v3.3'}

    def normalize_response(rpc_helper, resp, **kw):
        normalize_commit_message(resp.tag.target_commit)
        # no tag ids in Mercurial until we can assign a tagging changeset
        # (requires a long-term core change)
        resp.tag.id = ''

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='FindTag',
        response_sha_attrs=['tag.target_commit.id'],
        request_cls=FindTagRequest,
        normalizer=normalize_response,
    )
    rpc_helper.assert_compare(tag_name=b'v3.3')

    # Fine structured errors comparison even though they are expected to
    # be identical, for coverage of comparison method in `RpcHelper`:
    errors_handler = dict(git_cls=FindTagError, to_git=lambda e: e)
    rpc_helper.assert_compare_errors(tag_name=b'nosuchtag',
                                     structured_errors_handler=errors_handler)


def test_delete_refs(gitaly_comparison):
    fixture = gitaly_comparison
    git_repo = fixture.git_repo
    hg_wrapper = fixture.hg_repo_wrapper

    base_hg_ctx = hg_wrapper.commit_file('foo')
    hg_sha = base_hg_ctx.hex()
    mr_ref_name = b'merge-requests/2/train'
    mr_ref_path, git_sha = fixture.write_special_ref(mr_ref_name, hg_sha)

    rpc_helper = fixture.rpc_helper(stub_cls=RefServiceStub,
                                    method_name='DeleteRefs',
                                    request_cls=DeleteRefsRequest)

    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare_errors(refs=[b'xy'], except_with_prefix=[b'refs/heads'])
    assert_compare(refs=[mr_ref_path])

    # unknown refs dont create errors
    fixture.write_special_ref(mr_ref_name, hg_sha)
    unknown = b'refs/environments/imaginary'
    assert_compare(refs=[unknown])

    # also mixing unknown with known is ok
    assert_compare(refs=[unknown, mr_ref_path])

    assert git_repo.all_refs() == {b'refs/heads/branch/default': git_sha}
    hg_wrapper.reload()
    assert special_refs(hg_wrapper.repo) == {}

    # using except_with_prefix
    env_ref_name = b'environments/2877'
    env_ref_path, _ = fixture.write_special_ref(env_ref_name, hg_sha)

    # on the Mercurial side, we'll consider the special ref only,
    # but on the Git side, the `refs/heads` prefix has to be ignored.
    # This is similar to what the current actual caller,
    # `Projects::AfterImportService`, does.
    for except_prefixes in (
            [b'refs/environments/', b'refs/heads/'],
            [b'refs/environments', b'refs/heads/'],
            [b'refs/envir', b'refs/heads/'],
            ):
        fixture.write_special_ref(mr_ref_name, hg_sha)
        fixture.write_special_ref(env_ref_name, hg_sha)

        assert_compare(except_with_prefix=except_prefixes)
        assert git_repo.all_refs() == {b'refs/heads/branch/default': git_sha,
                                       env_ref_path: git_sha}
        hg_wrapper.reload()
        assert special_refs(hg_wrapper.repo) == {env_ref_name: hg_sha}


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_list_refs(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    hg_wrapper = fixture.hg_repo_wrapper

    def normalize_refs(rpc_helper, resps, vcs=None):
        if vcs != 'hg':
            return

        prefix = b'refs/keep-around/'

        for resp in resps:
            all_pseudo_ref_idx = None
            for i, ref_msg in enumerate(resp.references):
                if ref_msg.name == b'ALL' and rpc_helper.norm_all_pseudo_ref:
                    all_pseudo_ref_idx = i
                if ref_msg.name.startswith(prefix):
                    ref_msg.name = prefix + rpc_helper.hg2git(
                        ref_msg.name[len(prefix):])
            if all_pseudo_ref_idx is not None:
                del resp.references[all_pseudo_ref_idx]

    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RefServiceStub,
        method_name='ListRefs',
        request_cls=ListRefsRequest,
        request_defaults=dict(patterns=[b"refs/"], head=True),
        streaming=True,
        request_sha_attrs=['pointing_at_oids[]'],
        response_sha_attrs=['references[].target'],
        normalizer=normalize_refs,
    )
    rpc_helper.norm_all_pseudo_ref = True
    # empty repo, in particular no default GitLab branch (HEAD)
    rpc_helper.assert_compare()

    # make three changesets on which the 3 possible orderings differ
    # (in Mercurial committer and author dates are the same)
    now = time.time()
    commit_ages = {0: 30, 1: 40, 2: 20}
    hg_sha = hg_wrapper.commit_file('bar').hex()

    # branches
    hg_shas = []
    for i in range(3):
        hg_shas.append(
            hg_wrapper.commit_file('foo', branch='br%02d' % i,
                                   utc_timestamp=now - commit_ages[i]).hex()
        )
    rpc_helper.assert_compare()
    for head in False, True:
        rpc_helper.assert_compare(patterns=[b'refs/heads/'], head=head)

    # with tags
    hg_wrapper.command('tag', b'v3.1', rev=b'br01')
    hg_wrapper.command('gitlab-mirror')
    fixture.invalidate()
    rpc_helper.assert_compare()
    for head in False, True:
        rpc_helper.assert_compare(patterns=[b'refs/heads/'], head=head)
        rpc_helper.assert_compare(patterns=[b'refs/tags/'], head=head)

    # now with special refs
    fixture.write_special_ref(b'pipeline/13', hg_sha)
    rpc_helper.assert_compare()
    for head in False, True:
        rpc_helper.assert_compare(patterns=[b'refs/heads/'], head=head)
        rpc_helper.assert_compare(patterns=[b'refs/tags/'], head=head)

    # with a keep around
    fixture.create_keep_around(hg_sha)
    rpc_helper.assert_compare()
    for head in False, True:
        rpc_helper.assert_compare(patterns=[b'refs/heads/'], head=head)
        rpc_helper.assert_compare(patterns=[b'refs/tags/'], head=head)

    # more general patterns
    rpc_helper.norm_all_pseudo_ref = False
    for head in False, True:
        # notice how HEAD is ignored by pattern matching
        rpc_helper.assert_compare(patterns=[b'refs/heads/branch/br*'],
                                  head=head)

        # 'branch/something' should not match `br*` and special case of
        # HEAD not being part of response if nothing matches
        rpc_helper.assert_compare(patterns=[b'refs/heads/br*'], head=head)

    # trailing slash is stricly prefixing (no wildcards)
    rpc_helper.assert_compare(patterns=[b'refs/h*s/'])

    # if wildcards are interpreted, they can be in any segment, yet do not
    # match slashes and need equal numbers of segment (no prefixing by pattern)
    rpc_helper.assert_compare(patterns=[b'refs/h*s/branch/br*'])  # matching
    rpc_helper.assert_compare(patterns=[b'refs/*/br*'])  # not matching slash
    rpc_helper.assert_compare(patterns=[b'refs/*/branch'])  # prefixing case

    # logical conjunction of several patterns
    rpc_helper.assert_compare(patterns=[b'refs/heads/branch/br*',
                                        b'refs/heads/branch/d*'],
                              head=head)

    # no error that we can think of would be specific of this gRPC method

    # pointing_at_oids
    for head in False, True:
        rpc_helper.assert_compare(pointing_at_oids=[hg_shas[0]], head=head)
        rpc_helper.assert_compare(pointing_at_oids=[hg_shas[0], hg_shas[1]],
                                  head=head)
        # together with patterns
        for i in range(3):
            # empty result if `i == 0 and not head`
            rpc_helper.assert_compare(pointing_at_oids=[hg_shas[i]],
                                      patterns=[b'refs/tags/'],
                                      head=head)

    # sorting by date (not so important to be exactly as in Gitaly, we have
    # less date fields anyway, but the point is to test that RHGitaly works)
    rpc_helper.norm_all_pseudo_ref = True
    SortBy = ListRefsRequest.SortBy
    for direction in (SortDirection.ASCENDING, SortDirection.DESCENDING):
        rpc_helper.assert_compare(
            sort_by=SortBy(key=SortBy.AUTHORDATE,
                           direction=direction),
            patterns=[b"refs/heads/branch/br*"],
            head=False,
        )

    # FindRefsByOID is almost a subset of ListRefs, the only stated
    # thing that ListRefs would not do is accepting oids by prefix.
    # So we'll use the same setup

    rpc_helper = fixture.rpc_helper(
        stub_cls=RefServiceStub,
        method_name='FindRefsByOID',
        request_cls=FindRefsByOIDRequest,
        request_defaults=dict(ref_patterns=["refs/"]),
        request_sha_attrs=['oid'],
    )

    hg_short_shas = [sha[:12] for sha in hg_shas]
    git_short_shas = [rpc_helper.hg2git(sha)[:12] for sha in hg_shas]
    fixture.hg_git._map_hg.update(zip(hg_short_shas, git_short_shas))

    # no need to proceed further if this fails:
    assert rpc_helper.hg2git(hg_short_shas[1]) == git_short_shas[1]

    for hg_sha in hg_shas + hg_short_shas:
        for patterns in (
                ['refs/tags/'],
                ['refs/heads/'],
                [],
                ):
            rpc_helper.assert_compare(oid=hg_sha.decode(),
                                      ref_patterns=patterns)

    # hg_shas[1] has two refs (a branch and a tag)
    for limit in (0, 1, 2):
        rpc_helper.assert_compare(oid=hg_shas[1].decode(), limit=limit)
