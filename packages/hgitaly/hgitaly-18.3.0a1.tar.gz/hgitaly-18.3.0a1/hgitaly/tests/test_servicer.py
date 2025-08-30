# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import gc
import grpc
import os
from pathlib import Path
import pytest
from mercurial import (
    hg,
    pycompat,
)

from heptapod import obsutil

from mercurial_testhelpers import (
    as_bytes,
)

from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..testing.context import (
    FakeServicerContext,
    metadatum,
)
from ..testing.storage import GIT_REPOS_STOWED_AWAY_PATH
from ..servicer import (
    HG_GIT_MIRRORING_MD_KEY,
    NATIVE_PROJECT_MD_KEY,
    ACCEPT_MR_IID_KEY,
    SKIP_HOOKS_MD_KEY,
    PY_HEPTAPOD_SKIP_HOOKS,
    HGitalyServicer,
)
from ..stub.shared_pb2 import (
    Repository,
    User,
)
from ..stub.repository_pb2 import HasLocalBranchesRequest
from ..stub.repository_pb2_grpc import RepositoryServiceStub


class AbortContext(Exception):
    """Raised by FakeContext.abort.

    gRPC's context.abort raises `Exception()` (sic), which is
    inconvenient for testing.
    """


class FakeContext(FakeServicerContext):

    _invocation_metadata = ()

    def abort(self, code, message):
        self.code = code
        self.message = message
        raise AbortContext()

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

    def invocation_metadata(self):
        return self._invocation_metadata

    def set_invocation_md(self, md):
        self._invocation_metadata += (md, )


def test_load_repo(tmpdir):
    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))
    # context is used for error raising only
    context = FakeContext()

    wrapper = LocalRepoWrapper.init(storage_root.join('awesome-proj.hg'))
    loaded = servicer.load_repo(Repository(storage_name='storname',
                                           relative_path='awesome-proj.hg'),
                                context)
    assert loaded.root == wrapper.repo.root

    # In practice, requests from the Rails app will assume the relevant
    # path to end in `.git`, we need to ignore that.
    loaded = servicer.load_repo(Repository(storage_name='storname',
                                           relative_path='awesome-proj.git'),
                                context)
    assert loaded.root == wrapper.repo.root

    with pytest.raises(KeyError) as exc_info:
        servicer.load_repo_inner(Repository(storage_name='dream',
                                            relative_path='dream-proj.hg'),
                                 context)
    assert exc_info.value.args == ('storage', 'dream')

    with pytest.raises(AbortContext):
        servicer.load_repo(Repository(storage_name='dream',
                                      relative_path='dream-proj.hg'),
                           context)
    assert context.code == grpc.StatusCode.NOT_FOUND


def test_is_repo_aux_git(tmpdir):
    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))

    assert not servicer.is_repo_aux_git(None)
    assert not servicer.is_repo_aux_git(
        Repository(storage_name='storname',
                   relative_path='some/repo.git')
    )
    assert servicer.is_repo_aux_git(
        Repository(
            storage_name='storname',
            relative_path=str(GIT_REPOS_STOWED_AWAY_PATH / 'repo.git'))
    )


def test_load_repo_for_mutation(tmpdir):
    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))
    LocalRepoWrapper.init(storage_root.join('awesome-proj.hg'))
    grpc_repo = Repository(storage_name='storname',
                           relative_path='awesome-proj.hg')
    user = User(gl_id='whatever', name=b"Georges", email=b'gr@heptapod.test')

    context = FakeContext()
    loaded = servicer.load_repo(grpc_repo, context, for_mutation_by=user)
    assert loaded.ui.environ[b'HEPTAPOD_USERINFO_GL_ID'] == b'whatever'
    assert loaded.ui.configbool(b'heptapod', b'native') is False
    assert loaded.ui.configbool(b'heptapod', b'no-git') is False

    context.set_invocation_md(metadatum(NATIVE_PROJECT_MD_KEY, 'True'))
    loaded = servicer.load_repo(grpc_repo, context, for_mutation_by=user)
    assert loaded.ui.configbool(b'heptapod', b'native') is True
    assert loaded.ui.configbool(b'heptapod', b'no-git') is True

    context.set_invocation_md(metadatum(HG_GIT_MIRRORING_MD_KEY, 'True'))
    loaded = servicer.load_repo(grpc_repo, context, for_mutation_by=user)
    assert loaded.ui.configbool(b'heptapod', b'native') is True
    assert loaded.ui.configbool(b'heptapod', b'no-git') is False

    context.set_invocation_md(metadatum(ACCEPT_MR_IID_KEY, '609'))
    loaded = servicer.load_repo(grpc_repo, context, for_mutation_by=user)
    assert loaded.ui.environ[b'HEPTAPOD_ACCEPT_MR_IID'] == b'609'

    context.set_invocation_md(metadatum(SKIP_HOOKS_MD_KEY, 'True'))
    loaded = servicer.load_repo(grpc_repo, context, for_mutation_by=user)
    assert loaded.ui.environ[PY_HEPTAPOD_SKIP_HOOKS] == b'yes'

    with pytest.raises(AbortContext):
        servicer.load_repo(grpc_repo, context, for_mutation_by=User())
    assert context.code == grpc.StatusCode.INVALID_ARGUMENT


def test_load_repo_gc(tmpdir):
    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))
    # context is used for error raising only
    context = FakeContext()

    src_path = storage_root.join('awesome-proj.hg')
    dst_path = storage_root.join('shared.hg')
    LocalRepoWrapper.init(src_path)
    LocalRepoWrapper.share_from_path(src_path, dst_path)

    from mercurial.repoview import _filteredrepotypes as frt
    # we're checking that stuff doesn't accumulate in this frt
    # since it is a cache, we can start with a clean slate:
    frt.clear()

    loaded = servicer.load_repo(Repository(storage_name='storname',
                                           relative_path='shared.hg'),
                                context)
    # not what we really need, but will help demonstrate that proper removal
    # from frt actually happens.
    assert len(frt) > 0

    # let's even make a loop of references:
    hg.sharedreposource(loaded).dst_repo = loaded

    del loaded
    gc.collect()

    # this may turn out to be optimistic
    assert len(frt) == 0


def test_errors_propagation(grpc_channel, server_repos_root):
    # Taking a random RPC to check that the client receives the
    # proper error response
    repo_stub = RepositoryServiceStub(grpc_channel)

    with pytest.raises(grpc.RpcError) as exc_info:
        repo_stub.HasLocalBranches(HasLocalBranchesRequest(
            repository=Repository(storage_name='dream', relative_path='')))
    exc = exc_info.value

    assert exc.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'dream' in exc.details()

    with pytest.raises(grpc.RpcError) as exc_info:
        repo_stub.HasLocalBranches(HasLocalBranchesRequest(
            repository=Repository(storage_name='default',
                                  relative_path='not_here')))
    exc = exc_info.value

    assert exc.code() == grpc.StatusCode.NOT_FOUND
    assert 'not_here' in exc.details()


def test_temp_dir(tmpdir):
    # context is used for error raising only
    context = FakeContext()
    servicer = HGitalyServicer(dict(default=as_bytes(tmpdir)))

    path = servicer.temp_dir('default', context, ensure=False)
    path = Path(os.fsdecode(path))
    assert path.is_relative_to(tmpdir)
    assert not path.exists()

    assert servicer.temp_dir('default', context, ensure=True) == bytes(path)
    assert path.exists()

    with pytest.raises(KeyError) as exc_info:
        servicer.temp_dir_inner('unknown', context)
    assert exc_info.value.args == ('storage', 'unknown')

    with pytest.raises(AbortContext) as exc_info:
        servicer.temp_dir('unknown', context)
    assert context.code == grpc.StatusCode.NOT_FOUND

    # this is how it looks with a missing repository argument in the
    # gRPC request, and temp_dir(request.repository.storage_name)
    with pytest.raises(AbortContext) as exc_info:
        servicer.temp_dir('', context)
    assert context.code == grpc.StatusCode.INVALID_ARGUMENT


def test_temp_dir_failed_creation(tmpdir):
    # context is used for error raising only
    context = FakeContext()
    broken = tmpdir / 'broken'
    broken.mksymlinkto('broken')  # itself

    servicer = HGitalyServicer(dict(broken=as_bytes(broken)))

    with pytest.raises(AbortContext):
        servicer.temp_dir('broken', context, ensure=True)
    assert context.code == grpc.StatusCode.INTERNAL


def test_working_dir(tmpdir):
    context = FakeContext()
    servicer = HGitalyServicer(dict(default=as_bytes(tmpdir)))

    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))
    # context is used for error raising only
    context = FakeContext()

    wrapper = LocalRepoWrapper.init(storage_root.join('awesome-proj.hg'))
    gl_repo = Repository(storage_name='storname',
                         relative_path='awesome-proj.hg')
    repo = servicer.load_repo(gl_repo, context)

    with servicer.working_dir(gl_repo, repo, context) as wd:
        wd_path = wd.path
        wd_wrapper = LocalRepoWrapper.load(wd_path)
        sha = wd_wrapper.commit_file('foo').hex()

    wrapper.reload()
    ctx = wrapper.repo[sha]
    assert ctx.hex() == sha

    with servicer.working_dir(gl_repo, repo, context, changeset=ctx) as wd:
        assert wd.path == wd_path
        wd_wrapper.reload()
        sha2 = wd_wrapper.commit_file('nar').hex()

    wrapper.reload()
    ctx2 = wrapper.repo[sha2]
    assert ctx2.hex() == sha2


def test_repo_command(tmpdir):
    storage_root = tmpdir.join('repos')
    storage_root_bytes = pycompat.sysbytes(str(storage_root))
    servicer = HGitalyServicer(dict(storname=storage_root_bytes))
    wrapper = LocalRepoWrapper.init(storage_root.join('awesome-proj.hg'))
    ctx = wrapper.commit_file('foo')

    repo = wrapper.repo
    context = FakeContext()

    servicer.repo_command(repo, context, 'amend', message=b"amended")
    ctx = wrapper.repo.unfiltered()[ctx.rev()]
    amended = obsutil.latest_unique_successor(ctx)
    assert amended.description() == b'amended'
