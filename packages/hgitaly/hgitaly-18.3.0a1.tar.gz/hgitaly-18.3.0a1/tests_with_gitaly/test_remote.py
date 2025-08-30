import subprocess

from heptapod.testhelpers.git import GitRepo

from hgitaly.stub.remote_pb2 import (
    FindRemoteRepositoryRequest,
    UpdateRemoteMirrorRequest,
)
from hgitaly.stub.remote_pb2_grpc import RemoteServiceStub
from hgitaly.testing.ssh import hg_exe_path
from hgitaly.testing.sshd import hg_ssh_setup

import pytest
from . import skip_comparison_tests


if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip
Remote = UpdateRemoteMirrorRequest.Remote


@pytest.fixture
def ssh_fixture(tmpdir):
    working_dir = tmpdir / 'sshd'
    working_dir.mkdir()

    yield from hg_ssh_setup(working_dir)


@pytest.fixture()
def push_mirror_fixture(gitaly_rhgitaly_comparison_native,
                        ssh_fixture,
                        tmpdir):
    """Testing with resolved_address on the HGitaly side

    We're using SSH on the HGitaly side, as it is the most practical to setup
    in these tests.

    Surprisingly, it does not work with Gitaly, as it refuses our `known_hosts`
    and complains about lack of ED25519 server key (even if providing one).
    The general Heptapod tests demonstrate however that it can work (could
    be a matter of accepting the loopback address).

    Testing other protocols would be the job of Heptapod Tests (end-to-end).
    In these tests, we are more interested in options such as branch matching.
    """
    ssh_server, ssh_key, known_hosts = ssh_fixture
    ssh_base_url = f'ssh://localhost:{ssh_server.port}'
    comp = gitaly_rhgitaly_comparison_native
    target = tmpdir / 'target'
    comp.tgt_repo_gitaly = GitRepo.init(target / 'by_gitaly')
    comp.tgt_repo_hgitaly = GitRepo.init(target / 'by_hgitaly')

    rpc_helper = comp.rpc_helper(
        stub_cls=RemoteServiceStub,
        hg_server='rhgitaly',
        request_cls=UpdateRemoteMirrorRequest,
        method_name="UpdateRemoteMirror",
        streaming_request_field='only_branches_matching',
    )

    def assert_compare_target_repos(**kwargs):
        tgt_url_gitaly = str(comp.tgt_repo_gitaly.path)
        tgt_url_hgitaly = ssh_base_url + str(comp.tgt_repo_hgitaly.path)

        resolved_address = kwargs.get('resolved_address', '127.0.0.1')

        kwargs.setdefault('ssh_key', ssh_key)
        kwargs.setdefault('known_hosts', known_hosts)

        resp_gitaly = rpc_helper.rpc('git',
                                     remote=Remote(
                                         url=tgt_url_gitaly,
                                     ),
                                     **kwargs)

        resp_hgitaly = rpc_helper.rpc('hg',
                                      remote=Remote(
                                          url=tgt_url_hgitaly,
                                          resolved_address=resolved_address,
                                      ),
                                      repository=comp.hgitaly_repo,
                                      **kwargs)
        assert resp_gitaly == resp_hgitaly
        assert comp.tgt_repo_gitaly == comp.tgt_repo_hgitaly

    rpc_helper.assert_compare_target_repos = assert_compare_target_repos

    yield comp, rpc_helper


def test_update_remote_mirror_minimal(push_mirror_fixture, tmpdir):
    fixture, rpc_helper = push_mirror_fixture
    wrapper = fixture.hg_repo_wrapper
    src_git_repo = fixture.git_repo
    wrapper.write_commit('foo', message="Some foo")
    wrapper.command('hpd-export-native-to-git')
    # export worked
    assert set(src_git_repo.branches()) == {b'branch/default'}

    rpc_helper.assert_compare_target_repos()


def test_update_remote_mirror_branch_matching(push_mirror_fixture, tmpdir):
    fixture, rpc_helper = push_mirror_fixture
    wrapper = fixture.hg_repo_wrapper
    src_git_repo = fixture.git_repo
    ctx0 = wrapper.write_commit('foo', message="Some foo")
    # tags are always pushed
    wrapper.command('tag', b'start-tag', rev=ctx0.hex())
    wrapper.commit_file('foo', topic='sampletop')
    wrapper.command('hpd-export-native-to-git')
    # export worked
    assert set(src_git_repo.branches()) == {b'branch/default',
                                            b'topic/default/sampletop'}

    rpc_helper.assert_compare_target_repos(
        only_branches_matching=[b'branch/*']
    )

    # add the topic
    rpc_helper.assert_compare_target_repos(
        only_branches_matching=[b'topic/*/sampletop']
    )

    # remove the Git branch for the topic by publishing it and sync everything
    wrapper.set_phase('public', ['sampletop'])
    wrapper.command('hpd-export-native-to-git')
    rpc_helper.assert_compare_target_repos()


def test_find_remote_repository(gitaly_rhgitaly_comparison):
    fixture = gitaly_rhgitaly_comparison
    wrapper = fixture.hg_repo_wrapper
    rpc_helper = fixture.rpc_helper(
        stub_cls=RemoteServiceStub,
        repository_arg=False,
        hg_server='rhgitaly',
        request_cls=FindRemoteRepositoryRequest,
        method_name="FindRemoteRepository",
    )

    def remote_exists(url):
        return rpc_helper.rpc('hg', remote=url)

    rpc_helper.assert_compare(remote='http://unknown.test')

    hg_server = subprocess.Popen((hg_exe_path(), 'serve', '-p', '0'),
                                 cwd=wrapper.path,
                                 stdout=subprocess.PIPE)
    try:
        startup_line = hg_server.stdout.readline()
        for token in startup_line.split():
            if token.startswith(b'http://'):
                repo_url = token.decode('utf-8')
                assert remote_exists(repo_url)
                break
        else:  # pragma no cover
            raise RuntimeError("Could not parse URL from hg serve line")
    finally:
        hg_server.kill()
        hg_server.wait()
