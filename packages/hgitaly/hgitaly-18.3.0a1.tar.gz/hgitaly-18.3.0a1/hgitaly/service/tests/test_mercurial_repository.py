# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
from importlib import reload
import os
import pytest

from mercurial import (
    phases,
    sshpeer,
)
from hgext3rd.heptapod.branch import (
    write_gitlab_branches,
)


from hgitaly.testing.ssh import hg_exe_path
from hgitaly.testing.sshd import hg_ssh_setup
from hgitaly.tests.common import make_empty_repo

from hgitaly.stub.mercurial_repository_pb2 import (
    ConfigItemType,
    GetConfigItemRequest,
    GetManagedConfigRequest,
    HousekeepingRequest,
    SetManagedConfigRequest,
    HeptapodConfigSection,
    MercurialPeer,
    PushRequest,
)
from hgitaly.stub.mercurial_repository_pb2_grpc import (
    MercurialRepositoryServiceStub,
)

from .fixture import ServiceFixture

AutoPublish = HeptapodConfigSection.AutoPublish
CloneBundles = HeptapodConfigSection.CloneBundles

parametrize = pytest.mark.parametrize


class ConfigFixture(ServiceFixture):
    stub_cls = MercurialRepositoryServiceStub

    def config_item(self, **kw):
        return self.stub.GetConfigItem(
            GetConfigItemRequest(repository=self.grpc_repo, **kw))

    def config_bool(self, section, name):
        return self.config_item(as_type=ConfigItemType.BOOL,
                                section=section,
                                name=name,
                                ).as_bool

    def get_managed_config(self, **kw):
        return self.stub.GetManagedConfig(
            GetManagedConfigRequest(repository=self.grpc_repo, **kw))

    def set_managed_config(self, **kw):
        return self.stub.SetManagedConfig(
            SetManagedConfigRequest(repository=self.grpc_repo, **kw))

    def hgrc_path(self, main=False):
        hgrc_name = 'hgrc' if main else 'hgrc.managed'
        return self.repo_wrapper.path / '.hg' / hgrc_name

    def write_hgrc(self, *lines, main=False):
        self.hgrc_path().write_text('\n'.join((lines)))

    def append_main_hgrc(self, *lines):
        with open(self.hgrc_path(main=True), 'a') as hgrcf:
            hgrcf.write('\n'.join(lines))

    def write_main_hgrc(self, *lines, include_managed=True):
        with open(self.hgrc_path(main=True), 'w') as hgrcf:
            hgrcf.write('\n'.join(lines))
        if include_managed:
            self.include_managed_hgrc()

    def read_main_hgrc_lines(self):
        return self.hgrc_path(main=True).read_text().splitlines()

    def include_managed_hgrc(self):
        self.append_main_hgrc('', '%include hgrc.managed', '')

    def housekeeping(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        return self.stub.Housekeeping(HousekeepingRequest(**kw))


@pytest.fixture
def config_fixture(grpc_channel, server_repos_root):
    with ConfigFixture(grpc_channel, server_repos_root) as fixture:
        # this is normally done upon repository creation:
        fixture.include_managed_hgrc()
        setattr(fixture.grpc_repo, 'gl_project_path', 'mygroup/myproject')

        yield fixture


def test_config_item(config_fixture):
    rpc_config_bool = config_fixture.config_bool

    # Relying on current defaults in some random core settings, just pick
    # some other ones if they change.
    assert rpc_config_bool('format', 'usestore') is True
    assert rpc_config_bool('commands', 'status.verbose') is False


def test_get_managed_config(config_fixture):
    get_config = config_fixture.get_managed_config

    # first, default values
    config = get_config()
    # in these tests, the main hgrc is not initialized with the default
    # group inheritance.
    assert config.inherit is False

    section = config.heptapod
    assert section.auto_publish == AutoPublish.WITHOUT_TOPIC

    config_fixture.write_hgrc('[heptapod]',
                              'auto-publish = nothing',
                              'allow-bookmarks = yes',
                              '')
    section = get_config().heptapod
    assert section.auto_publish == AutoPublish.NOTHING
    assert section.allow_bookmarks is True

    config_fixture.append_main_hgrc('\n%include ../../../../../mygroup/hgrc\n')
    assert get_config().inherit is True


def test_get_managed_config_local(config_fixture):
    get_config = config_fixture.get_managed_config
    # Instead of inheriting from group (which Heptapod generally would do),
    # in this test, we set a direct value in the main HGRC file.
    # With 'local=True`, it should not be returned by the RPC either.

    config_fixture.append_main_hgrc('', '[heptapod]', 'auto-publish=all', '')

    config_fixture.write_hgrc('[heptapod]',
                              'allow-multiple-heads = yes',
                              '')
    section = get_config(local=True).heptapod
    # local call does not see the value from main HGRC, hence the default
    # value of the protocol is to be seen
    assert section.auto_publish == AutoPublish.WITHOUT_TOPIC
    # but parameters not present in the managed file are simply not set
    # (field is optional in protocol)
    assert not section.HasField('auto_publish')
    assert not section.HasField('allow_bookmarks')

    # and that is not because it is totally blind:
    assert section.allow_multiple_heads is True

    # double check
    assert get_config(local=False).heptapod.auto_publish == AutoPublish.ALL


def test_set_managed_config(config_fixture):
    get_config = config_fixture.get_managed_config
    set_config = config_fixture.set_managed_config

    config_fixture.write_main_hgrc('[heptapod]',
                                   'allow-multiple-heads = yes',
                                   '')
    set_config(
        heptapod=HeptapodConfigSection(allow_bookmarks=True,
                                       auto_publish=AutoPublish.NOTHING,
                                       ),
        by_line="by user foo"
    )
    section = get_config(local=True).heptapod
    assert not section.HasField('allow_multiple_heads')
    assert section.HasField('allow_bookmarks')
    assert section.allow_bookmarks
    assert section.HasField('auto_publish')
    assert section.auto_publish == AutoPublish.NOTHING
    assert get_config().heptapod.allow_multiple_heads is True  # control

    set_config(
        heptapod=HeptapodConfigSection(clone_bundles=CloneBundles.EXPLICIT),
        by_line="by user interested in bundles"
    )
    section = get_config(local=True).heptapod
    assert not section.HasField('allow_multiple_heads')
    assert section.HasField('clone_bundles')
    assert section.clone_bundles == CloneBundles.EXPLICIT

    # to check whether the managed file actually overrides a setting
    # and even if inclusion is missing
    config_fixture.write_main_hgrc('[heptapod]', 'allow-bookmarks = yes', '',
                                   include_managed=False)

    set_config(heptapod=HeptapodConfigSection(allow_bookmarks=False))
    section = get_config(local=True).heptapod
    assert not section.HasField('allow_multiple_heads')
    assert section.HasField('allow_bookmarks')
    assert not section.allow_bookmarks
    # field not mentioned in call is not affected
    assert section.HasField('auto_publish')
    assert section.auto_publish == AutoPublish.NOTHING
    # proof of override
    assert not get_config().heptapod.allow_bookmarks

    set_config(heptapod=HeptapodConfigSection(),
               remove_items=['allow_bookmarks'])
    section = get_config(local=True).heptapod
    assert not section.HasField('allow_multiple_heads')
    assert not section.HasField('allow_bookmarks')
    assert not section.allow_multiple_heads
    assert not section.allow_bookmarks
    # proof that override has been removed
    assert get_config().heptapod.allow_bookmarks

    # removing everything and testing by_line
    set_config(remove_items=('allow_bookmarks', 'auto_publish',
                             'clone_bundles'),
               by_line='by erasor')
    managed_lines = config_fixture.hgrc_path().read_text().splitlines()
    assert not managed_lines[0].startswith('[')
    assert managed_lines[1:] == ['# latest update by erasor', '']


def test_set_managed_config_inherit(config_fixture):
    get_config = config_fixture.get_managed_config
    set_config = config_fixture.set_managed_config
    config_fixture.write_main_hgrc("# An unrelated line",
                                   "%include some/path/hgrc",
                                   "# Another unrelated line",
                                   '')
    assert get_config().inherit is True

    set_config(inherit=False, by_line="by user foo1")
    assert get_config().inherit is False
    hgrc_lines = config_fixture.read_main_hgrc_lines()
    assert hgrc_lines[:3] == ["# An unrelated line",
                              "# inheritance removed by user foo1",
                              "# Another unrelated line",
                              ]
    set_config(inherit=True, by_line="by user foo2")
    assert get_config().inherit is True
    hgrc_lines = config_fixture.read_main_hgrc_lines()
    assert hgrc_lines[:5] == ["# inheritance restored by user foo2",
                              "%include ../../mygroup/hgrc",
                              "# An unrelated line",
                              "# inheritance removed by user foo1",
                              "# Another unrelated line",
                              ]

    # in case of no-op, nothing is changed (even by-line)
    set_config(inherit=True, by_line="by user foo3")
    assert get_config().inherit is True
    hgrc_lines = config_fixture.read_main_hgrc_lines()
    assert hgrc_lines[:2] == ["# inheritance restored by user foo2",
                              "%include ../../mygroup/hgrc",
                              ]


@pytest.fixture
def push_fixture(grpc_channel, server_repos_root):
    hg_repo_stub = MercurialRepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    target_wrapper, _target_grpc_repo = make_empty_repo(server_repos_root)

    # make sure that the sshpeer.sshv1peer class inherits from the
    # `wirepeer` patched as `tnspeer` by `hgext3rd.topic.server`
    reload(sshpeer)

    def push(remote_url=target_wrapper.path, peer_opts=None, **kw):
        if peer_opts is None:
            peer_opts = {}
        return hg_repo_stub.Push(PushRequest(
            repository=grpc_repo,
            remote_peer=MercurialPeer(url=str(remote_url), **peer_opts),
            **kw))
    yield wrapper, target_wrapper, push


def auto_publish_config(publish):
    """Return a config dict with phases.publish set."""
    return dict(phases=dict(publish='yes' if publish else 'no'))


def set_auto_publishing(repo_wrapper, publish):
    """Tweak persistently the auto-publishing behaviour of the repository

    In a typical push, the repository configuration will be initialized
    independently from the objects of these tests, so this has to be done
    in the `hgrc` file.

    TODO consider for inclusion in mercurial-testhelpers.
    """
    repo_wrapper.write_hgrc(auto_publish_config(publish))


def test_bare_push(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    def get_nodes_ids(repo):
        return {repo[r].hex() for r in repo.revs("all()")}

    ctx_pub = wrapper.commit_file('foo')
    wrapper.set_phase("public", [ctx_pub.hex()])
    ctx_draft = wrapper.commit_file('foo')

    # pushing public changesets only
    res = push()
    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_nodes_ids(target_wrapper.repo)
    assert target_node_ids == {ctx_pub.hex()}

    # idempotency
    res = push()
    assert not res.new_changesets

    # pushing drafts explicitely
    # this needs us to make the target repo non-publishing
    set_auto_publishing(target_wrapper, False)
    res = push(include_drafts=True)
    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_nodes_ids(target_wrapper.repo)
    assert target_node_ids == {ctx_pub.hex(), ctx_draft.hex()}

    # idempotency for drafts
    res = push(include_drafts=True)
    assert not res.new_changesets

    # case of target not existing
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=target_wrapper.path / 'does/not/exist')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "could not be used as a peer" in exc_info.value.details()

    # case of push failing on target (other ways to make it fail would
    # be of course admissible)
    (target_wrapper.path / '.hg' / 'hgrc').write_text(
        "[experimental]\n"
        "single-head-per-branch=yes\n")
    wrapper.write_commit('bar', parent=ctx_pub)
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=target_wrapper.path, include_drafts=True)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL


def test_push_branch(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    def get_node_ids(wrapper, revset="all()"):
        repo = wrapper.repo
        return {repo[r].hex() for r in repo.revs(revset)}

    ctx_foo = wrapper.commit_file('foo')
    wrapper.commit_file('baz')
    wrapper.update(0)
    ctx_bar = wrapper.commit_file('bar', branch="stable")
    wrapper.set_phase("public", [ctx_bar.hex()])
    expected_node_ids = {ctx_foo.hex(), ctx_bar.hex()}
    res = push(only_gitlab_branches_matching=[b'branch/stable'])

    assert res.new_changesets
    target_wrapper.reload()
    target_node_ids = get_node_ids(target_wrapper)
    assert target_node_ids == expected_node_ids

    # a head draft is not pushed, but its public ancestors are
    # (also using a wildcard pattern)
    ctx_bar2 = wrapper.commit_file('bar', branch='stable')
    ctx_bar3 = wrapper.commit_file('bar', branch='stable')
    wrapper.set_phase('public', [ctx_bar2.hex()])
    res = push(only_gitlab_branches_matching=[b'branch/st*'])
    assert res.new_changesets
    target_wrapper.reload()
    assert get_node_ids(target_wrapper, revset="stable") == {ctx_bar2.hex()}

    # pushing drafts explicitely
    # auto-publication is prohibited for now
    set_auto_publishing(target_wrapper, False)
    res = push(only_gitlab_branches_matching=[b'branch/stable'],
               include_drafts=True)
    assert res.new_changesets
    target_wrapper.reload()
    assert get_node_ids(target_wrapper, revset="stable") == {ctx_bar3.hex()}

    # pushing a branch that doesn't exist currently is not an error
    # (it can happen temporarily and still be the intent in repeated
    # invocations, such as mirrorring, the primary use-case)
    assert not push(only_gitlab_branches_matching=[b'z*']).new_changesets


@pytest.fixture
def ssh_fixture(tmpdir):
    working_dir = tmpdir / 'sshd'
    working_dir.mkdir()
    yield from hg_ssh_setup(working_dir)


def test_push_ssh(push_fixture, ssh_fixture):
    wrapper, target_wrapper, push = push_fixture
    server, client_key, known_hosts = ssh_fixture

    ctx = wrapper.commit_file('foo')

    # auto-publication is prohibited for now
    set_auto_publishing(target_wrapper, False)
    res = push(
        include_drafts=True,
        remote_url=f'ssh://{server.host}:{server.port}/{target_wrapper.path}',
        peer_opts=dict(
            ssh_remote_command=os.fsencode(hg_exe_path()),
            ssh_key=client_key,
            ssh_known_hosts=known_hosts,
        ))

    assert res.new_changesets

    target_wrapper.reload()
    assert ctx in target_wrapper.repo


@parametrize('order', ['hg-evolve-first', 'hg-evolve-second'])
def test_push_ssh_different_capabilities(order,
                                         server_repos_root,
                                         push_fixture,
                                         ssh_fixture):
    wrapper, target_wrapper, push = push_fixture
    server, client_key, known_hosts = ssh_fixture

    target2_wrapper, _ = make_empty_repo(server_repos_root)

    wrapper.commit_file('foo')
    topical = wrapper.commit_file('top', topic='feature')
    peer_opts = dict(
        ssh_remote_command=os.fsencode(hg_exe_path()),
        ssh_key=client_key,
        ssh_known_hosts=known_hosts,
    )

    # configuration for first target, with evolve/topic
    target_conf = auto_publish_config(False)
    target_conf['extensions'] = dict(topic='', evolve='')
    target_wrapper.write_hgrc(target_conf)

    # configuration for second target, without evolve/topic
    target2_conf = auto_publish_config(False)
    target2_conf['extensions'] = dict(topic='!', evolve='!')
    target2_wrapper.write_hgrc(target2_conf)

    ssh_base_url = f'ssh://{server.host}:{server.port}/'
    target_paths = [target_wrapper.path, target2_wrapper.path]
    if order == 'hg-evolve-second':
        target_paths.reverse()

    # if the topic extension calls `tns_heads()` method on a remote that does
    # not have the capability, we get a hard error.
    # As of this writing, the topic extension adds the `tns_heads()`
    # method inconditionally on `mercurial.sshpeer.sshv1peer`
    # but actual call of `tns_heads()` depends on current peer capability, as
    # it should.
    # Sabotaging that latter part (currently `topicpeerexecutor` class, defined
    # in `hgext3rd.topic.server`) breaks this test.
    results = [push(include_drafts=True,
                    remote_url=f'{ssh_base_url}/{tgt_path}',
                    peer_opts=peer_opts)
               for tgt_path in target_paths]

    assert all(res.new_changesets for res in results)

    for tgt_wrapper in (target_wrapper, target2_wrapper):
        tgt_wrapper.reload()
        assert topical in tgt_wrapper.repo


def test_push_auto_publishing_error(push_fixture):
    wrapper, target_wrapper, push = push_fixture

    ctx = wrapper.commit_file('foo')
    assert ctx.phase() == phases.draft  # making sure of main hypothesis

    set_auto_publishing(target_wrapper, True)

    with pytest.raises(grpc.RpcError) as exc_info:
        push(include_drafts=True)
    # debatable, but we currently don't have a clear way to tell the
    # inner exception apart
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'push would publish' in exc_info.value.details()


def test_push_unexpected_error(push_fixture):
    wrapper, target_wrapper, push = push_fixture
    wrapper.commit_file('foo')

    # we don't have many ways to trigger internal errors when
    # monkeypatch can't work (server is not in the same process):
    # let's corrupt the repo.

    write_gitlab_branches(wrapper.repo, {b'wrecked': b'not-a-hash'})

    with pytest.raises(grpc.RpcError) as exc_info:
        push(only_gitlab_branches_matching=[b'wrecked'])

    # debatable, but we currently don't have a clear way to tell the
    # inner exception apart
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    details = exc_info.value.details()
    assert "Unexpected" in details
    assert 'not-a-hash' in details


@parametrize('url', (
    'http://.heptapod.test/a/repo',  # hg.peer() fails at IDNA decoding
    'http://\u2100.test',  # refused for NKFC normalisation by urlparse()
    'mailto:pushoversmtpisajoke@heptapod.test',  # wrong scheme
    '/tmp/not_in_storage',
))
def test_push_invalid_url(push_fixture, url):
    _wrapper, _target_wrapper, push = push_fixture
    with pytest.raises(grpc.RpcError) as exc_info:
        push(remote_url=url)
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_housekeeping(config_fixture):
    fixture = config_fixture

    fixture.housekeeping(fail=True)

    assert fixture.housekeeping(
        working_directories_age_threshold_seconds=1).working_directories_gc

    fixture.housekeeping(working_directories_remove_unlisted=True)

    resp = fixture.housekeeping(recover=True)
    assert resp.recover_run
    assert not resp.recovered_interrupted_transaction
