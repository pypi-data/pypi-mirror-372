# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
from pathlib import Path
from mercurial import (
    node as node_mod,
    pycompat,
)
import pytest
import grpc
import itertools
# from hgitaly.git import EMPTY_TREE_OID
from hgitaly.testing import license_content
from hgitaly.revision import ZERO_SHA
from hgitaly.stub.shared_pb2 import Repository
from hgitaly import stream
from hgitaly.stub.commit_pb2 import (
    FindCommitRequest,
)
from hgitaly.stub.repository_pb2 import (
    CreateRepositoryRequest,
    CreateBundleRequest,
    CreateBundleFromRefListRequest,
    CreateRepositoryFromBundleRequest,
    FindLicenseRequest,
    FindLicenseResponse,
    FindMergeBaseRequest,
    HasLocalBranchesRequest,
    GetArchiveRequest,
    ObjectFormatRequest,
    RemoveRepositoryRequest,
    RepositoryExistsRequest,
    RepositorySizeRequest,
    SearchFilesByContentRequest,
    SearchFilesByNameRequest,
    WriteRefRequest,
)
from hgitaly.stub.shared_pb2 import (
        ObjectFormat,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub
from hgitaly.stub.repository_pb2_grpc import RepositoryServiceStub
from heptapod.testhelpers import (
    LocalRepoWrapper,
    git,
)

from . import skip_comparison_tests
from .comparison import (
    normalize_commit_message,
)
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip

parametrize = pytest.mark.parametrize

TESTS_DATA_DIR = Path(__file__).parent / 'data'
TIP_TAG_NAME = b'tip'


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_find_merge_base(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    git_repo = fixture.git_repo
    wrapper = fixture.hg_repo_wrapper

    # repo structure:
    #
    #   o 3 add animal (branch/stable)
    #   |
    #   | 2 add bar
    #   |/
    #   o 1 add zoo
    #   |
    #   o 0 add foo
    #
    gl_branch = b'branch/default'
    sha0 = wrapper.write_commit('foo').hex()
    git_shas = {
        sha0: git_repo.branches()[gl_branch]['sha']
    }
    ctx1 = wrapper.write_commit('zoo')
    sha1 = ctx1.hex()
    git_shas[sha1] = git_repo.branches()[gl_branch]['sha']
    sha2 = wrapper.write_commit('bar').hex()
    git_shas[sha2] = git_repo.branches()[gl_branch]['sha']
    sha3 = wrapper.write_commit('animal', branch='stable', parent=ctx1).hex()
    git_shas[sha3] = git_repo.branches()[b'branch/stable']['sha']
    # commiting a new root, which will test the case when there
    # is no merge_base (gca)
    sha4 = wrapper.commit_file('tut', branch='other',
                               parent=node_mod.nullid).hex()
    git_shas[sha4] = git_repo.branches()[b'branch/other']['sha']

    if hg_server == 'rhgitaly':
        hgitaly_channel = fixture.rhgitaly_channel
    else:
        hgitaly_channel = fixture.hgitaly_channel
    diff_stubs = dict(
        git=RepositoryServiceStub(fixture.gitaly_channel),
        hg=RepositoryServiceStub(hgitaly_channel),
    )

    def do_rpc(vcs, revisions):
        if vcs == 'git':
            revs = [git_shas.get(rev, rev) for rev in revisions]
            revisions = revs

        request = FindMergeBaseRequest(
            repository=gitaly_repo,
            revisions=revisions,
        )

        response = diff_stubs[vcs].FindMergeBase(request)
        base = pycompat.sysbytes(response.base)
        if not base:
            return base
        return base if vcs == 'git' else git_shas[base]

    list_of_interesting_revs = [b'branch/default', b'branch/stable',
                                sha0, sha1, sha4]
    for rev_pair in itertools.product(list_of_interesting_revs, repeat=2):
        assert do_rpc('hg', rev_pair) == do_rpc('git', rev_pair)

    # test with invalid_argument, as it requires minimum 2 revisions
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', [sha0])
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', [git_shas[sha0]])
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    sha_not_exists = b'deadnode' * 5
    assert (
        do_rpc('hg', [sha0, sha_not_exists])
        ==
        do_rpc('git', [git_shas[sha0], sha_not_exists])
    )


def test_compare_create_repository(
        gitaly_channel, grpc_channel, server_repos_root):
    rel_path = 'sample_repo'
    default_storage = 'default'
    repo_stubs = dict(
        hg=RepositoryServiceStub(grpc_channel),
        git=RepositoryServiceStub(gitaly_channel)
    )

    def do_rpc(vcs, rel_path, storage=default_storage):
        grpc_repo = Repository(relative_path=rel_path,
                               storage_name=storage)
        request = CreateRepositoryRequest(repository=grpc_repo)
        response = repo_stubs[vcs].CreateRepository(request)
        return response

    hg_rel_path = rel_path + '.hg'
    git_rel_path = rel_path + '.git'
    # actual test
    assert do_rpc('hg', hg_rel_path) == do_rpc('git', git_rel_path)

    # when repo already exists (actually its directory)
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', git_rel_path)
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', hg_rel_path)
    assert exc_info_hg.value.code() == exc_info_git.value.code()

    # when storage name is invalid
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', rel_path, storage='cargoship')
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', rel_path, storage='cargoship')
    assert exc_info_hg.value.code() == exc_info_git.value.code()

    # As of 16.8, the broken symlink (pointing to itself) is an INTERNAL
    # error in Gitaly (too many levels of symbolic links),
    # but the more interesting ordinary case
    # of existing directory is still a ALREADY_EXISTS error, so let us
    # test that.
    repo_name = "existing_dir"
    path = (server_repos_root / default_storage / repo_name)
    path.mkdir()
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        do_rpc('hg', repo_name)
    with pytest.raises(grpc.RpcError) as exc_info_git:
        do_rpc('git', repo_name)
    exc_hg, exc_git = exc_info_hg.value, exc_info_git.value
    assert exc_hg.code() == exc_git.code()
    for exc in (exc_hg, exc_git):
        assert 'exists already' in exc.details()


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_remove_repository(gitaly_rhgitaly_comparison,
                           hg_server,
                           server_repos_root):
    fixture = gitaly_rhgitaly_comparison
    grpc_repo = fixture.gitaly_repo
    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RepositoryServiceStub,
        method_name='RemoveRepository',
        request_cls=RemoveRepositoryRequest,
    )
    assert_compare_errors = rpc_helper.assert_compare_errors

    # unknown storage and missing repo
    assert_compare_errors(same_details=False,
                          repository=Repository(storage_name='unknown',
                                                relative_path='/some/path'))
    assert_compare_errors(
        same_details=False,  # RHGitaly displays the path
        repository=Repository(storage_name=grpc_repo.storage_name,
                              relative_path='no/such/path'))
    if hg_server != 'rhgitaly':
        return

    # specific RHGitaly testing, see heptapod#2275
    workdir = (server_repos_root / 'default/+hgitaly/tmp/workdirs'
               / fixture.hgitaly_repo.relative_path / '0')
    os.makedirs(workdir)
    (workdir / 'foo').write_bytes(b'some foo')
    aux_git = (server_repos_root / 'default/+hgitaly/hg-git'
               / fixture.gitaly_repo.relative_path)
    os.makedirs(aux_git)
    (aux_git / 'HEAD').write_bytes(b'ref: refs/heads/branch/default\n')

    rpc_helper.rpc('hg')
    assert not workdir.exists()
    assert not aux_git.exists()


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_repository_exists(gitaly_rhgitaly_comparison,
                           hg_server,
                           server_repos_root):
    fixture = gitaly_rhgitaly_comparison
    grpc_repo = fixture.gitaly_repo
    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='RepositoryExists',
        request_cls=RepositoryExistsRequest,
        hg_server=hg_server,
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare(repository=grpc_repo)
    assert_compare(
        repository=Repository(storage_name=grpc_repo.storage_name,
                              relative_path='no/such/path'))

    # missing repo *message* (!)
    assert_compare_errors(repository=None, same_details=False)

    # unknown storage
    assert_compare_errors(same_details=False,
                          repository=Repository(storage_name='unknown',
                                                relative_path='/some/path'))

    # RHGitaly accepts VCS qualified storage names
    if hg_server == 'rhgitaly':
        for storage in ('hg:default', 'rhg:default'):
            assert not rpc_helper.rpc(
                'hg',
                repository=Repository(storage_name=storage,
                                      relative_path='no/such')
            ).exists
            assert rpc_helper.rpc(
                'hg',
                repository=Repository(
                    storage_name=storage,
                    relative_path=grpc_repo.relative_path,
                )
            ).exists


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_object_format(gitaly_rhgitaly_comparison,
                       hg_server,
                       server_repos_root):
    fixture = gitaly_rhgitaly_comparison
    grpc_repo = fixture.gitaly_repo

    def normalize_unspecified(rpc_helper, resp, vcs='hg', **kw):
        if (
            vcs == 'hg'
            and resp.format == ObjectFormat.OBJECT_FORMAT_UNSPECIFIED
        ):
            # we chose to return UNSPECIFIED, and Gitaly on a repo with default
            # creation options sets and returns SHA1. We might want to revise
            # that later on, but that is not the point of this test.
            resp.format = ObjectFormat.OBJECT_FORMAT_SHA1

    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='ObjectFormat',
        request_cls=ObjectFormatRequest,
        hg_server=hg_server,
        normalizer=normalize_unspecified,
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare(repository=grpc_repo)
    assert_compare_errors(
        same_details=False,
        repository=Repository(storage_name=grpc_repo.storage_name,
                              relative_path='no/such/path'))

    # missing repo *message* (!)
    assert_compare_errors(repository=None, same_details=False)

    # unknown storage
    assert_compare_errors(same_details=False,
                          repository=Repository(storage_name='unknown',
                                                relative_path='/some/path'))


def test_repository_size(gitaly_comparison,
                         server_repos_root):
    fixture = gitaly_comparison
    grpc_repo = fixture.gitaly_repo
    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='RepositorySize',
        request_cls=RepositorySizeRequest,
    )
    # of course Git and Mercurial repository sizes differ, hence
    # we can only compare errors
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare_errors(
        repository=Repository(storage_name=grpc_repo.storage_name,
                              relative_path='no/such/path'))

    # missing repo *message* (!)
    assert_compare_errors(repository=None, same_details=False)

    # unknown storage
    assert_compare_errors(same_details=False,
                          repository=Repository(storage_name='unknown',
                                                relative_path='/some/path'))


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_has_local_branches(gitaly_rhgitaly_comparison,
                            server_repos_root,
                            hg_server):
    fixture = gitaly_rhgitaly_comparison
    grpc_repo = fixture.gitaly_repo
    rpc_helper = fixture.rpc_helper(
        hg_server=hg_server,
        stub_cls=RepositoryServiceStub,
        method_name='HasLocalBranches',
        request_cls=HasLocalBranchesRequest,
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare(repository=grpc_repo)

    # repo does not exist
    assert_compare_errors(
        same_details=False,
        repository=Repository(storage_name=grpc_repo.storage_name,
                              relative_path='no/such/path'))

    # missing repo *message* (!)
    assert_compare_errors(repository=None, same_details=False)

    # unknown storage
    assert_compare_errors(same_details=False,
                          repository=Repository(storage_name='unknown',
                                                relative_path='/some/path'))


def assert_compare_hg_git_created_repos(target_hgrepo, target_gitrepo):
    # assert branches
    br_prefix = b'branch/'
    hgbranches = set(
        [br[0] for br in target_hgrepo.branchmap().iterbranches()])
    gitbranches = set(
        [br[len(br_prefix):] for br in target_gitrepo.branches().keys()])
    assert hgbranches == gitbranches

    # assert tags
    hg_tags = set(target_hgrepo.tags().keys())
    hg_tags.remove(TIP_TAG_NAME)
    git_tags = set(target_gitrepo.tags())
    assert hg_tags == git_tags


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_compare_create_bundle_and_create_repository_from_bundle(
        gitaly_rhgitaly_comparison, tmpdir, server_repos_root, hg_server):
    default_storage = 'default'
    fixture = gitaly_rhgitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    wrapper = fixture.hg_repo_wrapper

    # repo structure:
    #
    #   @ 3 zoo (phase: draft) (amended) (branch:feature)
    #   |
    #   | o 1 bar (phase: public) (tag: v1.2.3)
    #   |/
    #   o 0 foo (phase: public)
    #
    ctx0 = wrapper.commit_file('foo')
    sha0 = ctx0.hex()
    sha1 = wrapper.commit_file('bar').hex()
    wrapper.commit_file('zoo', parent=ctx0, branch='feature')
    wrapper.amend_file('zoo')
    wrapper.set_phase('public', [sha0, sha1])
    wrapper.update(sha1)
    wrapper.command('tag', b'v1.2.3', rev=sha1)
    wrapper.command('gitlab-mirror')

    # repos are not cleaned up immediately, so we need unique names
    # for parametrization to work
    hg_rel_path = hg_server + 'target_hg_repo'
    git_rel_path = hg_server + 'target_git_repo'
    hgrepo_fullpath = server_repos_root / default_storage / hg_rel_path
    gitrepo_fullpath = server_repos_root / default_storage / git_rel_path
    target_repo_msg = dict(
        hg=Repository(relative_path=hg_rel_path,
                      storage_name=default_storage),
        git=Repository(relative_path=git_rel_path,
                       storage_name=default_storage))
    bundle_path = dict(
        hg=tmpdir / 'hg.bundle',
        git=tmpdir / 'git.bundle')
    if hg_server == 'rhgitaly':
        hgitaly_channel = fixture.rhgitaly_channel
    else:
        hgitaly_channel = fixture.hgitaly_channel
    repo_stub = dict(
        hg=RepositoryServiceStub(hgitaly_channel),
        git=RepositoryServiceStub(fixture.gitaly_channel))

    def rpc_create_bundle(vcs):
        request = CreateBundleRequest(repository=gitaly_repo)
        response = repo_stub[vcs].CreateBundle(request)
        with open(bundle_path[vcs], 'wb') as fobj:
            for chunk in response:
                fobj.write(chunk.data)

    def rpc_create_repository_from_bundle(vcs):
        with open(bundle_path[vcs], 'rb') as fobj:
            data = fobj.read()
            first_req_data_size = len(data) // 2
            request1 = CreateRepositoryFromBundleRequest(
                repository=target_repo_msg[vcs],
                data=data[:first_req_data_size])
            request2 = CreateRepositoryFromBundleRequest(
                data=data[first_req_data_size:])
            # create an iterator of requests
            request = (req for req in [request1, request2])
            return repo_stub[vcs].CreateRepositoryFromBundle(request)

    # Actual test
    rpc_create_bundle('hg')
    rpc_create_bundle('git')
    rpc_create_repository_from_bundle('hg')
    rpc_create_repository_from_bundle('git')

    target_hgrepo = LocalRepoWrapper.load(hgrepo_fullpath).repo
    target_gitrepo = git.GitRepo(gitrepo_fullpath)

    assert_compare_hg_git_created_repos(target_hgrepo, target_gitrepo)

    # test error case: when repo already exists
    with pytest.raises(grpc.RpcError) as exc_info_git:
        rpc_create_repository_from_bundle('git')
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        rpc_create_repository_from_bundle('hg')
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    # edge case: empty request
    with pytest.raises(grpc.RpcError) as exc_info_git:
        repo_stub['git'].CreateRepositoryFromBundle(())
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        repo_stub['hg'].CreateRepositoryFromBundle(())
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()


def test_create_bundle_from_ref_list(
        gitaly_comparison, tmpdir, server_repos_root):
    default_storage = 'default'
    fixture = gitaly_comparison
    gitaly_repo = fixture.gitaly_repo
    wrapper = fixture.hg_repo_wrapper

    # repo structure:
    #
    #   @ 3 zoo (branch:toy) (phase: draft) (amended)
    #   |
    #   | o 1 bar (branch: animal) (tag: v1.2.3)
    #   |/
    #   o 0 foo (branch: default)
    #
    ctx0 = wrapper.commit_file('foo')
    sha0 = ctx0.hex()
    sha1 = wrapper.commit_file('bar', branch='animal').hex()
    wrapper.commit_file('zoo', parent=ctx0, branch='toys').hex()
    wrapper.amend_file('zoo')
    wrapper.set_phase('public', [sha0, sha1])
    wrapper.update(sha1)
    wrapper.command('tag', b'v1.2.3', rev=sha1)
    wrapper.command('gitlab-mirror')

    def target_repo_path(vcs, bundle_name):
        relative_path = '%s_%s_repo' % (vcs, bundle_name)
        return server_repos_root / default_storage / relative_path

    def target_repo_msg(vcs, bundle_name):
        relative_path = '%s_%s_repo' % (vcs, bundle_name)
        # relative_path = vcs + bundle_name
        return Repository(relative_path=relative_path,
                          storage_name=default_storage)

    def target_repo(vcs, bundle_name):
        path = target_repo_path(vcs, bundle_name)
        if vcs == 'git':
            return git.GitRepo(path)
        return LocalRepoWrapper.load(path).repo.unfiltered()

    def vcs_qualified_bundle_path(vcs, bundle_name):
        return tmpdir / (vcs + bundle_name)

    repo_stub = dict(
        hg=RepositoryServiceStub(fixture.hgitaly_channel),
        git=RepositoryServiceStub(fixture.gitaly_channel),
    )

    def rpc_create_bundle_from_ref_list(
            vcs, bundle_name, refs, without_repository=False):
        bundle_path = vcs_qualified_bundle_path(vcs, bundle_name)

        def get_request_iter(refs):
            first_req = True
            for chunk in stream.split_batches(refs, 2):
                if first_req and not without_repository:
                    first_req = False
                    yield CreateBundleFromRefListRequest(
                        repository=gitaly_repo,
                        patterns=chunk)
                    continue
                yield CreateBundleFromRefListRequest(patterns=chunk)

        request = get_request_iter(refs)
        response = repo_stub[vcs].CreateBundleFromRefList(request)
        with open(bundle_path, 'wb') as fobj:
            for chunk in response:
                fobj.write(chunk.data)

    def rpc_create_repository_from_bundle(vcs, bundle_name):
        bundle_path = vcs_qualified_bundle_path(vcs, bundle_name)

        def get_request_iter(data):
            first_req = True
            for chunk in stream.split_batches(data, 10):
                if first_req:
                    first_req = False
                    yield CreateRepositoryFromBundleRequest(
                        repository=target_repo_msg(vcs, bundle_name),
                        data=chunk)
                    continue
                yield CreateRepositoryFromBundleRequest(data=chunk)

        with open(bundle_path, 'rb') as fobj:
            data = fobj.read()
            request = get_request_iter(data)
            return repo_stub[vcs].CreateRepositoryFromBundle(request)

    def create_bundle(bundle_name, *refs):
        rpc_create_bundle_from_ref_list('hg', bundle_name, refs)
        rpc_create_bundle_from_ref_list('git', bundle_name, refs)

    def create_repository_from_bundle(bundle_name):
        rpc_create_repository_from_bundle('hg', bundle_name)
        rpc_create_repository_from_bundle('git', bundle_name)

    def assert_compare_created_repository_from_bundle(bundle_name):
        target_hgrepo = target_repo('hg', bundle_name)
        target_gitrepo = target_repo('git', bundle_name)
        assert_compare_hg_git_created_repos(target_hgrepo, target_gitrepo)

    # 1) test with all refs
    allrefs_bundle = 'all_refs_bundle'
    create_bundle(
        allrefs_bundle,
        b'refs/heads/branch/animal', b'refs/heads/branch/toys',
        b'refs/heads/branch/default', b'refs/tags/v1.2.3')
    create_repository_from_bundle(allrefs_bundle)
    # test successful repo creation from bundle
    assert_compare_created_repository_from_bundle(allrefs_bundle)

    # 2) test with some refs
    somerefs_bundle = 'some_refs_bundle'
    create_bundle(
        somerefs_bundle,
        b'refs/heads/branch/default', b'refs/heads/branch/toys')
    create_repository_from_bundle(somerefs_bundle)
    # test successful repo creation from bundle
    assert_compare_created_repository_from_bundle(somerefs_bundle)

    # test error case: no repository object in request
    with pytest.raises(grpc.RpcError) as exc_info_git:
        rpc_create_bundle_from_ref_list(
            'git', 'temp_bname', [b'refs/heads/branch/default'],
            without_repository=True)
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        rpc_create_bundle_from_ref_list(
            'hg', 'temp_bname', [b'refs/heads/branch/default'],
            without_repository=True)
    assert exc_info_hg.value.code() == exc_info_git.value.code()
    assert exc_info_hg.value.details() == exc_info_git.value.details()

    # test error case: error in bundle application

    (tmpdir / 'hgbroken-bundle').write("Obviously garbage")
    (tmpdir / 'gitbroken-bundle').write("Garbage, yes, but Git garbage!")
    with pytest.raises(grpc.RpcError) as exc_info_hg:
        rpc_create_repository_from_bundle('hg', 'broken-bundle')
    with pytest.raises(grpc.RpcError) as exc_info_git:
        rpc_create_repository_from_bundle('git', 'broken-bundle')
    assert exc_info_hg.value.code() == exc_info_git.value.code()

    for vcs in ('hg', 'git'):
        assert not target_repo_path(vcs, 'broken-bundle').exists()


@parametrize('hg_server', ('hgitaly', 'rhgitaly'))
def test_search_files_by_name(gitaly_rhgitaly_comparison, hg_server):
    fixture = gitaly_rhgitaly_comparison

    wrapper = fixture.hg_repo_wrapper
    ctx0 = wrapper.write_commit('afoo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('bar content')
    (sub / 'ba2').write_text('ba2 content')
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    wrapper.commit(rel_paths=['sub/bar', 'sub/ba2'],
                   message="zebar", add_remove=True)

    wrapper.write_commit('animals', message="A branch without subdir",
                         branch='other', parent=ctx0)

    default_rev = b'branch/default'

    rpc_helper = fixture.rpc_helper(stub_cls=RepositoryServiceStub,
                                    hg_server=hg_server,
                                    method_name='SearchFilesByName',
                                    request_cls=SearchFilesByNameRequest,
                                    request_defaults=dict(
                                        ref=default_rev,
                                        limit=0,
                                        offset=0),
                                    streaming=True,
                                    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {
        default_rev: b"zebar",
        b'branch/other': b"A branch without subdir",
    }

    assert_compare(filter='/bar', query='.')
    assert_compare(filter='^sub/', query='.')
    assert_compare(filter='a', query='sub')
    assert_compare(filter='b?r$', query='sub')

    # without filter
    # Note that `git-ls-tree HEAD -- sub` would just return metadata about
    # `sub`, instead of listing its contents.
    assert_compare(query='.')
    assert_compare(query='sub')

    # offset and limit (we have 3 matches without filter)
    assert_compare(query='.', limit=2)
    assert_compare(query='.', limit=1, offset=1)  # both sort lexicographically

    # from a different ref
    assert_compare(filter='bar', query='.', ref=b'branch/other')  # no match
    assert_compare(filter='.*', query='.', ref=b'branch/other')

    # query is mandatory
    assert_compare_errors(filter='/ba')

    # problems with regexp
    assert_compare_errors(filter='\\', query='.', same_details=False)
    assert_compare_errors(filter='a' * 1001, query='.')

    # unknown ref gives back an empty list of files, not an error
    assert_compare(ref=b'unknown', query='.')


def test_search_files_by_content(gitaly_comparison):
    fixture = gitaly_comparison

    wrapper = fixture.hg_repo_wrapper
    wrapper.write_commit('afoo', message="Some foo")
    sub = (wrapper.path / 'sub')
    sub.mkdir()
    (sub / 'bar').write_text('line1\nline2\nbar content\nline4\nline5')
    (sub / 'ba2').write_text('line1\nba2 content')
    (sub / 'ba3').write_text('ba3 content\nline2')
    # This one has a Windows endings, and exhibits that `git grep` normalizes
    # to `\n`. Also Git does not interpret the MacOS classic line ending
    # '\r' and we do. In that case, we can claim our response to be more
    # correct and we will not compare it.
    (sub / 'ba4').write_text('l1\r\nl2\nl3\nba4 content\nline6')
    (sub / 'ba5').write_text('m1\nm2\nm3\nm4\nm5\nm6\nba5 content\n')
    (wrapper.path / 'large').write_text('very large content\n' * 3000)
    # TODO OS indep for paths (actually TODO make wrapper.commit easier to
    # use, e.g., check how to make it accept patterns)
    wrapper.commit(rel_paths=['sub/bar', 'sub/ba2', 'sub/ba3',
                              'sub/ba4', 'sub/ba5', 'large'],
                   message="zebar", add_remove=True)

    default_rev = b'branch/default'

    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='SearchFilesByContent',
        request_cls=SearchFilesByContentRequest,
        request_defaults=dict(
            ref=default_rev,
        ),
        streaming=True,
        error_details_normalizer=lambda s, vcs: s.lower(),
    )
    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {
        default_rev: b"zebar",
    }
    assert_compare(query='no match for this one')
    assert_compare(query='^bar.c')
    assert_compare(query='^ba2.c')   # only one line before match
    assert_compare(query='^ba3.c')   # only one line after match
    assert_compare(query='^ba4.c')   # more than two lines before match
    assert_compare(query='^very')
    assert_compare(query='^l1|ba4')  # two matches with overlapping context
    assert_compare(query='^m1|ba5')  # two matches with non-overlapping context
    assert_compare(query='ConTent')  # several files and case insensity

    # errors if query is missing
    assert_compare_errors()
    assert_compare_errors(ref=b'topic/default/does-not-exist')
    # unresolvable ref
    assert_compare(ref=b'topic/default/does-not-exist', query='foo')
    # missing repo, ref
    assert_compare_errors(ref=b'')
    assert_compare_errors(repository=None)
    fixture.gitaly_repo.relative_path = 'no/such/repo'
    fixture.hgitaly_repo.relative_path = 'no/such/repo'
    assert_compare_errors(query='foo', same_details=False)


def test_find_license(gitaly_rhgitaly_comparison):
    """Test the RHGitaly FindLicense implementation only.

    The Python version has been removed.
    """
    fixture = gitaly_rhgitaly_comparison

    rpc_helper = fixture.rpc_helper(
        hg_server='rhgitaly',
        stub_cls=RepositoryServiceStub,
        method_name='FindLicense',
        request_cls=FindLicenseRequest,
    )
    rpc_helper.assert_compare()

    wrapper = fixture.hg_repo_wrapper
    wrapper.write_commit('LICENSE', content=license_content('GPL-2'))
    # RHGitaly does not try to give the same result as Gitaly, and
    # askalono gives the correct result, whereas go-license-detector and
    # hence Gitaly as GPL2+, although the sample is the full
    # original text of GPLv2.
    assert rpc_helper.rpc('hg') == FindLicenseResponse(
        license_short_name="gpl-2.0-only",
        license_name="GNU General Public License v2.0 only",
        license_url="https://spdx.org/licenses/GPL-2.0-only.html",
        license_path="LICENSE",
        license_nickname="GNU GPLv2",
        )

    wrapper.write_commit('LICENSE', content="Some garbage")
    rpc_helper.assert_compare()


def test_write_ref(gitaly_comparison, server_repos_root):
    fixture = gitaly_comparison
    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='WriteRef',
        request_sha_attrs=['revision', 'old_revision'],
        request_cls=WriteRefRequest,
    )

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
    assert_compare_errors = rpc_helper.assert_compare_errors
    assert_compare = rpc_helper.assert_compare

    wrapper = fixture.hg_repo_wrapper
    sha0 = wrapper.write_commit('afoo', message="Some foo").hex()
    sha1 = wrapper.write_commit('afoo', message="Some foo").hex()
    default_rev = b'branch/default'

    # precondition for the test: mirror worked
    assert fixture.git_repo.branch_titles() == {default_rev: b"Some foo"}

    pipeline_1 = b'refs/pipelines/1'
    assert_compare(ref=pipeline_1, revision=default_rev)
    find_commit_helper.assert_compare(revision=pipeline_1)

    # cases with old_revision
    assert_compare(ref=pipeline_1, revision=sha0, old_revision=sha1)
    assert_compare_errors(ref=pipeline_1, revision=default_rev,
                          old_revision=ZERO_SHA)
    assert_compare_errors(ref=pipeline_1, revision=sha0, old_revision=sha1)

    # old_revision is not honoured for symrefs by Gitaly:
    assert_compare(ref=b'HEAD',
                   revision=b"refs/heads/something",
                   old_revision=b"refs/heads/other")

    # HGitaly is stricter than Gitaly with this (notably keep-arounds
    # consistency checks), and we don't want to downgrade that.
    # See also ordinary, non-comparison, tests for more details

    # unknown storage
    fixture.gitaly_repo.storage_name = 'unknown'
    fixture.hgitaly_repo.storage_name = 'unknown'
    assert_compare_errors(ref=b'refs/pipelines/37', revision=default_rev,
                          same_details=False)


def test_rhgitaly_archive(hgitaly_rhgitaly_comparison):
    fixture = hgitaly_rhgitaly_comparison
    wrapper = fixture.hg_repo_wrapper

    ctx = wrapper.write_commit('foo', content="Foo")
    (wrapper.path / 'sub').mkdir()
    ctx2 = wrapper.write_commit('sub/bar', content="Bar")
    node_str = ctx.hex().decode()
    node2_str = ctx2.hex().decode()

    rpc_helper = fixture.rpc_helper(
        stub_cls=RepositoryServiceStub,
        method_name='GetArchive',
        request_cls=GetArchiveRequest,
        streaming=True,
        request_defaults=dict(
            commit_id=node2_str,
            path=b'',
            format=GetArchiveRequest.Format.Value('TAR'),
            prefix='archive-dir',
        ),
    )

    assert_compare = rpc_helper.assert_compare
    assert_compare_errors = rpc_helper.assert_compare_errors

    assert_compare()
    assert_compare(commit_id=node_str)
    assert_compare(path=b'sub')
    assert_compare_errors(path=b'/etc/passwd')
