# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest
import grpc
import re

from mercurial_testhelpers import (
    as_bytes,
)

from hgitaly.git import (
    EMPTY_TREE_OID,
    NULL_BLOB_OID,
)
from hgitaly.oid import tree_oid
from hgitaly.revision import (
    gitlab_revision_hash,
)
from hgitaly.stub.commit_pb2 import (
    TreeEntryRequest,
    TreeEntryResponse,
)
from hgitaly.stub.diff_pb2 import (
    CommitDeltaRequest,
    CommitDiffRequest,
    DiffStatsRequest,
    FindChangedPathsRequest,
    GetPatchIDRequest,
    RawDiffRequest,
    RawPatchRequest,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub
from hgitaly.stub.diff_pb2_grpc import DiffServiceStub
from .test_blob_tree import oid_mapping  # TODO make it a fixture method

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip

parametrize = pytest.mark.parametrize

INDEX_LINE_REGEXP = re.compile(br'^index \w+\.\.\w+( \d+)?$')


def generate_diff_stubs(fixture, hg_server='hgitaly'):
    if hg_server == 'hgitaly':
        hgitaly_channel = fixture.hgitaly_channel
    elif hg_server == 'rhgitaly':
        hgitaly_channel = fixture.rhgitaly_channel

    return dict(
        git=DiffServiceStub(fixture.gitaly_channel),
        hg=DiffServiceStub(hgitaly_channel)
    )


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_raw_diff(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    wrapper_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_branch = b'branch/default'
    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Some bar")
    git_shas = {
        ctx0.hex(): git_repo.branches()[gl_branch]['sha']
    }
    ctx1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar")
    git_shas[ctx1.hex()] = git_repo.branches()[gl_branch]['sha']
    ctx2 = wrapper.commit_file('zoo', content="I am in\nzoo\n",
                               message="Added zoo")
    git_shas[ctx2.hex()] = git_repo.branches()[gl_branch]['sha']
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    wrapper.command(b'ci', message=b"Rename bar to zar")
    ctx3 = wrapper.repo[b'.']
    git_shas[ctx3.hex()] = git_repo.branches()[gl_branch]['sha']
    # Repo structure:
    #
    # @  3 Rename bar to zar
    # |
    # o  2 Added zoo
    # |
    # o  1 Changes bar
    # |
    # o  0 Some bar
    #

    diff_stubs = generate_diff_stubs(fixture, hg_server)

    def do_rpc(vcs, left_cid, right_cid):
        if vcs == 'git':
            left_cid = git_shas.get(left_cid, left_cid)
            right_cid = git_shas.get(right_cid, right_cid)
        request = RawDiffRequest(
                            repository=wrapper_repo,
                            left_commit_id=left_cid,
                            right_commit_id=right_cid,
                        )
        response = diff_stubs[vcs].RawDiff(request)
        return b''.join(resp.data for resp in response)

    # case 1: when indexline doesn't contain <mode>
    hg_resp_lines = do_rpc('hg', ctx1.hex(), ctx2.hex()).split(b'\n')
    git_resp_lines = do_rpc('git', ctx1.hex(), ctx2.hex()).split(b'\n')
    INDEX_LINE_POSITION = 2
    hg_indexline = hg_resp_lines[INDEX_LINE_POSITION]
    git_indexline = git_resp_lines[INDEX_LINE_POSITION]
    # check that index line has the correct format
    assert INDEX_LINE_REGEXP.match(hg_indexline) is not None
    assert INDEX_LINE_REGEXP.match(git_indexline) is not None
    # actual comparison
    del hg_resp_lines[INDEX_LINE_POSITION]
    del git_resp_lines[INDEX_LINE_POSITION]
    assert hg_resp_lines == git_resp_lines

    # case 2: when indexline has <mode> (it happens when mode didn't change)
    hg_resp_lines = do_rpc('hg', ctx0.hex(), ctx1.hex()).split(b'\n')
    git_resp_lines = do_rpc('git', ctx0.hex(), ctx1.hex()).split(b'\n')
    INDEX_LINE_POSITION = 1
    hg_indexline = hg_resp_lines[INDEX_LINE_POSITION]
    git_indexline = git_resp_lines[INDEX_LINE_POSITION]
    # check the mode
    assert INDEX_LINE_REGEXP.match(hg_indexline).group(1) == b' 100644'
    assert INDEX_LINE_REGEXP.match(git_indexline).group(1) == b' 100644'

    # case 3: test with file renaming
    hg_resp = do_rpc('hg', ctx2.hex(), ctx3.hex())
    git_resp = do_rpc('git', ctx2.hex(), ctx3.hex())
    assert hg_resp is not None
    assert hg_resp == git_resp

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc('hg', sha_not_exists, ctx2.hex())
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc('git', sha_not_exists, ctx2.hex())
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL

    # case 5: EMPTY_TREE_OID to represent null commit on the left
    hg_resp_lines = do_rpc('hg', EMPTY_TREE_OID, ctx0.hex()).split(b'\n')
    git_resp_lines = do_rpc('git', EMPTY_TREE_OID, ctx0.hex()).split(b'\n')
    INDEX_LINE_POSITION = 2
    assert (hg_resp_lines[INDEX_LINE_POSITION].split(b'..')[0]
            ==
            git_resp_lines[INDEX_LINE_POSITION].split(b'..')[0])
    del hg_resp_lines[INDEX_LINE_POSITION]
    del git_resp_lines[INDEX_LINE_POSITION]
    assert hg_resp_lines == git_resp_lines

    # case 6: EMPTY_TREE_OID to represent null commit on the right
    git_resp_lines = do_rpc('git', ctx0.hex(), EMPTY_TREE_OID).split(b'\n')
    hg_resp_lines = do_rpc('hg', ctx0.hex(), EMPTY_TREE_OID).split(b'\n')
    INDEX_LINE_POSITION = 2
    assert (hg_resp_lines[INDEX_LINE_POSITION].rsplit(b'..')[-1]
            ==
            git_resp_lines[INDEX_LINE_POSITION].rsplit(b'..')[-1])
    del hg_resp_lines[INDEX_LINE_POSITION]
    del git_resp_lines[INDEX_LINE_POSITION]
    assert hg_resp_lines == git_resp_lines


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_raw_patch(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_branch = b'branch/default'
    ctx0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Some bar")
    git_sha0 = git_repo.branches()[gl_branch]['sha']

    diff_stubs = generate_diff_stubs(fixture, hg_server)

    def do_rpc(vcs, left_cid, right_cid):
        request = RawPatchRequest(
            repository=gitaly_repo,
            left_commit_id=left_cid,
            right_commit_id=right_cid,
        )
        response = diff_stubs[vcs].RawPatch(request)
        return b''.join(resp.data for resp in response)

    # Here we are only comparing for error cases, as HGitaly returns Hg patches
    # and Gitaly returns Git pataches. For more, look at diff.RawPatch()
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', sha_not_exists, ctx0.hex())
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', sha_not_exists, git_sha0)
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()


def test_compare_commit_diff(gitaly_comparison):
    fixture = gitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper
    gl_branch = b'branch/default'

    wrapper.commit_file('bar', content='I am in\nrab\n',
                        message='Add bar')
    ctx1 = wrapper.commit_file('bar', content='I am in\nbar\n',
                               message='Changes bar')
    git_sha1 = git_repo.branches()[gl_branch]['sha']
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    wrapper.command(b'ci', message=b'Rename bar to zar')
    ctx3 = wrapper.commit_file('zoo', content='I am in \n zoo\n',
                               message='Added zoo')
    git_sha3 = git_repo.branches()[gl_branch]['sha']
    ctx4 = wrapper.commit_file('zoo', content='I am in\nzoo\n',
                               message='zoo: change whitespace')
    git_sha4 = git_repo.branches()[gl_branch]['sha']
    ctx5 = wrapper.commit_file('too', content='I am in\ntoo\n',
                               message='Added too')
    git_sha5 = git_repo.branches()[gl_branch]['sha']
    ctx6 = wrapper.commit_file('hulk', content=b'abcd\n' * 1024 + b'foobar\n',
                               message='Added hulk')
    git_sha6 = git_repo.branches()[gl_branch]['sha']
    # Repo structure:
    #
    # @  5 Added too
    # |
    # o  4 zoo: remove whitespace
    # |
    # o  3 Added zoo
    # |
    # o  2 Rename bar to zar
    # |
    # o  1 Changes bar
    # |
    # o  0 Add bar
    #

    def do_rpc(vcs, left_cid, right_cid, **opts):
        request = CommitDiffRequest(
                    repository=gitaly_repo,
                    left_commit_id=left_cid,
                    right_commit_id=right_cid,
                    **opts,
                )
        diff_stubs = dict(git=DiffServiceStub(fixture.gitaly_channel),
                          hg=DiffServiceStub(fixture.hgitaly_channel))
        response = diff_stubs[vcs].CommitDiff(request)
        final = []
        # `from_id`, `to_id` are different in hgitaly/gitaly responses
        # for equality setting them to empty string
        for resp in response:
            resp.from_id = ''
            resp.to_id = ''
            final.append(resp)
        return final

    def rpc_diff_size(*args, **kwargs):
        """Perform RPC and return the total length of patch data it gives."""
        return sum(len(chunk.raw_patch_data)
                   for chunk in do_rpc(*args, **kwargs))

    # case 1: actual test (rename + new file + content change)
    hg_resp = do_rpc('hg', left_cid=ctx1.hex(),
                     right_cid=ctx3.hex())
    git_resp = do_rpc('git', left_cid=git_sha1,
                      right_cid=git_sha3)
    assert hg_resp == git_resp

    # case 2: test with enforce_limits opt
    # thresholds dict with limits checked manually
    thresholds = dict(
        max_files=3,
        max_bytes=29,
        max_lines=5,
        max_patch_bytes=31,
    )
    for lm in [None, 'max_files', 'max_bytes', 'max_lines', 'max_patch_bytes']:
        new_thresholds = thresholds.copy()
        if lm is not None:
            new_thresholds[lm] -= 1

        hg_resp = do_rpc(
            'hg', left_cid=ctx1.hex(),
            right_cid=ctx5.hex(),
            enforce_limits=True,
            **new_thresholds,
        )
        git_resp = do_rpc(
            'git', left_cid=git_sha1,
            right_cid=git_sha5,
            enforce_limits=True,
            **new_thresholds,
        )
        assert hg_resp == git_resp

    # case 3: test with collapse_diffs opt
    # thresholds dict with limits checked manually
    thresholds = dict(
        safe_max_files=3,
        safe_max_bytes=29,
        safe_max_lines=5,
    )
    for lm in [None, 'safe_max_files', 'safe_max_bytes', 'safe_max_lines']:
        new_thresholds = thresholds.copy()
        if lm is not None:
            new_thresholds[lm] -= 1
        hg_resp = do_rpc(
            'hg', left_cid=ctx1.hex(),
            right_cid=ctx5.hex(),
            collapse_diffs=True,
            **new_thresholds,
        )
        git_resp = do_rpc(
            'git', left_cid=git_sha1,
            right_cid=git_sha5,
            collapse_diffs=True,
            **new_thresholds,
        )
        assert hg_resp == git_resp

    # case 4: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', sha_not_exists, ctx3.hex())
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', sha_not_exists, git_sha3)
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    # case 5: when response.raw_patch_data size exceeds DIFF_MSG_SIZE_THRESHOLD
    hg_resp = do_rpc('hg', left_cid=ctx5.hex(),
                     right_cid=ctx6.hex())
    git_resp = do_rpc('git', left_cid=git_sha5,
                      right_cid=git_sha6)
    assert hg_resp == git_resp
    assert len(hg_resp) == 2

    # case 6: whitespace options
    WHITESPACE_IGNORE = CommitDiffRequest.WHITESPACE_CHANGES_IGNORE
    WHITESPACE_IGNORE_ALL = CommitDiffRequest.WHITESPACE_CHANGES_IGNORE_ALL
    hg_resp = do_rpc('hg', left_cid=ctx3.hex(),
                     right_cid=ctx4.hex(),
                     whitespace_changes=WHITESPACE_IGNORE)
    git_resp = do_rpc('git', left_cid=git_sha3,
                      right_cid=git_sha4,
                      whitespace_changes=WHITESPACE_IGNORE)
    # Git and Mercurial differ in how they represent the line with
    # ignored changes. Both mark it as unchanged in the patch, but
    # Git displays the new value for context Mercurial displays the old value:
    hg_raw = hg_resp[0].raw_patch_data.splitlines()
    # we don't change the first char (' ', '-', or '+')
    hg_raw[1] = hg_raw[1][:-1]
    hg_raw.append(b'')  # for final EOL
    hg_resp[0].raw_patch_data = b'\n'.join(hg_raw)
    assert hg_resp == git_resp

    hg_size = rpc_diff_size('hg', left_cid=ctx3.hex(),
                            right_cid=ctx4.hex(),
                            whitespace_changes=WHITESPACE_IGNORE_ALL)
    git_size = rpc_diff_size('git', left_cid=git_sha3,
                             right_cid=git_sha4,
                             whitespace_changes=WHITESPACE_IGNORE_ALL)
    assert hg_size == git_size


def test_compare_commit_delta(gitaly_comparison):
    fixture = gitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper
    gl_branch = b'branch/default'

    sha0 = wrapper.commit_file('bar', content="I am in\nrab\n",
                               message="Add bar").hex()
    git_shas = {
        sha0: git_repo.branches()[gl_branch]['sha']
    }
    sha1 = wrapper.commit_file('bar', content="I am in\nbar\n",
                               message="Changes bar").hex()
    git_shas[sha1] = git_repo.branches()[gl_branch]['sha']
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    sha2 = wrapper.commit([b'zar', b'bar'], message=b"Rename bar to zar").hex()
    git_shas[sha2] = git_repo.branches()[gl_branch]['sha']
    sha3 = wrapper.commit_file('zoo', content="I am in \nzoo\n",
                               message="Added zoo").hex()
    git_shas[sha3] = git_repo.branches()[gl_branch]['sha']
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

    diff_stubs = dict(git=DiffServiceStub(fixture.gitaly_channel),
                      hg=DiffServiceStub(fixture.hgitaly_channel))

    def do_rpc(vcs, left_cid, right_cid, **opts):
        request = CommitDeltaRequest(
                    repository=gitaly_repo,
                    left_commit_id=left_cid,
                    right_commit_id=right_cid,
                    **opts,
                )
        response = diff_stubs[vcs].CommitDelta(request)
        final = [resp.deltas for resp in response if resp.deltas]
        # `from_id`, `to_id` are different in hgitaly/gitaly responses
        # for equality setting them to empty string
        for deltas in final:
            for delta in deltas:
                delta.from_id = ''
                delta.to_id = ''
        return final

    def do_assert(left_cid, right_cid, paths):
        assert (
            do_rpc('hg', left_cid, right_cid, paths=paths)
            ==
            do_rpc('git', git_shas[left_cid], git_shas[right_cid], paths=paths)
        )

    # actual test
    test_paths = [
        [],
        [b'zoo', b'zar'],
        [b'zoo', b'bar'],
        [b'bar', b'zar'],
        [b'zoo'],
        [b'bar'],
        [b'zar'],
    ]
    for left_cid in [sha0, sha1, sha2, sha3]:
        for right_cid in [sha0, sha1, sha2, sha3]:
            for paths in test_paths:
                do_assert(left_cid, right_cid, paths=paths)

    # when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', sha_not_exists, sha3)
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', sha_not_exists, git_shas[sha3])
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()


def test_compare_diff_stats(gitaly_comparison):
    fixture = gitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper
    gl_branch = b'branch/default'

    ctx0 = wrapper.commit_file('bar',
                               content="first_line\n"
                                       "second_line\n"
                                       "third_line\n",
                               message="Add bar")
    git_sha0 = git_repo.branches()[gl_branch]['sha']
    wrapper.commit_file('bar',
                        content="first_line\n"
                                "second_line\n"
                                "third_line_updated\n",
                        message="Changes bar")
    wrapper.command(b'mv', wrapper.repo.root + b'/bar',
                    wrapper.repo.root + b'/zar')
    wrapper.commit([b'zar', b'bar'], message=b"Rename bar to zar")
    ctx3 = wrapper.commit_file('zoo', content="I am in zoo\n",
                               message="Added zoo")
    git_sha3 = git_repo.branches()[gl_branch]['sha']
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

    def do_rpc(vcs, left_cid, right_cid, **opts):
        request = DiffStatsRequest(
                    repository=gitaly_repo,
                    left_commit_id=left_cid,
                    right_commit_id=right_cid,
                    **opts,
                )
        diff_stubs = dict(git=DiffServiceStub(fixture.gitaly_channel),
                          hg=DiffServiceStub(fixture.hgitaly_channel))
        response = diff_stubs[vcs].DiffStats(request)
        return [resp.stats for resp in response]

    # case 1: actual test
    hg_resp = do_rpc('hg', left_cid=ctx0.hex(),
                     right_cid=ctx3.hex())
    git_resp = do_rpc('git', left_cid=git_sha0,
                      right_cid=git_sha3)
    assert hg_resp == git_resp

    # case 2: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', sha_not_exists, ctx3.hex())
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', sha_not_exists, git_sha3)
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()


def test_compare_find_changed_paths(gitaly_comparison):
    fixture = gitaly_comparison
    wrapper_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    gl_branch = b'branch/default'
    (wrapper.path / 'sub').mkdir()
    (wrapper.path / 'sub/foo').write_text('foo content')
    (wrapper.path / 'bar').write_text('bar content')
    ctx0 = wrapper.commit(rel_paths=['sub/foo', 'bar'],
                          add_remove=True)
    git_sha0 = git_repo.branches()[gl_branch]['sha']

    (wrapper.path / 'zoo').write_text('zoo content')
    (wrapper.path / 'zoo').chmod(0o755)
    (wrapper.path / 'sub/foo').write_text('foo content modified')
    (wrapper.path / 'bar').unlink()
    wrapper.command(b'rm', wrapper.repo.root + b'/bar')
    ctx1 = wrapper.commit(rel_paths=['sub/foo', 'bar', 'zoo'],
                          add_remove=True)
    git_sha1 = git_repo.branches()[gl_branch]['sha']

    diff_stubs = dict(
        git=DiffServiceStub(fixture.gitaly_channel),
        hg=DiffServiceStub(fixture.hgitaly_channel)
    )

    oid_to_git = oid_mapping(fixture,
                             ((ctx.hex(), path, 'blob')
                              for ctx, path in (
                                      (ctx0, b'sub/foo'),
                                      (ctx1, b'sub/foo'),
                                      (ctx0, b'bar'),
                                      (ctx1, b'zoo'),
                              )))
    oid_to_git[NULL_BLOB_OID] = NULL_BLOB_OID

    def do_rpc_inner(vcs, **req_kwargs):
        """Transitional to accomodate deprecated and new style"""

        request = FindChangedPathsRequest(repository=wrapper_repo,
                                          **req_kwargs)
        response = diff_stubs[vcs].FindChangedPaths(request)
        final = []
        for resp in response:
            paths = sorted(resp.paths, key=lambda o: o.path)
            final.append(paths)
            if vcs == 'hg':
                for path in paths:
                    if path.old_blob_id:
                        path.old_blob_id = oid_to_git[path.old_blob_id]
                    if path.new_blob_id:
                        path.new_blob_id = oid_to_git[path.new_blob_id]
        return final

    def do_rpc_depr(vcs, commits):
        return do_rpc_inner(vcs, commits=commits)

    CommitRequest = FindChangedPathsRequest.Request.CommitRequest

    def do_rpc_commits(vcs, commits, compare_to=(), **kw):
        """Using the new (as of Gitaly 15.2 CommitRequest message.

        for more cases, use do_rpc_inner directly
        :param compare_to: if given, will be used in all requests.
        """
        return do_rpc_inner(
            vcs,
            requests=[
                FindChangedPathsRequest.Request(
                    commit_request=CommitRequest(
                        commit_revision=c,
                        parent_commit_revisions=compare_to))
                for c in commits],
            **kw
        )

    TreeRequest = FindChangedPathsRequest.Request.TreeRequest

    def git_tree(revision, path):
        stub = CommitServiceStub(fixture.gitaly_channel)
        resps = list(stub.TreeEntry(
            TreeEntryRequest(repository=wrapper_repo,
                             revision=revision,
                             path=path)
        ))
        assert len(resps) == 1
        assert resps[0].type == TreeEntryResponse.ObjectType.TREE
        return resps[0].oid

    def hg_tree(revision, path):
        repo = wrapper.repo
        return tree_oid(repo,
                        gitlab_revision_hash(repo, revision).decode('ascii'),
                        path)

    tree_finders = dict(hg=hg_tree, git=git_tree)

    def do_rpc_tree(vcs, left_commit, right_commit, path):
        # for now we support only the case where all trees are the same subdir
        # in different commits.

        tree_finder = tree_finders[vcs]
        return do_rpc_inner(
            vcs,
            requests=[
                FindChangedPathsRequest.Request(
                    tree_request=TreeRequest(
                        left_tree_revision=tree_finder(left_commit, path),
                        right_tree_revision=tree_finder(right_commit, path))
                )
            ]
        )

    assert (do_rpc_tree('git', git_sha0, git_sha1, b'sub')
            ==
            do_rpc_tree('hg', ctx0.hex(), ctx1.hex(), b'sub')
            )

    # case 1: actual test
    assert do_rpc_depr('git', [git_sha1]) == do_rpc_depr('hg', [ctx1.hex()])
    assert (do_rpc_commits('git', [git_sha1])
            ==
            do_rpc_commits('hg', [ctx1.hex()])
            )

    # Note: khanchi97: As per the command used by gitaly for FindChangedPaths
    # cmd: `git diff-tree --stdin -z -m -r --name-status --no-renames`
    #      `--no-commit-id --diff-filter=AMDTC`
    # -> git doesn't return anything for the first commit, although I assume
    # it should, so not testing for ctx0 for now.

    # case 2: when commit_id does not correspond to a commit
    sha_not_exists = b'deadnode' * 5

    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc_depr('hg', [ctx0.hex(), sha_not_exists])
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc_depr('git', [git_sha0, sha_not_exists])
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc_commits('hg', [ctx0.hex(), sha_not_exists])
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc_commits('git', [git_sha0, sha_not_exists])
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    # case 3: tree requests
    assert (do_rpc_tree('git', git_sha0, git_sha1, b'sub')
            ==
            do_rpc_tree('hg', ctx0.hex(), ctx1.hex(), b'sub')
            )

    # can't compare with copies because Gitaly actually fails to
    # detect them (it does not pass the `-C` flag to `git diff-tree`,
    # at least as of gitaly@2b069d853)
    # not sure if that counts as a bug on their side or is really
    # intended, even though the copied case is part of protocol.

    # case 4: several requests, checking our analysis that results are
    # not merged.
    # Let's begin with the extreme case, twice the same commit:
    assert (do_rpc_commits('git', [git_sha1, git_sha1])
            ==
            do_rpc_commits('hg', [ctx1.hex(), ctx1.hex()])
            )
    # Less disturbing, let's make a new commit, modifying `foo` once again
    (wrapper.path / 'sub/foo').write_text('foo content re modified')
    hg_sha2 = wrapper.commit(rel_paths=['sub']).hex()
    git_sha2 = git_repo.branches()[gl_branch]['sha']
    fixture.invalidate()

    oid_to_git.update(oid_mapping(fixture,
                                  [(hg_sha2, b'sub/foo', 'blob')]))
    assert (do_rpc_commits('git', [git_sha1, git_sha2])
            ==
            do_rpc_commits('hg', [ctx1.hex(), hg_sha2])
            )

    # case 4: merge
    # In case of several parents, `git diff-tree -m`, on which the Gitaly
    # implementation is based would display the diffs against each parent,
    # one after the other.

    other_ctx = wrapper.commit_file('new', branch='other', parent=ctx0,
                                    content="new file in branch")
    wrapper.update(2)
    wrapper.command('merge', other_ctx.hex())
    # the foo file will appeared to be modified when compared with each parent
    (wrapper.path / 'sub/foo').write_text('something else entirely')
    # TODO implement comiit with "always matcher" in mercurial-testhelpers
    # (merge commits don't allow specifying paths, even if we list all)
    wrapper.command('commit', message=b'the merge')
    hg_sha3 = wrapper.repo[b'tip'].hex()
    git_sha3 = git_repo.branches()[gl_branch]['sha']
    fixture.invalidate()

    oid_to_git.update(
        oid_mapping(fixture,
                    ((sha, path, 'blob') for sha, path in (
                        (hg_sha3, b'new'),
                        (hg_sha3, b'sub/foo'),
                        (hg_sha3, b'zoo'),
                        (other_ctx.hex(), b'bar'),
                        (other_ctx.hex(), b'new'),
                        (other_ctx.hex(), b'sub/foo'),
                        ))))
    assert (do_rpc_commits('git', [git_sha3])
            ==
            do_rpc_commits('hg', [hg_sha3])
            )

    # case 5: passing "parents" explicitely
    hg_sha4 = wrapper.commit_file("toto").hex()
    git_sha4 = git_repo.branches()[gl_branch]['sha']
    fixture.invalidate()

    oid_to_git.update(
        oid_mapping(fixture,
                    ((sha, path, 'blob') for sha, path in (
                        (hg_sha4, b'new'),
                        (hg_sha4, b'sub/foo'),
                        (hg_sha4, b'toto'),
                        (hg_sha4, b'zoo'),
                        ))))
    assert (do_rpc_commits('git', [git_sha4], compare_to=[git_sha0])
            ==
            do_rpc_commits('hg', [hg_sha4], compare_to=[ctx0.hex()])
            )

    # case 6: with renames
    repo_path = wrapper.path
    wrapper.command(
        'mv', as_bytes(repo_path / 'zoo'), as_bytes(repo_path / 'zaz')
    )
    wrapper.command('commit', message=b'cp/mv')
    hg_sha5 = wrapper.repo[b'tip'].hex()
    git_sha5 = git_repo.branches()[gl_branch]['sha']
    fixture.invalidate()
    oid_to_git.update(oid_mapping(fixture,
                                  [(hg_sha5, b'zaz', 'blob')]))

    for find_renames in (False, True):
        assert (do_rpc_commits('git', [git_sha5], find_renames=find_renames)
                ==
                do_rpc_commits('hg', [hg_sha5], find_renames=find_renames)
                )


def test_compare_get_patch_id(gitaly_comparison):
    fixture = gitaly_comparison
    wrapper = fixture.hg_repo_wrapper
    rpc_helper = fixture.rpc_helper(
        stub_cls=DiffServiceStub,
        method_name='GetPatchID',
        request_cls=GetPatchIDRequest,
        request_sha_attrs=['old_revision', 'new_revision'],
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    hex0 = wrapper.commit_file('regular', content='foo\n').hex()
    hex1 = wrapper.commit_file('regular', content='bar\n', topic='bar').hex()

    gl_branch = b'branch/default'
    gl_topic = b'topic/default/bar'

    # regular operation with symbolic or sha revisions
    assert_compare(old_revision=gl_branch, new_revision=gl_topic)
    assert_compare(old_revision=hex0, new_revision=gl_topic)
    assert_compare(old_revision=gl_branch, new_revision=hex1)

    # errors on unknown revisions (for now INTERNAL with Gitaly, highly
    # probable that it will become something else and that details really
    # do not matter)
    assert_compare_errors(old_revision=gl_branch, new_revision=b'unknown',
                          same_details=False)
    assert_compare_errors(old_revision=b'unknown', new_revision=gl_branch,
                          same_details=False)
