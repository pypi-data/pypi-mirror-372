# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for OperationService (most mutations)

Because it is not convenient to mutate the Mercurial and Git repositories
Without side-effects, these tests are mostly checking assumptions on the
behaviour of Gitaly
"""
from io import BytesIO
from pathlib import Path
import pytest

from grpc import RpcError

from hgitaly.stub.shared_pb2 import User

from hgitaly.stub.mercurial_operations_pb2 import (
    MercurialPermissions,
    MergeBranchError,
    MergeBranchRequest,
)
from hgitaly.stub.mercurial_operations_pb2_grpc import (
    MercurialOperationsServiceStub,
)
from hgitaly.stub.errors_pb2 import (
    MergeConflictError,
    ReferenceUpdateError,
)
from hgitaly.stub.operations_pb2 import (
    OperationBranchUpdate,
    UserCommitFilesAction,
    UserCommitFilesActionHeader,
    UserCommitFilesRequest,
    UserCommitFilesRequestHeader,
    UserFFBranchError,
    UserFFBranchRequest,
    UserMergeBranchError,
    UserMergeBranchRequest,
    UserSquashRequest,
)
from hgitaly.stub.operations_pb2_grpc import (
    OperationServiceStub,
)

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip

parametrize = pytest.mark.parametrize

TESTS_DATA_DIR = Path(__file__).parent / 'data'
TIP_TAG_NAME = b'tip'
PUBLISH_PERM = MercurialPermissions.PUBLISH


@pytest.fixture
def comparison(gitaly_comparison):
    gitaly_comparison.user = User(gl_id='user-37',
                                  name=b'Test User',
                                  email=b'testuser@heptapod.test',
                                  gl_username='testuser')
    yield gitaly_comparison


def test_compare_squash(comparison):
    """This test is mostly about error cases, as comparing the """
    fixture = comparison
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_branch = b'branch/default'
    gl_topic = b'topic/default/sampletop'
    wrapper.write_commit('foo')
    wrapper.write_commit('zoo', topic='sampletop')
    wrapper.write_commit('bar')

    rpc_helper = fixture.rpc_helper(stub_cls=OperationServiceStub,
                                    method_name='UserSquash',
                                    request_cls=UserSquashRequest,
                                    request_defaults=dict(
                                        user=fixture.user,
                                        author=fixture.user,
                                        commit_message=b'squashed'),
                                    request_sha_attrs=['start_sha', 'end_sha'])
    assert_compare_errors = rpc_helper.assert_compare_errors
    # proof that any valid revspec can be passed as "sha" arguments
    git_resp = rpc_helper.call_git_only(start_sha=gl_branch, end_sha=gl_topic)
    squashed_sha = git_resp.squash_sha
    # Gitaly does not move the ref, apparently
    assert git_repo.commit_hash_title(squashed_sha) == [
        squashed_sha.encode('ascii'),
        b'squashed'
    ]

    # revision resolution errors
    assert_compare_errors(start_sha='unresolvable', end_sha=gl_topic)
    assert_compare_errors(start_sha=gl_branch, end_sha='unresolvable')

    # errors on missing arguments
    assert_compare_errors(start_sha=gl_topic)
    assert_compare_errors(end_sha=gl_topic)
    assert_compare_errors(user=None, start_sha=gl_branch, end_sha=gl_topic)
    assert_compare_errors(commit_message=None,
                          start_sha=gl_branch, end_sha=gl_topic)
    assert_compare_errors(author=None, start_sha=gl_branch, end_sha=gl_topic)


def test_compare_ff_branch(comparison):
    """Mostly testing error cases, as comparing results is unpractical.

    Once the Mercurial fast-forward is done, there is nothing to be done
    on the Git side.
    """
    fixture = comparison
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_branch = b'branch/default'
    gl_topic = b'topic/default/sampletop'
    ctx0 = wrapper.write_commit('foo')
    sha0 = ctx0.hex()
    sha1 = wrapper.write_commit('foo').hex()
    ctx2 = wrapper.write_commit('zoo', topic='sampletop')
    sha2 = ctx2.hex()
    git_sha2 = git_repo.branches()[gl_topic]['sha']
    ctx_old = wrapper.write_commit('old', parent=ctx0, topic='needs-rebase')

    rpc_helper = fixture.rpc_helper(
        stub_cls=OperationServiceStub,
        method_name='UserFFBranch',
        error_details_normalizer=lambda s, **kw: s.lower(),
        request_cls=UserFFBranchRequest,
        request_defaults=dict(user=fixture.user),
        request_sha_attrs=['commit_id',
                           'expected_old_oid'],
    )
    assert_compare_errors = rpc_helper.assert_compare_errors

    def error_to_git(merge_error):
        if merge_error.HasField('reference_update'):
            upd_error = merge_error.reference_update
            git_upd_error = ReferenceUpdateError(
                reference_name=upd_error.reference_name,
                old_oid=rpc_helper.hg2git(upd_error.old_oid),
                new_oid=rpc_helper.hg2git(upd_error.new_oid),
            )
            return UserFFBranchError(reference_update=git_upd_error)

        raise NotImplementedError("unexpected variant")  # pragma no cover

    # A working Gitaly call, as a baseline that cannot be directly compared.
    git_resp = rpc_helper.call_git_only(branch=gl_branch,
                                        commit_id=sha2,
                                        expected_old_oid=sha1,
                                        )
    assert git_resp.branch_update == OperationBranchUpdate(
        commit_id=git_sha2,
        repo_created=False,
        branch_created=False,
    )
    assert git_repo.commit_hash_title('branch/default')[0] == git_sha2

    # revision resolution errors
    unknown_sha = '2134cafe' * 5
    assert_compare_errors(commit_id=unknown_sha,
                          expected_old_oid=sha0.decode(),
                          branch=gl_branch)
    assert_compare_errors(commit_id='not-an-id',
                          same_details=False,
                          expected_old_oid=sha0.decode(),
                          branch=gl_branch)
    assert_compare_errors(commit_id=sha2,
                          same_details=False,
                          expected_old_oid='not-an-id',
                          branch=gl_branch)
    assert_compare_errors(commit_id=sha2,
                          expected_old_oid=unknown_sha,
                          branch=gl_branch)

    # expected_old_oid mismatch
    assert_compare_errors(commit_id=sha2,
                          expected_old_oid=sha0,
                          branch=gl_branch,
                          same_details=False,
                          structured_errors_handler=dict(
                              git_cls=UserFFBranchError,
                              to_git=error_to_git,
                          ))

    # errors on missing arguments
    assert_compare_errors(commit_id=sha2)
    assert_compare_errors(user=None, branch=gl_branch, commit_id=sha2)

    # Not a fast-forward
    assert_compare_errors(commit_id=ctx_old.hex().decode(),
                          branch=gl_branch)


def test_compare_user_merge_branch(comparison):
    """Mostly testing error cases, as comparing results is unpractical.

    Once the Mercurial merge is done, there is nothing to be done
    on the Git side, and it is not clear it would give the very same hash.
    """
    fixture = comparison
    wrapper = fixture.hg_repo_wrapper

    rpc_helper = fixture.rpc_helper(
        stub_cls=MercurialOperationsServiceStub,
        method_name='MergeBranch',
        error_details_normalizer=lambda s, **kw: s.lower(),
        request_cls=MergeBranchRequest,
        request_defaults=dict(user=fixture.user, hg_perms=PUBLISH_PERM),
        request_sha_attrs=['commit_id',
                           'expected_old_oid'],
    )

    git_stub = OperationServiceStub(comparison.gitaly_channel)

    def git_merge(**git_kwargs):
        # TODO second request but we may not need it
        del git_kwargs['hg_perms']
        resps = git_stub.UserMergeBranch(iter([
            UserMergeBranchRequest(**git_kwargs),
            UserMergeBranchRequest(apply=True, **git_kwargs)
        ]))
        return [r for r in resps]

    error_to_git = rpc_helper.structured_errors_git_converter(
        (dict(hg_field='conflict',
              git_field='merge_conflict',
              git_cls=MergeConflictError,
              subfields=['conflicting_commit_ids[]']),
         dict(hg_field='reference_check',
              git_field='reference_update',
              git_cls=ReferenceUpdateError,
              subfields=['old_oid']),
         ),
        error_git_cls=UserMergeBranchError
    )

    def error_normalizer(error):
        if not error.HasField('reference_update'):
            return

        # `new_oid` in reference update error is about the merge commit,
        # already created, before moving the Git branch to it.
        # There is nothing alike on
        # the Mercurial side (unless we implement the same logic for bookmarks
        # but that seems unlikely)
        error.reference_update.new_oid = ''

    def assert_compare_errors(same_details=True, **hg_kwargs):
        rpc_helper.apply_request_defaults(hg_kwargs)
        git_kwargs = rpc_helper.request_kwargs_to_git(hg_kwargs)
        git_kwargs.setdefault('repository', comparison.gitaly_repo)

        with pytest.raises(RpcError) as exc_info_hg:
            rpc_helper.rpc('hg', **hg_kwargs)
        with pytest.raises(RpcError) as exc_info_git:
            git_merge(**git_kwargs)
        rpc_helper.assert_compare_grpc_exceptions(
            exc_info_hg.value,
            exc_info_git.value,
            structured_errors_handler=dict(hg_cls=MergeBranchError,
                                           git_cls=UserMergeBranchError,
                                           normalizer=error_normalizer,
                                           to_git=error_to_git),
            same_details=same_details
        )

    gl_branch = b'branch/default'
    ctx0 = wrapper.write_commit('foo')
    sha0 = ctx0.hex()
    wrapper.write_commit('foo').hex()
    ctx2 = wrapper.write_commit('zoo', topic='sampletop')
    sha2 = ctx2.hex()
    ctx_conflict = wrapper.write_commit('foo', parent=ctx0, topic='conflict')

    # Conflict
    assert_compare_errors(branch=gl_branch,
                          commit_id=ctx_conflict.hex().decode(),
                          message=b"Will not merge")

    # revision resolution errors
    unknown_sha = '2134cafe' * 5
    assert_compare_errors(commit_id=unknown_sha,
                          expected_old_oid=sha0.decode(),
                          branch=gl_branch)
    assert_compare_errors(commit_id='not-an-id',
                          same_details=False,
                          expected_old_oid=sha0.decode(),
                          branch=gl_branch)
    assert_compare_errors(commit_id=sha2,
                          same_details=False,
                          expected_old_oid='not-an-id',
                          branch=gl_branch)
    assert_compare_errors(commit_id=sha2,
                          expected_old_oid=unknown_sha,
                          branch=gl_branch)

    # expected_old_oid mismatch
    assert_compare_errors(commit_id=sha2,
                          expected_old_oid=sha0,
                          message=b"msg",
                          same_details=True,
                          branch=gl_branch)

    # errors on missing arguments
    assert_compare_errors(commit_id=sha2)
    assert_compare_errors(user=None, branch=gl_branch, commit_id=sha2)

    # Conflict
    assert_compare_errors(commit_id=ctx_conflict.hex().decode(),
                          branch=gl_branch)


def ucf_actions(action):
    content = action.pop('content', None)
    requests = [dict(
        action=UserCommitFilesAction(
            header=UserCommitFilesActionHeader(**action))
    )]
    if content is not None:
        # we make one message per line for testing purposes,
        # but we avoid splitlines() as it removes line separators.
        # we could re-add them but that would make life difficult
        # for (future) tests about EOL normalization.
        lines = BytesIO(content).readlines()

        requests.extend(dict(action=UserCommitFilesAction(content=line))
                        for line in lines)
    return requests


def test_compare_commit_files(comparison):
    """This test is mostly about error cases

    comparing the results would be tedious and pointless.
    """
    fixture = comparison
    wrapper = fixture.hg_repo_wrapper
    # We do not want to touch the Git repository when updating state files
    # TODO this should be unnecessary now, but be careful, as py-heptapod
    # must stay able to make cases for other Comparison Tests and handle
    # Git push-mirrors.
    wrapper.setconfig(b'heptapod', b'native', True)

    gl_branch = b'branch/default'

    def normalizer(rpc_helper, response, **kw):
        if response.branch_update.commit_id:
            # we do not care about actually comparing commits
            # only that they both exist or both don't
            response.branch_update.commit_id = 'present'

    rpc_helper = fixture.rpc_helper(
        stub_cls=OperationServiceStub,
        method_name='UserCommitFiles',
        request_cls=UserCommitFilesRequest,
        streaming_requests_with_header=('header',
                                        UserCommitFilesRequestHeader),
        normalizer=normalizer,
        request_defaults=dict(
            user=fixture.user,
            commit_author_name=fixture.user.name,
            commit_author_email=fixture.user.email,
            branch_name=gl_branch,
            commit_message=b"A commit",
        ),
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    ActionType = UserCommitFilesActionHeader.ActionType

    assert_compare(
        branch_name=b'branch/default',
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'/foo',
            content=b'foo content')),
    )

    # file creation can create sub directory
    assert_compare(
        branch_name=b'branch/default',
        commit_message=b"Implicit dir creation",
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'existing/bar',
            content=b'bar in existing dir')),
    )

    # updating state files for relevance of subsequent tests
    wrapper.command('gitlab-mirror')

    # missing branch specification and unknown start branch
    assert_compare_errors(
        branch_name=b'',
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'bar',
            content=b'bar content')),
    )
    assert_compare_errors(
        same_details=False,
        start_branch_name=b'branch/unknown',
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'bar',
            content=b'bar content')),
    )

    # wrong start oid
    assert_compare_errors(
        same_details=False,
        expected_old_oid=b'85fa6e7c' * 5,
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'bar',
            content=b'bar content')),
    )

    # file already exists
    assert_compare_errors(
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE,
            file_path=b'foo',
            content=b'refoo')),
    )

    # directory already exists
    assert_compare_errors(
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE_DIR,
            file_path=b'existing')),
    )

    # directory name already taken by a file
    assert_compare_errors(
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE_DIR,
            file_path=b'foo')),
    )

    # successful directory creation
    assert_compare(
        tail_requests=ucf_actions(dict(
            action=ActionType.CREATE_DIR,
            file_path=b'new-dir')),
    )

    # update on a file that does not exist
    assert_compare_errors(
        tail_requests=ucf_actions(dict(
            action=ActionType.UPDATE,
            file_path=b'not-yet',
            content=b'try again')),
    )

    # chmod and delete on a file that does not exist
    for action in (ActionType.CHMOD, ActionType.DELETE):
        assert_compare_errors(
            tail_requests=ucf_actions(dict(
                action=action,
                file_path=b'not-yet',
                execute_filemode=True,
                )))

    # move edge cases
    assert_compare_errors(
        same_details=False,
        tail_requests=ucf_actions(dict(  # source file does not exist
            action=ActionType.MOVE,
            file_path=b'target',
            previous_path=b'unknown',
        ))
    )
    assert_compare(
        branch_name=b"topic/default/move-success",
        start_branch_name=b"branch/default",
        tail_requests=ucf_actions(dict(
            action=ActionType.MOVE,
            file_path=b'created-by-move/foo',
            previous_path=b'foo',
        ))
    )
    assert_compare_errors(  # target file already exists
        tail_requests=ucf_actions(dict(
            action=ActionType.MOVE,
            file_path=b'existing/bar',
            previous_path=b'foo',
        ))
    )

    # invalid path
    for path in ('double//slash', '../../../good.joke'):
        for action in ('CREATE', 'CREATE_DIR', 'CHMOD',
                       'UPDATE', 'DELETE', 'MOVE'):
            assert_compare_errors(
                same_details=False,
                tail_requests=ucf_actions(dict(
                    action=getattr(ActionType, action),
                    file_path=path.encode(),
                    previous_path=b'something',  # for MOVE only
                )))
        assert_compare_errors(
            same_details=False,
            tail_requests=ucf_actions(dict(
                action=getattr(ActionType, action),
                previous_path=path.encode(),
                file_path=b'ignored-target',
            )))

    # content before action header
    assert_compare_errors(
        tail_requests=[dict(
            action=UserCommitFilesAction(content=b"stray content"))])

    # two general headers!
    assert_compare_errors(
        tail_requests=[dict(header=UserCommitFilesRequestHeader())])

    # wrong ordering of requests
    rpc_helper.streaming_requests_with_header = None
    rpc_helper.streaming_requests_raw = True
    assert_compare_errors(
        requests=[UserCommitFilesRequest(action=UserCommitFilesAction())]
    )
