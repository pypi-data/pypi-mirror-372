# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import (
    RpcError,
    StatusCode,
)
import pytest
import uuid

from mercurial import (
    error as hg_error,
    phases,
)
from mercurial_testhelpers import RepoWrapper

from google.protobuf.timestamp_pb2 import Timestamp

from hgext3rd.heptapod.branch import (
    gitlab_branches,
)

from hgitaly.changelog import ancestor
from hgitaly.errors import (
    parse_assert_structured_error,
)
from hgitaly.identification import INCARNATION_ID
from hgitaly.servicer import (
    PY_HEPTAPOD_SKIP_HOOKS,
)
from hgitaly.stub.errors_pb2 import (
    ReferenceUpdateError,
)
from hgitaly.stub.mercurial_operations_pb2 import (
    CensorRequest,
    MergeBranchError,
    MergeBranchRequest,
    MercurialPermissions,
    PreCheckUpdateError,
    PublishChangesetRequest,
    MergeAnalysisRequest,
    MergeAnalysisResponse,
    GetWorkingDirectoryRequest,
    ReleaseWorkingDirectoryRequest,
)
from hgitaly.stub.mercurial_operations_pb2_grpc import (
    MercurialOperationsServiceStub,
)
from hgitaly.tests.common import make_empty_repo_with_gitlab_state_maintainer
from .fixture import MutationServiceFixture

parametrize = pytest.mark.parametrize

WRITE_PERM = MercurialPermissions.WRITE
PUBLISH_PERM = MercurialPermissions.PUBLISH


class OperationsFixture(MutationServiceFixture):

    stub_cls = MercurialOperationsServiceStub

    client_id = str(uuid.uuid4())

    def merge_analysis(self, **kw):
        return self.stub.MergeAnalysis(MergeAnalysisRequest(
            repository=self.grpc_repo, **kw))

    def publish(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.PublishChangeset(PublishChangesetRequest(**kw),
                                          metadata=self.grpc_metadata())

    def censor(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.Censor(CensorRequest(**kw),
                                metadata=self.grpc_metadata())

    def merge_branch(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.MergeBranch(MergeBranchRequest(**kw),
                                     metadata=self.grpc_metadata())

    def get_workdir(self, **kw):
        kw.setdefault('client_id', self.client_id)
        kw.setdefault('incarnation_id', INCARNATION_ID)
        kw.setdefault('repository', self.grpc_repo)
        return self.stub.GetWorkingDirectory(
            GetWorkingDirectoryRequest(**kw))

    def release_workdir(self, **kw):
        kw.setdefault('client_id', self.client_id)
        kw.setdefault('repository', self.grpc_repo)
        return self.stub.ReleaseWorkingDirectory(
            ReleaseWorkingDirectoryRequest(**kw))


@pytest.fixture
def operations_fixture(grpc_channel, server_repos_root):
    with OperationsFixture(
            grpc_channel, server_repos_root,
            repo_factory=make_empty_repo_with_gitlab_state_maintainer,
    ) as fixture:
        yield fixture


def test_merge_analysis_ff(operations_fixture):
    repo_wrapper = operations_fixture.repo_wrapper
    commit_file = repo_wrapper.commit_file
    default_ctx = commit_file('foo')
    default_sha = default_ctx.hex().decode()
    topic_ctx = commit_file('foo', parent=default_ctx, topic='zetop')
    topic_first_hex = topic_ctx.hex()
    topic_first_sha = topic_first_hex.decode()

    merge_analysis = operations_fixture.merge_analysis
    assert (
        merge_analysis(source_revision=b'topic/default/zetop',
                       target_revision=b'branch/default')
        ==
        MergeAnalysisResponse(is_fast_forward=True,
                              source_node_id=topic_first_sha,
                              source_branch=b'default',
                              source_topic=b'zetop',
                              target_node_id=default_sha,
                              target_branch=b'default',
                              target_topic=b'',
                              target_is_public=False,
                              )
    )
    newtop_sha = commit_file('foo',
                             parent=topic_ctx,
                             topic='newtop').hex().decode()
    repo_wrapper.update(topic_ctx)
    repo_wrapper.amend_file('foo').hex()

    assert (
        merge_analysis(source_revision=b'topic/default/newtop',
                       target_revision=b'branch/default')
        ==
        MergeAnalysisResponse(is_fast_forward=True,
                              has_obsolete_changesets=True,
                              has_unstable_changesets=True,
                              source_node_id=newtop_sha,
                              source_branch=b'default',
                              source_topic=b'newtop',
                              target_node_id=default_sha,
                              target_branch=b'default',
                              target_topic=b'',
                              target_is_public=False,
                              )
    )
    assert (
        merge_analysis(source_revision=topic_first_hex,
                       target_revision=b'branch/default')
        ==
        MergeAnalysisResponse(is_fast_forward=True,
                              has_obsolete_changesets=True,
                              has_unstable_changesets=False,
                              source_node_id=topic_first_sha,
                              source_branch=b'default',
                              source_topic=b'zetop',
                              target_node_id=default_sha,
                              target_branch=b'default',
                              target_topic=b'',
                              target_is_public=False,
                              )
    )

    # error cases
    with pytest.raises(RpcError) as exc_info:
        merge_analysis(source_revision=b'unknown',
                       target_revision=b'branch/default')
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'source revision' in exc_info.value.details().lower()

    with pytest.raises(RpcError) as exc_info:
        merge_analysis(source_revision=b'topic/default/zetop',
                       target_revision=b'unknownn')
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'target revision' in exc_info.value.details().lower()


def test_merge_analysis_conflict(operations_fixture):
    repo_wrapper = operations_fixture.repo_wrapper
    commit_file = repo_wrapper.commit_file
    ctx0 = commit_file('foo')
    default_sha = commit_file('foo', content="default").hex().decode()
    repo_wrapper.set_phase('public', ['.'])  # also testing `target_is_public`
    topic_first_sha = commit_file('foo', parent=ctx0,
                                  topic='zetop', content="top"
                                  ).hex().decode()

    merge_analysis = operations_fixture.merge_analysis
    assert (
        merge_analysis(source_revision=b'topic/default/zetop',
                       target_revision=b'branch/default')
        ==
        MergeAnalysisResponse(is_fast_forward=False,
                              has_conflicts=True,
                              source_node_id=topic_first_sha,
                              source_branch=b'default',
                              source_topic=b'zetop',
                              target_node_id=default_sha,
                              target_branch=b'default',
                              target_topic=b'',
                              target_is_public=True,
                              )
    )

    # same without the conflicts check
    conflicts_check_skipped = merge_analysis(
        skip_conflicts_check=True,
        source_revision=b'topic/default/zetop',
        target_revision=b'branch/default',
    )
    assert conflicts_check_skipped.is_fast_forward is False
    assert conflicts_check_skipped.has_conflicts is False  # was really skipped

    # solving the conflict
    topic_fixed_sha = commit_file('foo', topic='zetop',
                                  content="default").hex().decode()
    assert (
        merge_analysis(source_revision=b'topic/default/zetop',
                       target_revision=b'branch/default')
        ==
        MergeAnalysisResponse(is_fast_forward=False,
                              has_conflicts=False,
                              source_node_id=topic_fixed_sha,
                              source_branch=b'default',
                              source_topic=b'zetop',
                              target_node_id=default_sha,
                              target_branch=b'default',
                              target_topic=b'',
                              target_is_public=True,
                              )
    )


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_publish_changeset(operations_fixture, project_mode):
    fixture = operations_fixture
    fixture.hg_native = project_mode != 'hg-git-project'

    wrapper = fixture.repo_wrapper

    ctx0 = wrapper.commit_file('foo')
    hex0 = ctx0.hex()
    default_head = wrapper.commit_file('foo')

    # watching GitLab branches move when a topical changeset gets
    # published is an important thing to test
    topical = wrapper.commit_file('foo', topic='zetop', message='topical')

    # because of the config set by fixture, operations through wrapper
    # are performed in all cases with Git mirroring.
    git_repo = fixture.git_repo()
    initial_git_branches = git_repo.branches()

    default_ref = b'refs/heads/branch/default'
    top_ref = b'refs/heads/topic/default/zetop'

    # TODO make an obsolete and an unstable changeset, confirm it is
    # refused (or not, after all this is stricly for commit_files)

    # starting points
    assert ctx0.phase() == phases.draft
    assert fixture.list_refs() == {default_ref: default_head.hex().decode(),
                                   top_ref: topical.hex().decode()}

    fixture.publish(gitlab_revision=hex0, hg_perms=PUBLISH_PERM)
    wrapper.reload()
    assert wrapper.repo[hex0].phase() == phases.public

    # working with a symbolic revision
    fixture.publish(gitlab_revision=b'branch/default', hg_perms=PUBLISH_PERM)
    wrapper.reload()
    assert wrapper.repo[default_head.hex()].phase() == phases.public

    # publishing a topic
    fixture.publish(gitlab_revision=topical.hex(), hg_perms=PUBLISH_PERM)
    wrapper.reload()
    assert wrapper.repo[topical.hex()].phase() == phases.public

    assert fixture.list_refs() == {default_ref: topical.hex().decode()}

    if fixture.hg_native:
        # expect Git branches not to have moved
        assert git_repo.branches() == initial_git_branches
    else:
        # expect Git branch to point on new commit (and Git repo has moved
        # to the protected location so we need to reinstantiate it)
        git_repo = fixture.git_repo()
        assert git_repo.branches()[b'branch/default']['title'] == b'topical'

    # error cases
    with pytest.raises(RpcError) as exc_info:
        fixture.publish(gitlab_revision=b'not-resolvable',
                        hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'resolve revision' in exc_info.value.details().lower()

    with pytest.raises(RpcError) as exc_info:
        fixture.publish(hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'empty' in exc_info.value.details().lower()

    with pytest.raises(RpcError) as exc_info:
        fixture.publish(gitlab_revision=hex0, hg_perms=WRITE_PERM)


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_merge_branch(operations_fixture, project_mode):
    fixture = operations_fixture
    merge = fixture.merge_branch

    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    gl_branch = b'branch/default'

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    ctx0 = wrapper.commit_file('foo')
    initial_head = wrapper.commit_file('foo')
    ctx2 = wrapper.commit_file('foo', topic='zetop', message='fast-forward')
    sha2 = ctx2.hex().decode('ascii')
    conflict = wrapper.commit_file('foo', parent=ctx0, content='conflict',
                                   topic='conflicting')
    wrapper.commit_file('bar', branch='other', parent=ctx0)
    non_linear = wrapper.commit_file('old', parent=ctx0,
                                     topic='non-linear'
                                     ).hex().decode('ascii')

    # simple error cases
    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch, commit_id=sha2, message=b"whatever")
    assert exc_info.value.code() == StatusCode.PERMISSION_DENIED

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch, commit_id=sha2, message=b"whatever",
              hg_perms=WRITE_PERM)
    assert exc_info.value.code() == StatusCode.PERMISSION_DENIED

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch, commit_id=sha2, hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert exc_info.value.details() == 'empty message'

    with pytest.raises(RpcError) as exc_info:
        merge(message=b'whatever', commit_id=sha2, hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'branch name' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=b'topic/default/sometopic',
              message=b'whatever', commit_id=sha2, hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'named branches only' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id='12ca34fe' * 5,
              message=b'whatever',
              hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INTERNAL
    assert 'invalid commit' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id=sha2,
              expected_old_oid='12ca34fe' * 5,
              message=b'whatever',
              hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'cannot resolve' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id='not-a-hash',
              message=b'whatever',
              hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id=sha2,
              expected_old_oid='not-a-hash',
              message=b'whatever',
              hg_perms=PUBLISH_PERM)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id=non_linear,
              expected_old_oid=sha2,
              message=b'whatever',
              hg_perms=PUBLISH_PERM)
    _details, structured_err = parse_assert_structured_error(
        exc_info.value, MergeBranchError, StatusCode.FAILED_PRECONDITION)
    assert structured_err.reference_check == ReferenceUpdateError(
        reference_name=b'refs/heads/' + gl_branch,
        old_oid=sha2,
        new_oid=initial_head.hex().decode()
    )

    # semi-linear request but not fast-forwardable
    with pytest.raises(RpcError) as exc_info:
        merge(branch=gl_branch,
              commit_id=non_linear,
              message=b"whatever",
              hg_perms=PUBLISH_PERM,
              semi_linear=True)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION

    # successful fast-forward
    resp = merge(branch=gl_branch, commit_id=sha2,
                 hg_perms=PUBLISH_PERM,
                 message=b"whatever")
    wrapper.reload()

    assert resp.branch_update.commit_id == sha2
    assert wrapper.repo[ctx2.rev()].phase() == phases.public
    assert gitlab_branches(wrapper.repo)[gl_branch] == sha2.encode()

    if project_mode != 'native-project':
        git_repo = fixture.git_repo()
        assert git_repo.branch_titles()[gl_branch] == b'fast-forward'

    # successful actual merge
    resp = merge(branch=gl_branch,
                 commit_id=non_linear,
                 hg_perms=PUBLISH_PERM,
                 message=b"Actual merge!")
    wrapper.reload()

    merge_sha = resp.branch_update.commit_id
    assert merge_sha
    merge_changeset = wrapper.repo[merge_sha.encode()]
    assert merge_changeset.phase() == phases.public
    assert gitlab_branches(wrapper.repo)[gl_branch] == merge_changeset.hex()
    assert merge_changeset.p1().hex() == sha2.encode()
    assert merge_changeset.p2().hex() == non_linear.encode()
    assert merge_changeset.description() == b"Actual merge!"

    if project_mode != 'native-project':
        git_repo = fixture.git_repo()
        assert git_repo.branch_titles()[gl_branch] == b'Actual merge!'

    # conflict
    current_default_sha = merge_changeset.hex().decode()
    conflicting_sha = conflict.hex().decode()
    with pytest.raises(RpcError) as exc_info:
        resp = merge(branch=gl_branch,
                     commit_id=conflicting_sha,
                     hg_perms=PUBLISH_PERM,
                     message=b"whatever")
    details, merge_error = parse_assert_structured_error(
        exc_info.value, MergeBranchError, StatusCode.FAILED_PRECONDITION)
    conflict_error = merge_error.conflict
    assert conflict_error.conflicting_commit_ids == [current_default_sha,
                                                     conflicting_sha]
    assert conflict_error.conflicting_files == [b'foo']


@parametrize('project_mode', ('hg-git-project', 'native-project'))
@parametrize('semi_lin_req', ('semi_linear_req', 'classical_req'))
def test_merge_linear_named_branch(operations_fixture,
                                   project_mode,
                                   semi_lin_req):
    fixture = operations_fixture
    merge = fixture.merge_branch

    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    gl_branch = b'branch/default'

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    ctx0 = wrapper.commit_file('foo')

    linear_branch = b'linear'
    linear_branch_ctx = wrapper.commit_file('foolin',
                                            branch=linear_branch,
                                            parent=ctx0)
    # just checking what we just did
    assert ancestor(linear_branch_ctx, ctx0) == ctx0.rev()

    merge_msg = b"Actual merge for a named branch that makes linear history"
    resp = merge(branch=gl_branch,
                 commit_id=linear_branch_ctx.hex().decode('ascii'),
                 semi_linear=semi_lin_req == 'semi_linear_req',
                 hg_perms=PUBLISH_PERM,
                 message=merge_msg)
    wrapper.reload()

    merge_sha = resp.branch_update.commit_id
    assert merge_sha
    merge_changeset = wrapper.repo[merge_sha.encode()]
    assert merge_changeset.branch() == b'default'
    assert merge_changeset.phase() == phases.public
    assert gitlab_branches(wrapper.repo)[gl_branch] == merge_changeset.hex()
    assert merge_changeset.p1().hex() == ctx0.hex()
    assert merge_changeset.p2().hex() == linear_branch_ctx.hex()
    assert merge_changeset.description() == merge_msg


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_merge_branch_timestamp(operations_fixture, project_mode):
    fixture = operations_fixture
    merge = fixture.merge_branch

    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    gl_branch = b'branch/default'

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    ctx0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('foo')
    to_merge = wrapper.commit_file(
        'bar', branch='other', topic='zetop', parent=ctx0)

    solar_eclipse = 1624279076
    fixture.merge_branch(branch=gl_branch,
                         commit_id=to_merge.hex().decode(),
                         hg_perms=PUBLISH_PERM,
                         timestamp=Timestamp(seconds=solar_eclipse),
                         message=b'we have a date',
                         )
    wrapper.reload()
    merged = wrapper.repo[to_merge.rev()]
    assert merged.phase() == phases.public
    from mercurial import scmutil

    merge = scmutil.revsingle(wrapper.repo, b'default')
    assert merge.description() == b'we have a date'
    assert merge.date() == (solar_eclipse, 0)
    assert merge.p1().hex() == ctx1.hex()
    assert merge.p2() == merged

    if project_mode != 'native-project':
        git_repo = fixture.git_repo()
        git_branch = git_repo.branches()[gl_branch]
        assert git_branch['title'] == b'we have a date'
        assert git_repo.git(
            'log', '-n1', '--format=%as %cs', git_branch['sha']
        ).strip() == b'2021-06-21 2021-06-21'


def test_merge_branch_troubled_changesets(operations_fixture):
    fixture = operations_fixture
    wrapper = fixture.repo_wrapper

    gl_branch = b'branch/default'

    # stacked topics, and amending the first. The point of stacking
    # is that the amended changeset stays visible
    wrapper.commit_file('foo').hex().decode()
    amended = wrapper.commit_file('foo', topic='top1')
    wrapper.commit_file('foo', topic='top2')
    wrapper.update(amended)

    divergent = wrapper.amend_file('foo')  # not yet divergent

    def merge(source_changeset, **in_kw):
        out_kw = dict(branch=gl_branch,
                      hg_perms=PUBLISH_PERM,
                      commit_id=source_changeset.hex().decode(),
                      message=b'whatever')
        out_kw.update(in_kw)
        return fixture.merge_branch(**out_kw)

    with pytest.raises(RpcError) as exc_info:
        merge(amended)
    details, merge_error = parse_assert_structured_error(
        exc_info.value, MergeBranchError, StatusCode.FAILED_PRECONDITION)
    assert merge_error.pre_check == PreCheckUpdateError.OBSOLETE_CHANGESET

    # making a phase divergence
    wrapper.set_phase('public', [amended.hex()])

    with pytest.raises(RpcError) as exc_info:
        merge(divergent)
    details, merge_error = parse_assert_structured_error(
        exc_info.value, MergeBranchError, StatusCode.FAILED_PRECONDITION)
    assert merge_error.pre_check == PreCheckUpdateError.UNSTABLE_CHANGESET


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_censor(operations_fixture, project_mode):
    fixture = operations_fixture
    # The `censor` extension is part of py-heptapod's `required.hgrc`, hence
    # always there in Heptapod context
    fixture.repo_wrapper.write_hgrc(dict(extensions=dict(censor='')))
    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    ctx0 = wrapper.commit_file('foo', content='oops, secret')
    hex0 = ctx0.hex()
    wrapper.commit_removal('foo')
    # censor cannot work if the file is in the working directory
    # TODO do in-method, we really want to be able to censor

    fixture.censor(changeset_node_id=hex0.decode(), file_path=b'foo')

    with pytest.raises(hg_error.Abort) as exc_info:
        wrapper.command('cat', b'/'.join((wrapper.repo.root, b'foo')),
                        rev=hex0)
    assert 'censored node' in str(exc_info.value)

    # error cases

    with pytest.raises(RpcError) as exc_info:
        fixture.censor(changeset_node_id='dead6789' * 5, file_path=b'foo')
    exc = exc_info.value
    assert exc.code() == StatusCode.INVALID_ARGUMENT
    assert 'changeset' in exc.details().lower()
    assert 'not found' in exc.details().lower()


@parametrize('storage', ('vcs-qualified-storage', 'bare-storage'))
def test_working_directories(operations_fixture, server_repos_root, storage):
    fixture = operations_fixture
    if storage == 'vcs-qualified-storage':
        fixture.grpc_repo.storage_name = 'hg:default'

    gl_rev = b'branch/default'
    wrapper = fixture.repo_wrapper
    cs0 = wrapper.commit_file('foo')

    resp = fixture.get_workdir(revision=gl_rev)
    wd_id = resp.working_directory_id
    wd_path = server_repos_root / 'default' / resp.relative_path

    # let us check that the working directory works by committing a file
    # in there and retrieve it from the main repo
    wd_wrapper = RepoWrapper.load(wd_path)
    wd_wrapper.repo.ui.environ[PY_HEPTAPOD_SKIP_HOOKS] = b'yes'
    cs_done_in_wd = wd_wrapper.commit_file('bar', "done in wd")
    wrapper.reload()
    cs_in_main = wrapper.repo[cs_done_in_wd.hex()]
    assert cs_in_main.description() == b'done in wd'
    assert cs_in_main.p1() == cs0

    # releasing without being the correct client
    with pytest.raises(RpcError) as exc_info:
        fixture.release_workdir(working_directory_id=wd_id,
                                client_id='some other client')
    exc = exc_info.value
    assert exc.code() == StatusCode.PERMISSION_DENIED

    wd_id2 = fixture.get_workdir(revision=gl_rev).working_directory_id
    assert wd_id2 != wd_id

    # releasing for good
    fixture.release_workdir(working_directory_id=wd_id)

    # reuse of first workdir (also tests that no revison ends up selecting
    # the same Mercurial branch as `branch/default`, hence `default`
    assert fixture.get_workdir().working_directory_id == wd_id

    # unknown revision
    with pytest.raises(RpcError) as exc_info:
        fixture.get_workdir(revision=b'ca34fe12')
    exc = exc_info.value
    assert exc.code() == StatusCode.NOT_FOUND
