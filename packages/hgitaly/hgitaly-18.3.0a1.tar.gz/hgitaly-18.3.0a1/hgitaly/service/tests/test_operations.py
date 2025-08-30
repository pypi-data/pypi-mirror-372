# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from base64 import b64encode
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import (
    RpcError,
    StatusCode,
)
from io import BytesIO
import pytest
import stat

from mercurial import (
    phases,
)
from mercurial_testhelpers.util import as_bytes


from hgext3rd.heptapod.branch import (
    gitlab_branches,
)

from hgitaly.stub.operations_pb2 import (
    OperationBranchUpdate,
    UserCommitFilesAction,
    UserCommitFilesActionHeader,
    UserCommitFilesRequest,
    UserCommitFilesRequestHeader,
    UserFFBranchRequest,
    UserSquashRequest,
)
from hgitaly.stub.operations_pb2_grpc import (
    OperationServiceStub,
)
from hgitaly.stub.shared_pb2 import (
    User,
)
from hgitaly.tests.common import (
    make_empty_repo,
    make_empty_repo_with_gitlab_state_maintainer,
)


from .fixture import MutationServiceFixture

parametrize = pytest.mark.parametrize


class OperationsFixture(MutationServiceFixture):

    stub_cls = OperationServiceStub

    def user_squash(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.UserSquash(UserSquashRequest(**kw),
                                    metadata=self.grpc_metadata())

    def user_ff_branch(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.UserFFBranch(UserFFBranchRequest(**kw),
                                      metadata=self.grpc_metadata())

    def user_commit_files(self, actions, **kw):
        requests = [self.user_commit_files_header(**kw)]
        for action in actions:
            requests.extend(self.ucf_actions(action))
        return self.raw_user_commit_files(requests)

    def user_commit_files_header(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        kw.setdefault('commit_author_name', self.user.name)
        kw.setdefault('commit_author_email', self.user.email)
        return UserCommitFilesRequest(
            header=UserCommitFilesRequestHeader(**kw)
        )

    def raw_user_commit_files(self, requests):
        return self.stub.UserCommitFiles(iter(requests),
                                         metadata=self.grpc_metadata())

    def ucf_actions(self, action):
        content = action.pop('content', None)
        requests = [UserCommitFilesRequest(
            action=UserCommitFilesAction(
                header=UserCommitFilesActionHeader(**action))
        )]
        if content is not None:
            # we make one message per line for testing purposes,
            # but we avoid splitlines() as it removes line separators.
            # we could re-add them but that would make life difficult
            # for (future) tests about EOL normalization.
            lines = BytesIO(content).readlines()

            requests.extend(
                UserCommitFilesRequest(
                    action=UserCommitFilesAction(content=line)
                ) for line in lines
            )
        return requests


@pytest.fixture
def operations_fixture(grpc_channel, server_repos_root):
    with OperationsFixture(
            grpc_channel, server_repos_root,
            repo_factory=make_empty_repo_with_gitlab_state_maintainer
    ) as fixture:
        yield fixture


@parametrize('timestamp', ('timestamp', 'now'))
@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_user_squash(operations_fixture, project_mode, timestamp):
    fixture = operations_fixture
    wrapper = fixture.repo_wrapper
    hg_repo = wrapper.repo

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    sha1 = wrapper.commit_file('foo').hex().decode('ascii')
    sha2 = wrapper.commit_file('foo', message='foo2').hex().decode('ascii')
    sha3 = wrapper.commit_file('foo', message='foo3').hex().decode('ascii')
    wrapper.update(sha1)  # avoid keeping changeset 3 visible
    # let's confirm it
    git_repo = fixture.git_repo()
    before_squash_git_branches = git_repo.branches()
    assert before_squash_git_branches[b'branch/default']['title'] == b'foo3'

    squash = fixture.user_squash

    fixture.hg_native = project_mode != 'hg-git-project'

    if timestamp == 'now':
        ts = None
    else:
        ts = Timestamp()
        ts.FromSeconds(1702472217)
    author = User(name=b"John Doe",
                  gl_id='user-987',
                  email=b"jd@heptapod.test",
                  )
    resp = squash(start_sha=sha1,
                  end_sha=sha3,
                  author=author,
                  timestamp=ts,
                  commit_message=b'squashed!')

    # we will need more that list_refs, namely that the state file does exist,
    # without any fallback.
    # TODO check obslog on the result
    wrapper.reload()
    hg_repo = wrapper.repo
    gl_branches = gitlab_branches(hg_repo)
    folded_sha = gl_branches[b'branch/default']
    assert folded_sha == resp.squash_sha.encode('ascii')
    assert folded_sha != sha2.encode('ascii')
    folded_ctx = hg_repo[folded_sha]
    assert folded_ctx.description() == b'squashed!'
    unfi = hg_repo.unfiltered()
    for sha in (sha2, sha3):
        assert unfi[sha].obsolete()
    assert fixture.list_refs() == {
        b'refs/heads/branch/default': folded_sha.decode('ascii')
    }

    if fixture.hg_native:
        # expect Git branches not to have moved
        assert git_repo.branches() == before_squash_git_branches
    else:
        # expect Git branch to point on new commit (also Git repo may have
        # moved, let's also reload it)
        git_repo = fixture.git_repo()
        assert git_repo.branches()[b'branch/default']['title'] == b'squashed!'

    for kw in (
            dict(user=None, start_sha=sha1, end_sha=sha2),
            dict(commit_message=None, start_sha=sha1, end_sha=sha2),
            # missing author
            dict(commit_message=b'squashed', start_sha=sha1, end_sha=sha2),
            # missing start_sha or end_sha
            dict(commit_message=b'squashed', author=author, end_sha=sha2),
            dict(commit_message=b'squashed', author=author, start_sha=sha1),
            dict(commit_message=b'squashed', author=author,
                 start_sha='unknown', end_sha=sha2),
            dict(commit_message=b'squashed', author=author, end_sha=sha2),
            dict(commit_message=b'squashed', author=author,
                 start_sha=sha1, end_sha='unknown'),
    ):
        with pytest.raises(RpcError) as exc_info:
            squash(**kw)
        assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

    amend_msg = b'squash becomes an amend!'
    resp = squash(start_sha=sha1,
                  end_sha=folded_sha,
                  author=author,
                  commit_message=amend_msg)
    amended_sha = resp.squash_sha.encode('ascii')
    wrapper.reload()
    amended_ctx = wrapper.repo[amended_sha]
    assert amended_ctx.description() == amend_msg


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_user_ff_branch(operations_fixture, project_mode):
    fixture = operations_fixture
    ff_branch = fixture.user_ff_branch

    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    gl_topic = b'topic/default/zetop'
    gl_branch = b'branch/default'
    gl_other_branch = b'branch/other'

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    ctx0 = wrapper.commit_file('foo')
    sha0 = ctx0.hex().decode()
    default_head = wrapper.commit_file('foo')
    ctx2 = wrapper.commit_file('foo', topic='zetop', message='foo2')
    sha2 = ctx2.hex().decode('ascii')
    wrapper.commit_file('bar', branch='other', parent=ctx0)
    needs_rebase = wrapper.commit_file('old', parent=ctx0,
                                       topic='needs-rebase'
                                       ).hex().decode('ascii')
    bogus1 = wrapper.commit_file('bogus', topic='bogus',
                                 parent=default_head)
    bogus1_sha = bogus1.hex().decode()
    # changing topic so that amending bogus1 is not a multiple heads condition
    bogus2 = wrapper.commit_file('bogus', topic='bogus2')
    bogus2_sha = bogus2.hex().decode()

    # let's confirm the mirroring to Git
    git_repo = fixture.git_repo()
    before_ff_git_branches = git_repo.branches()
    assert before_ff_git_branches[gl_topic]['title'] == b'foo2'

    # making bogus_top1 obsolete
    wrapper.update_bin(bogus1.node())
    wrapper.amend_file('foo')

    before_refs = fixture.list_refs()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_other_branch, commit_id=sha2)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'branch differ' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=bogus2_sha)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'unstable' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=bogus1_sha)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'obsolete' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_topic, commit_id=sha2)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'named branches only' in exc_info.value.details()

    # case where nothing is pathological, but is not a fast-forward
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=needs_rebase)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'not fast forward' in exc_info.value.details()

    # basic errors, missing and unresolvable arguments
    with pytest.raises(RpcError) as exc_info:
        ff_branch(commit_id=sha2)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'empty branch' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id='not-a-hash')
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit ID' in exc_info.value.details()

    unknown_oid = '01beef23' * 5
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=unknown_oid)
    assert exc_info.value.code() == StatusCode.INTERNAL
    assert 'invalid commit' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2,
                  expected_old_oid=unknown_oid)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'old object' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2,
                  expected_old_oid='12deadbeef')  # short hash
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit ID' in exc_info.value.details()

    # old oid mismatch
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2, expected_old_oid=sha0)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert exc_info.value.details() == "expected_old_oid mismatch"

    assert fixture.list_refs() == before_refs

    # Actual call expected to succeed
    resp = ff_branch(branch=gl_branch, commit_id=sha2)

    # checking change on default branch ref, and only this ref.
    expected_refs = before_refs.copy()
    expected_refs[b'refs/heads/' + gl_branch] = sha2
    del expected_refs[b'refs/heads/' + gl_topic]

    assert fixture.list_refs() == expected_refs
    assert resp.branch_update == OperationBranchUpdate(commit_id=sha2,
                                                       repo_created=False,
                                                       branch_created=False)
    wrapper.reload()
    assert wrapper.repo[ctx2.rev()].phase() == phases.public


def test_user_commit_files(operations_fixture, tmpdir):
    fixture = operations_fixture
    commit_files = fixture.user_commit_files

    fixture.hg_native = True  # TODO just remove hg-git now
    fixture.heptapod_permission = 'publish'
    wrapper = fixture.repo_wrapper
    with open(wrapper.path / '.hg/hgrc', 'a') as hgrcf:
        # this is part of the normally included `required.hgrc` of
        # py-heptapod
        hgrcf.write('\n'.join((
            "[experimental]",
            "topic.publish-bare-branch = yes"
            ""
        )))

    gl_topic = b'topic/default/zetop'
    gl_branch = b'branch/default'
    gl_other_branch = b'branch/other'

    ActionType = UserCommitFilesActionHeader.ActionType

    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Committed by HGitaly!',
        actions=(dict(action=ActionType.CREATE,
                      file_path=b'foo',
                      content=b'foo content',
                      ),
                 )
    )
    hex0 = resp.branch_update.commit_id.encode()
    ctx0 = wrapper.repo[hex0]
    assert ctx0.description() == b'Committed by HGitaly!'
    assert ctx0.user() == b'Test User <testuser@heptapod.test>'

    clone, _clone_grpc_repo = make_empty_repo(tmpdir)

    def clone_pull_update(rev, hidden=False):
        clone.command('pull', as_bytes(wrapper.path), remote_hidden=False)
        clone.update(rev)

    clone_pull_update(hex0)
    foo_cloned = clone.path / 'foo'
    assert foo_cloned.read_binary() == b'foo content'

    # now let's start a topic and test file content
    two_lines = b"zz\nsecond proto message"
    resp = commit_files(
        branch_name=gl_topic,
        start_branch_name=gl_branch,
        commit_message=b'New topic',
        actions=(dict(action=ActionType.CREATE,
                      file_path=b'intop',
                      content=two_lines,
                      ),
                 )
    )
    hex1 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx1 = wrapper.repo[hex1]
    assert ctx1.description() == b'New topic'
    assert ctx1.branch() == b'default'
    assert ctx1.topic() == b'zetop'

    clone_pull_update(hex1)
    assert (clone.path / 'intop').read_binary() == two_lines

    # insufficient perms
    fixture.heptapod_permission = 'write'  # not enough for auto-publication
    before_count = len(wrapper.repo)
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            commit_message=b'publication',
            actions=(dict(action=ActionType.CREATE,
                          file_path=b'foo',
                          content=b'foo published!',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.PERMISSION_DENIED
    wrapper.reload()
    assert len(wrapper.repo) == before_count  # everything got rollbacked
    fixture.heptapod_permission = 'publish'

    # now let's start a new named branch
    resp = commit_files(
        branch_name=gl_other_branch,
        start_branch_name=gl_branch,
        commit_message=b'New branch',
        actions=(dict(action=ActionType.UPDATE,
                      file_path=b'foo',
                      content=b"other foo",
                      ),
                 dict(action=ActionType.CREATE,
                      file_path=b'inother',
                      content=b"new file in other branch",
                      execute_filemode=True
                      ),
                 )
    )
    assert resp.branch_update.branch_created
    hex2 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx2 = wrapper.repo[hex2]
    assert ctx2.description() == b'New branch'
    assert ctx2.branch() == b'other'
    assert not ctx2.topic()
    assert ctx2.phase() == phases.public

    clone_pull_update(hex2)
    assert foo_cloned.read_binary() == b"other foo"
    in_other = (clone.path / 'inother')
    assert in_other.read_binary() == b"new file in other branch"
    assert in_other.stat().mode & stat.S_IXUSR

    # CHMOD
    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Made foo executable',
        actions=(dict(action=ActionType.CHMOD,
                      file_path=b'foo',
                      execute_filemode=True
                      ),
                 )
    )
    hex3 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx3 = wrapper.repo[hex3]
    assert ctx3.branch() == b'default'
    assert not ctx3.topic()
    clone_pull_update(hex3)
    assert foo_cloned.read_binary() == b"foo content"  # unchanged
    assert foo_cloned.stat().mode & stat.S_IXUSR

    # DELETE
    resp = commit_files(
        branch_name=gl_topic,
        commit_message=b'Deleted intopic',
        actions=(dict(action=ActionType.DELETE,
                      file_path=b'intop',
                      ),
                 )
    )
    hex4 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx4 = wrapper.repo[hex4]
    assert ctx4.branch() == b'default'
    assert ctx4.topic() == b'zetop'
    clone_pull_update(hex4)
    assert not (clone.path / 'intopic').exists()

    # MOVE
    resp = commit_files(
        branch_name=gl_other_branch,
        commit_message=b'Remamed inother',
        actions=(dict(action=ActionType.MOVE,
                      previous_path=b'inother',
                      file_path=b'asother',
                      ),
                 )
    )
    hex5 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx5 = wrapper.repo[hex5]
    assert ctx5.branch() == b'other'
    clone_pull_update(hex5)
    assert not (clone.path / 'inother').exists()
    assert (clone.path / 'asother'
            ).read_binary() == b"new file in other branch"

    # base64 content
    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Deleted intopic',
        actions=(dict(action=ActionType.CREATE,
                      file_path=b'src/main.rs',
                      content=b64encode(b'// Some clever Rust code'),
                      base64_content=True,
                      ),
                 )
    )
    hex6 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    clone_pull_update(hex6)
    assert not (clone.path / 'inother').exists()
    assert (clone.path / 'src/main.rs').read_binary().startswith(b'//')

    # CREATE_DIR
    resp = commit_files(
        branch_name=gl_branch,
        actions=(dict(action=ActionType.CREATE_DIR,
                      file_path=b'out',
                      ),
                 ))
    hex7 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    clone_pull_update(hex7)
    assert (clone.path / 'out').isdir()

    # start_sha has precedence
    resp = commit_files(
        branch_name=gl_other_branch,
        start_sha=hex5,
        start_branch_name=gl_branch,
        commit_message=b'follow-up on other_branch',
        actions=(dict(action=ActionType.UPDATE,
                      file_path=b'asother',
                      content=b"other foo2",
                      ),
                 )
    )
    hex8 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    clone_pull_update(hex8)
    assert (clone.path / 'asother').read_binary() == b"other foo2"
    ctx8 = clone.repo[hex8]
    assert ctx8.p1().hex() == hex5
    assert ctx8.branch() == b'other'
    assert ctx8.phase() == phases.public

    # CHMOD back
    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Made foo non-executable',
        actions=(dict(action=ActionType.CHMOD,
                      file_path=b'foo',
                      execute_filemode=False
                      ),
                 )
    )
    hex9 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx9 = wrapper.repo[hex9]
    assert ctx9.branch() == b'default'
    assert not ctx9.topic()
    clone_pull_update(hex9)
    assert foo_cloned.read_binary() == b"foo content"  # unchanged
    assert not foo_cloned.stat().mode & stat.S_IXUSR

    # No resulting op is not an error
    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Made foo non-executable',
        actions=(dict(action=ActionType.CHMOD,
                      file_path=b'foo',
                      execute_filemode=False
                      ),
                 )
    )
    assert not resp.HasField('branch_update')

    # Special case for NULL
    # (this normally done at repo creation, for the README)
    resp = commit_files(
        branch_name=b'branch/newroot',
        commit_message=b'starting from NULL',
        expected_old_oid='0000' * 10,
        actions=(dict(action=ActionType.CREATE,
                      file_path=b'from_null',
                      content=b"it is admissible",
                      ),
                 )
    )
    hex10 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    ctx10 = wrapper.repo[hex10]
    # without special provisions for old_oid, the changeset would be
    # stacked on the previous head of default
    assert ctx10.p1().rev() == -1
    assert ctx10.branch() == b'newroot'

    #
    # Error cases
    #

    # prevent wild heads

    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            start_sha=hex0,
            commit_message=b'wild heads',
            actions=(dict(action=ActionType.UPDATE,
                          file_path=b'foo',
                          content=b"Wild foo!",
                          ),
                     )
        )
    exc = exc_info.value
    assert exc.code() == StatusCode.INVALID_ARGUMENT
    assert 'multiple heads' in exc.details()

    # missing branch specification and unknown start branch
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=b'',
            commit_message=b'Commit without branch!',
            actions=(dict(action=ActionType.CREATE,
                          file_path=b'zoo',
                          content=b'zoo',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            start_branch_name=b'branch/unknown',
            commit_message=b'Commit without branch!',
            actions=(dict(action=ActionType.CREATE,
                          file_path=b'zoo',
                          content=b'zoo',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.INTERNAL

    # wrong start oid
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            commit_message=b'OID mismatch',
            expected_old_oid=b'85fa6e7c' * 5,
            actions=(dict(action=ActionType.CREATE,
                          file_path=b'zoo',
                          content=b'zoo',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

    # branch resolving to a bookmark
    for start_branch in (b'oldbook', gl_branch, gl_topic, b''):
        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=b'book',
                start_branch_name=start_branch,
                commit_message=b'bookmark',
                expected_old_oid=b'85fa6e7c' * 5,
                actions=(dict(action=ActionType.CREATE,
                              file_path=b'zoo',
                              content=b'zoo',
                              ),
                         )
            )
    # TODO start branch being a bookmark should be acceptable
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

    # file already exists
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            commit_message=b'foo',
            actions=(dict(action=ActionType.CREATE,
                          file_path=b'out',
                          content=b'foo redux',
                          ),
                     )
        )
    assert exc_info.value.code() == StatusCode.ALREADY_EXISTS

    # directory already exists (file or directory)
    for existing in (b'foo', b'out'):
        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=gl_branch,
                commit_message=b'redux',
                actions=(dict(action=ActionType.CREATE_DIR,
                              file_path=existing,
                              ),
                         )
            )
    assert exc_info.value.code() == StatusCode.ALREADY_EXISTS

    # update on a file that does not exist
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            commit_message=b'update attempt',
            actions=(dict(action=ActionType.UPDATE,
                          file_path=b'not-yet',
                          content=b'someting',
                          ),
                     )
        )
    assert exc_info.value.code() == StatusCode.NOT_FOUND

    # delete and chmod on a file that does not exist
    for action in (ActionType.CHMOD, ActionType.DELETE):
        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=gl_branch,
                commit_message=b'cnmod attempt',
                actions=(dict(action=action,
                              file_path=b'not-yet',
                              ),
                         )
                )
        assert exc_info.value.code() == StatusCode.NOT_FOUND

    # move source file does not exist
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_branch,
            commit_message=b'move attempt',
            actions=(dict(action=ActionType.MOVE,
                          file_path=b'moved',
                          previous_path=b'not-yet',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.NOT_FOUND

    # move target already exists
    with pytest.raises(RpcError) as exc_info:
        commit_files(
            branch_name=gl_other_branch,
            commit_message=b'move attempt',
            actions=(dict(action=ActionType.MOVE,
                          file_path=b'foo',
                          previous_path=b'asother',
                          ),
                     )
            )
    assert exc_info.value.code() == StatusCode.ALREADY_EXISTS

    # invalid paths
    for path in ('double//slash', '../../../good.joke'):
        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=gl_branch,
                commit_message=b'invalid file path',
                actions=(dict(action=ActionType.CREATE,
                              file_path=path.encode(),
                              content=b'will be rejected',
                              ),
                         )
                )
        assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=gl_branch,
                commit_message=b'invalid dir path',
                actions=(dict(action=ActionType.CREATE_DIR,
                              file_path=path.encode(),
                              ),
                         )
            )
        assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

        with pytest.raises(RpcError) as exc_info:
            commit_files(
                branch_name=gl_branch,
                commit_message=b'invalid move source',
                actions=(dict(action=ActionType.MOVE,
                              previous_path=path.encode(),
                              file_path=b'ignored-target',
                              ),
                         )
            )
        assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

    # leading slash is interpreted as meaning the root of checkout
    resp = commit_files(
        branch_name=gl_branch,
        commit_message=b'Deleted intopic',
        actions=(dict(action=ActionType.CREATE,
                      file_path=b'/etc/shadow',
                      content=b"This is in repo!",
                      ),
                 )
    )
    hex11 = resp.branch_update.commit_id.encode()
    wrapper.reload()
    clone_pull_update(hex11)
    assert (clone.path / 'etc/shadow').read_binary() == b"This is in repo!"

    # bogus request flows
    header_req = fixture.user_commit_files_header(
        branch_name=gl_other_branch,
    )
    with pytest.raises(RpcError) as exc_info:
        fixture.raw_user_commit_files([  # double header
            header_req,
            header_req,
        ])
    assert exc_info.value.code() == StatusCode.INTERNAL

    with pytest.raises(RpcError) as exc_info:
        fixture.raw_user_commit_files([  # content before header action
            header_req,
            UserCommitFilesRequest(action=UserCommitFilesAction(
                content=b'too earlly!')),
        ])
    assert exc_info.value.code() == StatusCode.INTERNAL

    with pytest.raises(RpcError) as exc_info:
        fixture.raw_user_commit_files([  # action before header
            UserCommitFilesRequest(action=UserCommitFilesAction())
        ])
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
