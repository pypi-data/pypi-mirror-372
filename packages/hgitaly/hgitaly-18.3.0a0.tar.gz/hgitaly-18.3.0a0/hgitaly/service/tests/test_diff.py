# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
from mercurial.pycompat import sysstr
import pytest
from hgitaly.git import (
    EMPTY_TREE_OID,
    OBJECT_MODE_DOES_NOT_EXIST,
    OBJECT_MODE_EXECUTABLE,
    OBJECT_MODE_NON_EXECUTABLE,
)
from hgitaly.oid import (
    tree_oid,
)
from hgitaly.stub.diff_pb2 import (
    CommitDeltaRequest,
    CommitDiffRequest,
    ChangedPaths,
    DiffStatsRequest,
    GetPatchIDRequest,
    RawDiffRequest,
    RawPatchRequest,
    FindChangedPathsRequest,
)
from mercurial import (
    node,
)
from hgitaly.stub.diff_pb2_grpc import DiffServiceStub

from .fixture import ServiceFixture

StatusCode = grpc.StatusCode


class DiffFixture(ServiceFixture):

    stub_cls = DiffServiceStub

    def raw_method(self, stub_meth, req_cls, left_sha, right_sha):
        request = req_cls(
            repository=self.grpc_repo,
            left_commit_id=left_sha,
            right_commit_id=right_sha,
        )
        return b''.join(resp.data for resp in stub_meth(request))

    def raw_diff(self, left_sha, right_sha):
        return self.raw_method(self.stub.RawDiff,
                               RawDiffRequest,
                               left_sha, right_sha)

    def raw_patch(self, left_sha, right_sha):
        return self.raw_method(self.stub.RawPatch,
                               RawPatchRequest,
                               left_sha, right_sha)

    def commit_ids_method(self, stub_meth, req_cls,
                          left_cid, right_cid,
                          flatten_attr=None,
                          **kwargs):
        """Common caller for commit_* methods and similar.

        :param flatten_attr: if provided, the responses are flattened to
           a single list, from sublists provided in this attribute. Other
           wise simple conversion to list of the streaming request is
           performed.
        """
        response = stub_meth(req_cls(repository=self.grpc_repo,
                                     left_commit_id=left_cid,
                                     right_commit_id=right_cid,
                                     **kwargs))
        if flatten_attr is not None:
            return [item for r in response
                    for item in getattr(r, flatten_attr)]
        return list(response)

    def commit_diff(self, left_cid, right_cid, **kwargs):
        return self.commit_ids_method(self.stub.CommitDiff,
                                      CommitDiffRequest,
                                      left_cid, right_cid,
                                      **kwargs)

    def get_patch_id(self, old_revision, new_revision, **kwargs):
        kwargs.setdefault('repository', self.grpc_repo)
        return self.stub.GetPatchID(GetPatchIDRequest(
            old_revision=old_revision,
            new_revision=new_revision,
            **kwargs)).patch_id

    def commit_delta(self, left_cid, right_cid, **kwargs):
        return self.commit_ids_method(self.stub.CommitDelta,
                                      CommitDeltaRequest,
                                      left_cid, right_cid,
                                      flatten_attr='deltas',
                                      **kwargs)

    def diff_stats(self, left_cid, right_cid, **kwargs):
        return self.commit_ids_method(self.stub.DiffStats,
                                      DiffStatsRequest,
                                      left_cid, right_cid,
                                      flatten_attr='stats',
                                      **kwargs)

    def find_changed_paths(self, **kwargs):
        """Run FindChangedPaths and present the results by file path.

        :return: a :class:`dict` whose keys are file paths (bytes) and
          values are lists of (status change, permission change).

        Permission changes are pairs ``(old_perm, new_perm)`` if this is
        an actual change, and ``None`` otherwise.
        """
        by_file = {}
        for resp in self.stub.FindChangedPaths(FindChangedPathsRequest(
                repository=self.grpc_repo, **kwargs)):
            for changed in resp.paths:
                if changed.old_mode != changed.new_mode:
                    perm_change = (changed.old_mode, changed.new_mode)
                else:
                    perm_change = None

                by_file.setdefault(changed.path, []).append(
                    (changed.status, perm_change))
        return by_file

    def find_changed_paths_commits(self, commits, compare_to=(), **kw):
        """Wrap FindChangedPaths used with CommitRequest.

        :param compare_to: if given, will be used in all requests, hoping
          we won't need more flexibility
        """
        CommitRequest = FindChangedPathsRequest.Request.CommitRequest
        return self.find_changed_paths(
            requests=[
                FindChangedPathsRequest.Request(
                    commit_request=CommitRequest(
                        commit_revision=c,
                        parent_commit_revisions=compare_to))
                for c in commits],
            **kw
        )

    def find_changed_paths_tree(self, left_oid, right_oid):
        TreeRequest = FindChangedPathsRequest.Request.TreeRequest
        return self.find_changed_paths(
            requests=[
                FindChangedPathsRequest.Request(
                    tree_request=TreeRequest(left_tree_revision=left_oid,
                                             right_tree_revision=right_oid,
                                             ))
                ]
        )


@pytest.fixture
def diff_fixture(grpc_channel, server_repos_root):
    with DiffFixture(grpc_channel, server_repos_root) as fixture:
        yield fixture


def test_raw_diff(diff_fixture):
    raw_diff = diff_fixture.raw_diff
    wrapper = diff_fixture.repo_wrapper

    ctx0 = wrapper.commit_file('foo', content="I am oof\n",
                               message=b'added foo')
    ctx1 = wrapper.commit_file('foo', content="I am foo\n",
                               message=b'changes foo')
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    wrapper.command(b'ci', message=b"rename foo to zoo")
    ctx2 = wrapper.repo[b'.']
    sha0, sha1, sha2 = ctx0.hex(), ctx1.hex(), ctx2.hex()

    # case 1: actual test
    resp = raw_diff(sha0, sha1)
    respheader = (
        b'diff --git a/foo b/foo\n'
    )
    resphunk = (
        b'--- a/foo\n'
        b'+++ b/foo\n'
        b'@@ -1,1 +1,1 @@\n'
        b'-I am oof\n'
        b'+I am foo\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2: with null node
    resp = raw_diff(node.nullhex, sha0)
    respheader = (
        b'diff --git a/foo b/foo\n'
    )
    resphunk = (
        b'--- /dev/null\n'
        b'+++ b/foo\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am oof\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2bis: with null left node, expressed as empty tree
    # this is really used by the Rails app.
    resp = raw_diff(EMPTY_TREE_OID, sha0)
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 2ter: with null right node, expressed as empty tree
    # this is for completeness
    resp = raw_diff(sha0, EMPTY_TREE_OID)
    resphunk = (
        b'--- a/foo\n'
        b'+++ /dev/null\n'
        b'@@ -1,1 +0,0 @@\n'
        b'-I am oof\n'
    )
    assert resp.startswith(respheader) and resp.endswith(resphunk)

    # case 3: with file renaming
    resp = raw_diff(sha1, sha2)
    assert resp == (
        b'diff --git a/foo b/zoo\n'
        b'similarity index 100%\n'
        b'rename from foo\n'
        b'rename to zoo\n'
    )

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    # varient 1
    with pytest.raises(grpc.RpcError) as exc_info:
        raw_diff(sha0, sha_not_exists)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'exit status 128' in exc_info.value.details()
    # varient 2
    with pytest.raises(grpc.RpcError) as exc_info:
        raw_diff(sha_not_exists, sha0)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'exit status 128' in exc_info.value.details()


def test_raw_patch(diff_fixture):
    raw_patch = diff_fixture.raw_patch

    # prepare repo as:
    #
    #   @    3 merge with stable
    #   |\
    #   | o  2 added bar (branch: stable)
    #   | |
    #   o |  1 changes foo (topic: feature)
    #   |/
    #   o  0 added foo
    #
    #
    wrapper = diff_fixture.repo_wrapper
    dayoffset = 86400  # seconds in 24 hours
    ctx0 = wrapper.commit_file('foo', content="I am oof\n",
                               message=b'added foo', user=b'testuser',
                               utc_timestamp=dayoffset)
    ctx1 = wrapper.commit_file('foo', content="I am foo\n", topic=b'feature',
                               message=b'changes foo', user=b'testuser',
                               utc_timestamp=dayoffset*2)
    ctx2 = wrapper.commit_file('bar', content="I am bar\n",
                               message=b'added bar', user=b'testuser',
                               utc_timestamp=dayoffset*3, parent=ctx0,
                               branch=b'stable')
    wrapper.update(ctx1.rev())
    ctx3 = wrapper.merge_commit(ctx2, user=b'testuser',
                                utc_timestamp=dayoffset*4,
                                message=b'merge with stable')
    sha0, sha2, sha3 = ctx0.hex(), ctx2.hex(), ctx3.hex()

    # with null revision
    null_node = b"00000" * 5
    assert raw_patch(null_node, sha0) == (
        b'# HG changeset patch\n'

        b'# User testuser\n'
        b'# Date 86400 0\n'
        b'#      Fri Jan 02 00:00:00 1970 +0000\n'
        b'# Node ID f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'# Parent  0000000000000000000000000000000000000000\n'
        b'added foo\n'
        b'\n'
        b'diff --git a/foo b/foo\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/foo\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am oof\n'
    )
    # with merge commit
    assert raw_patch(sha2, sha3) == (
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 172800 0\n'
        b'#      Sat Jan 03 00:00:00 1970 +0000\n'
        b'# Node ID 0ae85a0d494d9197fd2bf8347d7fff997576f25a\n'
        b'# Parent  f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'# EXP-Topic feature\n'
        b'changes foo\n'
        b'\n'
        b'diff --git a/foo b/foo\n'
        b'--- a/foo\n'
        b'+++ b/foo\n'
        b'@@ -1,1 +1,1 @@\n'
        b'-I am oof\n'
        b'+I am foo\n'
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 345600 0\n'
        b'#      Mon Jan 05 00:00:00 1970 +0000\n'
        b'# Node ID 2215a964a3245ee4e7c3906f076b14977152a1df\n'
        b'# Parent  0ae85a0d494d9197fd2bf8347d7fff997576f25a\n'
        b'# Parent  c4fa3ef1fc8ba157ed8c26584c13492583bf17e9\n'
        b'# EXP-Topic feature\n'
        b'merge with stable\n'
        b'\n'
        b'diff --git a/bar b/bar\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/bar\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am bar\n'
    )
    # with different branch
    assert raw_patch(sha0, sha2) == (
        b'# HG changeset patch\n'
        b'# User testuser\n'
        b'# Date 259200 0\n'
        b'#      Sun Jan 04 00:00:00 1970 +0000\n'
        b'# Branch stable\n'
        b'# Node ID c4fa3ef1fc8ba157ed8c26584c13492583bf17e9\n'
        b'# Parent  f1a2b5b072f5e59abd43ed6982ab428a6149eda8\n'
        b'added bar\n'
        b'\n'
        b'diff --git a/bar b/bar\n'
        b'new file mode 100644\n'
        b'--- /dev/null\n'
        b'+++ b/bar\n'
        b'@@ -0,0 +1,1 @@\n'
        b'+I am bar\n'
    )
    # when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    # varient 1
    with pytest.raises(grpc.RpcError) as exc_info:
        raw_patch(sha0, sha_not_exists)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'exit status 128' in exc_info.value.details()
    # varient 2
    with pytest.raises(grpc.RpcError) as exc_info:
        raw_patch(sha_not_exists, sha0)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'exit status 128' in exc_info.value.details()


def test_commit_diff(diff_fixture):
    commit_diff = diff_fixture.commit_diff

    wrapper = diff_fixture.repo_wrapper
    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    ctx4 = wrapper.commit_file('zoo', content="I  am in\n zoo\n")
    # Repo structure:
    #
    # @  4 Whitespace changes
    # |
    # o  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    # case 1: when a file renamed
    resp = commit_diff(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'zar'
    assert resp.raw_patch_data == b''
    assert resp.old_mode == resp.new_mode

    # case 2: when a new file added
    resp = commit_diff(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.raw_patch_data == b'@@ -0,0 +1,2 @@\n+I am in\n+zoo\n'
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3: test with enforce_limits
    # Note: For thorough testing, look at comparison tests
    resp = commit_diff(
        left_cid=ctx2.hex(),
        right_cid=ctx3.hex(),
        enforce_limits=True,
        max_files=10,
        max_bytes=100,
        max_lines=1,
    )
    assert len(resp) == 1
    assert resp[0].overflow_marker

    # case 4: test with collapse_diffs
    # Note: For thorough testing, look at comparison tests
    resp = commit_diff(
        left_cid=ctx2.hex(),
        right_cid=ctx3.hex(),
        collapse_diffs=True,
        safe_max_files=10,
        safe_max_bytes=100,
        safe_max_lines=1,
    )
    assert len(resp) == 1
    assert resp[0].collapsed

    # case 5: test with paths
    resp = commit_diff(left_cid=ctx0.hex(), right_cid=ctx3.hex(),
                       paths=[b'zoo'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.from_path == b'zoo'
    assert resp.raw_patch_data == b'@@ -0,0 +1,2 @@\n+I am in\n+zoo\n'

    # case 6: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        commit_diff(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION

    # cases 7 and 8: ignoring whitespace
    WHITESPACE_IGNORE = CommitDiffRequest.WHITESPACE_CHANGES_IGNORE
    WHITESPACE_IGNORE_ALL = CommitDiffRequest.WHITESPACE_CHANGES_IGNORE_ALL
    resp = commit_diff(left_cid=ctx3.hex(), right_cid=ctx4.hex(),
                       whitespace_changes=WHITESPACE_IGNORE)
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.raw_patch_data == (b'@@ -1,2 +1,2 @@\n'
                                   b' I am in\n'
                                   b'-zoo\n+ zoo\n')

    resp = commit_diff(left_cid=ctx3.hex(), right_cid=ctx4.hex(),
                       whitespace_changes=WHITESPACE_IGNORE_ALL)
    assert len(resp) == 0


def test_commit_delta(diff_fixture):
    wrapper = diff_fixture.repo_wrapper
    commit_delta = diff_fixture.commit_delta

    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    # Repo structure:
    #
    # @  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    # case 1: when a file renamed
    resp = commit_delta(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'zar'
    assert resp.old_mode == resp.new_mode

    # case 2: when a new file added
    resp = commit_delta(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3: test with paths
    resp = commit_delta(left_cid=ctx0.hex(), right_cid=ctx3.hex(),
                        paths=[b'zoo'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == resp.to_path
    assert resp.from_path == b'zoo'

    # case 3.a
    resp = commit_delta(left_cid=ctx1.hex(), right_cid=ctx2.hex(),
                        paths=[b'zar'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'zar'
    assert resp.to_path == b'zar'
    assert resp.old_mode == 0
    assert resp.new_mode == 0o100644

    # case 3.b
    resp = commit_delta(left_cid=ctx1.hex(), right_cid=ctx2.hex(),
                        paths=[b'bar'])
    assert len(resp) == 1
    resp = resp[0]
    assert resp.from_path == b'bar'
    assert resp.to_path == b'bar'
    assert resp.old_mode == 0o100644
    assert resp.new_mode == 0

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        commit_delta(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION


def test_diff_stats(diff_fixture):
    diff_stats = diff_fixture.diff_stats
    wrapper = diff_fixture.repo_wrapper

    wrapper.commit_file('bar', content="I am in\nrab\n",
                        message="Add bar")
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    ctx2 = wrapper.commit([b'bar', b'zar'], message="Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    # Repo structure:
    #
    # @  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    # case 1: when a file renamed
    resp = diff_stats(left_cid=ctx1.hex(), right_cid=ctx2.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert resp.old_path == b'bar'
    assert resp.path == b'zar'
    assert not resp.additions
    assert not resp.deletions

    # case 2: when a new file added
    resp = diff_stats(left_cid=ctx2.hex(), right_cid=ctx3.hex())
    assert len(resp) == 1
    resp = resp[0]
    assert not resp.old_path
    assert resp.path == b'zoo'
    assert resp.additions == 2
    assert not resp.deletions

    # case 3: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        diff_stats(sha_not_exists, ctx3.hex())
    assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION


def test_find_changed_paths(diff_fixture):
    wrapper = diff_fixture.repo_wrapper

    (wrapper.path / 'sub').mkdir()
    (wrapper.path / 'sub/foo').write_text('foo content')
    (wrapper.path / 'bar').write_text('bar content')
    (wrapper.path / 'zoo').write_text('zoo content')
    ctx0 = wrapper.commit(rel_paths=['sub/foo', 'bar', 'zoo'],
                          add_remove=True)
    (wrapper.path / 'too').write_text('too content')
    (wrapper.path / 'too').chmod(0o755)
    (wrapper.path / 'sub/foo').write_text('foo content modified')
    (wrapper.path / 'bar').unlink()
    wrapper.command(b'cp', wrapper.repo.root + b'/zoo',
                    wrapper.repo.root + b'/zaz')
    ctx1 = wrapper.commit(rel_paths=['sub/foo', 'bar', 'zaz', 'too'],
                          add_remove=True)

    # Actual test (for ctx1)
    resp_dict = {
        b'too': [(ChangedPaths.Status.ADDED,
                  (OBJECT_MODE_DOES_NOT_EXIST, OBJECT_MODE_EXECUTABLE),
                  )],
        b'sub/foo': [(ChangedPaths.Status.MODIFIED, None)],
        b'bar': [(ChangedPaths.Status.DELETED,
                  (OBJECT_MODE_NON_EXECUTABLE, OBJECT_MODE_DOES_NOT_EXIST),
                  )],
        b'zaz': [(ChangedPaths.Status.COPIED, None)],
    }
    for changed in (diff_fixture.find_changed_paths,  # deprecated
                    diff_fixture.find_changed_paths_commits,  # new style
                    ):
        assert changed(commits=[ctx1.hex()]) == resp_dict
        assert changed(commits=[ctx1.hex()]) == resp_dict

        # when commit_id does not correspond to a commit
        wrong_cid = b'12face12' * 5
        with pytest.raises(grpc.RpcError) as exc_info:
            changed(commits=[wrong_cid])
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
        assert sysstr(wrong_cid) in exc_info.value.details()

    # Testing with two commits
    # in particular reproducing a former loop masking bug
    ctx2 = wrapper.commit_file('sub/foo', content='foo remodified')
    resp_dict[b'sub/foo'].append((ChangedPaths.Status.MODIFIED, None))
    assert diff_fixture.find_changed_paths_commits(
        [ctx1.hex(), ctx2.hex()]) == resp_dict

    # Testing by passing "parents" (changesets to compare to)
    ctx3 = wrapper.commit_file("toto")
    assert diff_fixture.find_changed_paths_commits(
        [ctx3.hex()], compare_to=[ctx1.hex()]
        ) == {
            b'sub/foo': [(ChangedPaths.Status.MODIFIED, None)],
            b'toto': [(ChangedPaths.Status.ADDED,
                       (OBJECT_MODE_DOES_NOT_EXIST,
                        OBJECT_MODE_NON_EXECUTABLE),
                       )],
        }

    # Tree requests
    repo = wrapper.repo
    sub0_oid, sub1_oid = [tree_oid(repo, ctx.hex().decode('ascii'), b'sub')
                          for ctx in (ctx0, ctx1)]
    assert diff_fixture.find_changed_paths_tree(sub0_oid, sub1_oid) == {
        b'foo': [(ChangedPaths.Status.MODIFIED, None)]
    }

    # TreeRequests on different paths. Arguably a lack in HGitaly, since
    # git diff-tree will happily issue provide a diff between arbitrary tree
    # objects. At least we're testing that our error raising works
    with pytest.raises(grpc.RpcError) as exc_info:
        # with our purely conventional oid, it does not matter if the
        # path exists or not for this test
        bogus_oid = tree_oid(repo, ctx0.hex().decode('ascii'), b'other')
        diff_fixture.find_changed_paths_tree(sub0_oid, bogus_oid)

    assert exc_info.value.code() == grpc.StatusCode.UNIMPLEMENTED


def test_find_changed_paths_copy_in_tree(diff_fixture):
    wrapper = diff_fixture.repo_wrapper

    (wrapper.path / 'subdir').mkdir()  # avoid all lengths to be 3
    (wrapper.path / 'subdir/bar').write_text('some bar')
    ctx0 = wrapper.commit(rel_paths=['subdir'], add_remove=True)

    wrapper.command(b'cp', wrapper.repo.root + b'/subdir/bar',
                    wrapper.repo.root + b'/subdir/baz')
    ctx1 = wrapper.commit(rel_paths=['subdir'])

    repo = wrapper.repo

    sub0_oid, sub1_oid = [tree_oid(repo, ctx.hex().decode('ascii'), b'subdir')
                          for ctx in (ctx0, ctx1)]
    assert diff_fixture.find_changed_paths_tree(sub0_oid, sub1_oid) == {
        b'baz': [(ChangedPaths.Status.COPIED, None)],
    }


def test_find_changed_paths_rename(diff_fixture):
    wrapper = diff_fixture.repo_wrapper

    (wrapper.path / 'subdir').mkdir()  # avoid all lengths to be 3
    (wrapper.path / 'subdir/bar').write_text('some bar')
    ctx0 = wrapper.commit(rel_paths=['subdir'], add_remove=True)

    wrapper.command(b'mv', wrapper.repo.root + b'/subdir/bar',
                    wrapper.repo.root + b'/subdir/baz')
    ctx1 = wrapper.commit(rel_paths=['subdir'])

    repo = wrapper.repo

    sub0_oid, sub1_oid = [tree_oid(repo, ctx.hex().decode('ascii'), b'subdir')
                          for ctx in (ctx0, ctx1)]
    ret = diff_fixture.find_changed_paths_commits(
        [ctx1.hex()],
        compare_to=[ctx0.hex()],
        find_renames=False,
    )
    assert ret == {
        b'subdir/baz': [(ChangedPaths.Status.ADDED,
                         (OBJECT_MODE_DOES_NOT_EXIST,
                          OBJECT_MODE_NON_EXECUTABLE),
                         )],
        b'subdir/bar': [(ChangedPaths.Status.DELETED,
                         (OBJECT_MODE_NON_EXECUTABLE,
                          OBJECT_MODE_DOES_NOT_EXIST)
                         )],
    }

    ret = diff_fixture.find_changed_paths_commits(
        [ctx1.hex()],
        compare_to=[ctx0.hex()],
        find_renames=True,
    )
    assert ret == {
        b'subdir/baz': [(ChangedPaths.Status.RENAMED, None)],
    }

    # TODO test the case of rename with duplication:
    # hg cp foo bar; hg mv foo bar2


def test_get_patch_id(diff_fixture):
    wrapper = diff_fixture.repo_wrapper
    patch_id = diff_fixture.get_patch_id

    hex0 = wrapper.commit_file('regular', content='foo\n').hex()
    hex1 = wrapper.commit_file('regular', content='bar\n').hex()
    hex2 = wrapper.commit_file(
        'foo.gz',
        content=b'\x1f\x8b\x08\x08\xd6Q\xc1e\x00\x03foo\x00K'
        b'\xcb\xcf\xe7\x02\x00\xa8e2~\x04\x00\x00\x00',
        message='gzipped file is easy binary').hex()
    hex3 = wrapper.commit_file(
        'foo.gz',
        content=b"\x1f\x8b\x08\x088=\xc2e\x00"
        b"\x03foo\x00K\xcb7\xe2\x02\x00\xb1F'q\x04\x00\x00\x00",
        message='gzipped file is easy binary').hex()

    patch_id1 = patch_id(hex0, hex1)
    patch_id2 = patch_id(hex1, hex2)
    patch_id3 = patch_id(hex2, hex3)

    # symbolic revisions work
    assert patch_id(hex2, b'branch/default') == patch_id3

    assert len(set((patch_id1, patch_id3, patch_id2))) == 3

    #
    # error cases
    #

    # Git not found
    wrapper.write_hgrc(dict(hgitaly={'git-executable': '/does/not/exist'}))
    with pytest.raises(grpc.RpcError) as exc_info:
        patch_id(hex0, hex1)
    exc = exc_info.value
    assert exc.code() == StatusCode.INTERNAL
    assert 'not found' in exc.details()

    # Git found, but not executable
    wrapper.write_hgrc(dict(
        hgitaly={'git-executable': str(wrapper.path / 'regular')}))
    with pytest.raises(grpc.RpcError) as exc_info:
        patch_id(hex0, hex1)
    exc = exc_info.value
    assert exc.code() == StatusCode.INTERNAL
    assert 'not executable' in exc.details()

    # Unknown revisions
    with pytest.raises(grpc.RpcError) as exc_info:
        patch_id(b'unknown', hex1)
    assert exc_info.value.code() == StatusCode.INTERNAL

    with pytest.raises(grpc.RpcError) as exc_info:
        patch_id(hex0, b'unknown')
    assert exc_info.value.code() == StatusCode.INTERNAL
