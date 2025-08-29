# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from datetime import (
    datetime,
    timedelta,
    timezone,
)
import grpc
import pytest
from mercurial import (
    pycompat,
    scmutil,
)
import time

from hgext3rd.heptapod.branch import (
    set_default_gitlab_branch,
)
from hgext3rd.heptapod.special_ref import (
    special_refs,
    write_gitlab_special_ref,
)
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)
from hgitaly import feature
from hgitaly.errors import parse_assert_structured_error
from hgitaly.revision import (
    ZERO_SHA,
    ZERO_SHA_STR,
)
from hgitaly.tests.common import (
    make_empty_repo,
    make_tree_shaped_repo,
)

from hgitaly.stub.shared_pb2 import (
    PaginationParameter,
    SortDirection,
)
from hgitaly.stub.ref_pb2 import (
    FindAllTagsRequest,
    RefExistsRequest,
    FindBranchRequest,
    FindLocalBranchesRequest,
    FindAllRemoteBranchesRequest,
    FindAllBranchesRequest,
    DeleteRefsRequest,
    ListBranchNamesContainingCommitRequest,
    ListRefsRequest,
    ListTagNamesContainingCommitRequest,
    GetTagMessagesRequest,
    FindRefsByOIDRequest,
    FindTagError,
    FindTagRequest,
    UpdateReferencesRequest,
)
from hgitaly.stub.ref_pb2_grpc import RefServiceStub

from .fixture import ServiceFixture


class RefFixture(ServiceFixture):

    stub_cls = RefServiceStub

    feature_flags = None

    def commit_file(self, *args, **kwargs):
        return self.repo_wrapper.commit_file(*args, **kwargs)

    def find_tag(self, **kw):
        return self.rpc('FindTag',
                        FindTagRequest(repository=self.grpc_repo, **kw))

    def find_all_tags(self, **kw):
        return self.stub.FindAllTags(
            FindAllTagsRequest(repository=self.grpc_repo, **kw))

    def find_local_branches(self, **kw):
        return self.stub.FindLocalBranches(
            FindLocalBranchesRequest(repository=self.grpc_repo, **kw),
            metadata=feature.as_grpc_metadata(self.feature_flags),
        )

    def ref_exists(self, ref, **kw):
        kw.setdefault('repository', self.grpc_repo)
        return self.stub.RefExists(RefExistsRequest(ref=ref, **kw)).value

    def list_refs(self, patterns=(b"refs/", ), **kw):
        return [(ref.name, ref.target)
                for resp in self.stub.ListRefs(
                        ListRefsRequest(repository=self.grpc_repo,
                                        patterns=patterns,
                                        **kw))
                for ref in resp.references]

    def find_refs_by_oid(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        return self.stub.FindRefsByOID(FindRefsByOIDRequest(**kw)).refs

    def update_refs(self, updates, **kw):
        Update = UpdateReferencesRequest.Update
        kw.setdefault('repository', self.grpc_repo)

        update_messages = []
        for ref_path, old_id, new_id in updates:
            upd_kw = dict(reference=ref_path, new_object_id=new_id)
            if old_id is not None:
                upd_kw['old_object_id'] = old_id
            update_messages.append(Update(**upd_kw))

        return self.stub.UpdateReferences(
            iter([UpdateReferencesRequest(updates=[upd], **kw)
                  for upd in update_messages])
        )


@pytest.fixture
def ref_fixture(grpc_channel, server_repos_root):
    with RefFixture(grpc_channel, server_repos_root) as fixture:
        yield fixture


def test_tags(ref_fixture):
    wrapper = ref_fixture.repo_wrapper

    ctx = ref_fixture.commit_file('foo', message="The tagged chgs")
    wrapper.command('tag', b'v3.2.1', rev=ctx.hex())

    assert [n for n, _ in ref_fixture.list_refs(patterns=[b'refs/tags/'])
            ] == [b'refs/tags/v3.2.1']

    tag = ref_fixture.find_tag(tag_name=b'v3.2.1').tag
    assert tag.name == b'v3.2.1'
    target = tag.target_commit
    assert target.subject == b"The tagged chgs"

    assert [list(chunk.tags)
            for chunk in ref_fixture.find_all_tags()
            ] == [[tag]]

    # finally, structured error for a non existing tag
    with pytest.raises(grpc.RpcError) as exc_info:
        ref_fixture.find_tag(tag_name=b'does-not-exist')
    _details, error = parse_assert_structured_error(
        exc_info.value, FindTagError, grpc.StatusCode.NOT_FOUND)
    assert error.tag_not_found.reference_name == b'refs/tags/does-not-exist'


def test_find_branch(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    ctx = wrapper.write_commit('foo', message="Ze subject")
    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'branch/default'))
    branch = resp.branch
    assert branch is not None
    assert branch.name == b'branch/default'
    assert branch.target_commit.id == ctx.hex().decode()

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'refs/heads/branch/default'))
    assert resp.branch == branch

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'cannot-be-found'))
    assert not resp.branch.name

    resp = ref_stub.FindBranch(
        FindBranchRequest(repository=grpc_repo,
                          name=b'refs/keeparound/012ca34fe56'))

    # There is no None in gRPC, just cascading default content (empty string).
    # We checked that Gitaly indeed uses the default `Branch(name=b'')`
    # to represent the absence of results.
    assert not resp.branch.name

    resp = ref_stub.FindAllBranches(
        FindAllBranchesRequest(repository=grpc_repo))
    branches = [br for chunk in resp for br in chunk.branches]
    assert len(branches) == 1
    assert branches[0].name == b'refs/heads/branch/default'
    assert branches[0].target == branch.target_commit

    resp = list(ref_stub.FindAllRemoteBranches(
        FindAllRemoteBranchesRequest(repository=grpc_repo)))
    assert not resp


def test_find_local_branches(ref_fixture):
    ctx = ref_fixture.commit_file('foo', message="Ze subject")

    ref_fixture.feature_flags = [
        ('simplify-find-local-branches-response', True),
    ]
    resp = ref_fixture.find_local_branches(
                pagination_params=PaginationParameter(limit=-1))
    branches = [br for chunk in resp for br in chunk.local_branches]
    assert len(branches) == 1
    assert branches[0].name == b'refs/heads/branch/default'
    target = branches[0].target_commit
    assert target.id == ctx.hex().decode()
    assert target.subject == b"Ze subject"


def test_find_local_branches_pagination(ref_fixture):
    # pagination doesn't preclude chunking inside each page
    for i in range(22):
        ref_fixture.commit_file('foo', branch='br%02d' % i, return_ctx=False)

    # limit=0 doesn't mean unlimited
    resp = list(ref_fixture.find_local_branches(
        pagination_params=PaginationParameter(limit=0)))
    assert len(resp) == 0

    # but no pagination_params does mean unlimited
    assert sum(len(resp.local_branches)
               for resp in ref_fixture.find_local_branches()) == 22

    resp = list(ref_fixture.find_local_branches(
        pagination_params=PaginationParameter(limit=21)))
    assert len(resp[0].local_branches) == 20
    # cursor aka page token is (not yet) returned
    assert [br.name for br in resp[1].local_branches] == [
        b'refs/heads/branch/br20']

    # but we can infer it
    resp = list(ref_fixture.find_local_branches(
        pagination_params=PaginationParameter(
            limit=6,
            page_token='refs/heads/branch/br20')))
    assert len(resp) == 1
    assert [br.name for br in resp[0].local_branches] == [
        b'refs/heads/branch/br21']


def test_find_local_branches_sort_by(ref_fixture):
    utc2 = timezone(timedelta(hours=2))

    ref_fixture.commit_file('foo', branch='aaa',
                            tz_datetime=(datetime(2021, 3, 1, 5, 57, 0,
                                                  tzinfo=utc2)  # 03:57 UTC
                                         ))
    ref_fixture.commit_file('foo', branch='bbb',
                            utc_datetime=(datetime(2021, 3, 1, 4, 0, 0)))
    ref_fixture.commit_file('foo', branch='ccc',
                            utc_datetime=(datetime(2021, 3, 1, 3, 0, 0)))

    SortBy = FindLocalBranchesRequest.SortBy
    pagination_params = PaginationParameter(limit=-1)

    def assert_branches_sorted_by(by, expected):
        assert [br.name
                for resp in ref_fixture.find_local_branches(
                        sort_by=by,
                        pagination_params=pagination_params
                )
                for br in resp.local_branches
                ] == [b'refs/heads/branch/' + ex for ex in expected]

    assert_branches_sorted_by(SortBy.NAME, [b'aaa', b'bbb', b'ccc'])
    assert_branches_sorted_by(SortBy.UPDATED_ASC, [b'ccc', b'aaa', b'bbb'])
    assert_branches_sorted_by(SortBy.UPDATED_DESC, [b'bbb', b'aaa', b'ccc'])


def test_ref_exists(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def ref_exists(ref):
        return ref_stub.RefExists(RefExistsRequest(repository=grpc_repo,
                                                   ref=ref)).value

    with pytest.raises(grpc.RpcError) as exc_info:
        ref_exists(b'not-a-ref-path')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    ctx = wrapper.write_commit('foo', message="Ze Foo")
    assert ref_exists(b'refs/heads/branch/default')
    assert not ref_exists(b'refs/heads/branch/other')
    assert not ref_exists(b'refs/heads/topic/default/zetop')
    assert not ref_exists(b'refs/tags/v3.2.1')

    wrapper.write_commit('zetop', topic='zetop')
    assert ref_exists(b'refs/heads/topic/default/zetop')

    wrapper.command('tag', b'v3.2.1', rev=ctx.hex())
    assert ref_exists(b'refs/tags/v3.2.1')
    assert not ref_exists(b'refs/tags/tip')

    # although we could resolve the hexadecimal node id from any
    # "wild" branch ref, it is just wrong to pretend it exists.
    assert not ref_exists(b'refs/heads/wild/' + ctx.hex())

    sref_name = b'pipelines/765'
    sref_path = b'refs/' + sref_name
    assert not ref_exists(sref_path)
    write_gitlab_special_ref(wrapper.repo, sref_name, ctx.hex())
    assert ref_exists(sref_path)

    keep_around = b'refs/keep-around/' + ctx.hex()
    assert not ref_exists(keep_around)
    create_keep_around(wrapper.repo, ctx.hex())
    assert ref_exists(keep_around)

    assert not ref_exists(b'refs/unknown/type/of/ref')


def test_delete_refs(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    repo = wrapper.repo

    def do_rpc(refs=(), except_prefixes=()):
        return ref_stub.DeleteRefs(
            DeleteRefsRequest(repository=grpc_repo,
                              refs=refs,
                              except_with_prefix=except_prefixes))

    def assert_special_refs(expected):
        # it is normal for the client-side repo to need invalidation
        wrapper.reload()
        assert special_refs(wrapper.repo) == expected

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(refs=[b'xy'], except_prefixes=[b'refs/heads'])
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    ctx = wrapper.write_commit('foo')
    wrapper.command('tag', b'v1.2.3')

    # Deleting a branch or a tag is forbidden
    for ref in (b'branch/default',
                b'refs/heads/branch/default',
                b'refs/tags/v1.2.3'):
        assert do_rpc([ref]).git_error

    special_ref_name = b'pipelines/256'
    special_ref_path = b'refs/' + special_ref_name

    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    # double check
    assert_special_refs({special_ref_name: ctx.hex()})

    # go
    assert not do_rpc([special_ref_path]).git_error
    assert_special_refs({})

    # case where one mixes unknown and known refs
    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    # double check
    assert_special_refs({special_ref_name: ctx.hex()})
    mixed_refs = [special_ref_path, b'refs/merge-requests/12/head']
    assert not do_rpc(mixed_refs).git_error
    assert_special_refs({})

    other_special_ref_name = b'environments/124'
    for prefix in (b'refs/environments',
                   b'refs/environ',
                   b'refs/environments/'):
        write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
        write_gitlab_special_ref(repo, other_special_ref_name, ctx.hex())
        # double check
        assert_special_refs({special_ref_name: ctx.hex(),
                             other_special_ref_name: ctx.hex()})

        assert not do_rpc(except_prefixes=[prefix]).git_error
        assert_special_refs({other_special_ref_name: ctx.hex()})

    # exclusion matching both special refs
    write_gitlab_special_ref(repo, special_ref_name, ctx.hex())
    write_gitlab_special_ref(repo, other_special_ref_name, ctx.hex())
    assert not do_rpc(except_prefixes=[b'refs/environ',
                                       b'refs/pipel']).git_error
    assert_special_refs({special_ref_name: ctx.hex(),
                         other_special_ref_name: ctx.hex()})


def test_list_branch_names_containing_commit(grpc_channel, server_repos_root):
    """Test ListBranchNamesContainingCommit on a repo a bit more spread
    """
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo, changesets = make_tree_shaped_repo(server_repos_root)

    def do_list(ctx, limit=0):
        chunks_iter = ref_stub.ListBranchNamesContainingCommit(
            ListBranchNamesContainingCommitRequest(
                repository=grpc_repo,
                commit_id=pycompat.sysstr(ctx.hex()),
                limit=limit,
            ))
        return [pycompat.sysstr(gl_branch) for chunk in chunks_iter
                for gl_branch in chunk.branch_names]

    wild1, wild2 = changesets['wild1'], changesets['wild2']
    top1, top2 = changesets['top1'], changesets['top2']

    wild_branch1 = 'wild/' + pycompat.sysstr(wild1.hex())
    wild_branch2 = 'wild/' + pycompat.sysstr(wild2.hex())
    assert all(do_list(ctx) == ['topic/default/zzetop']
               for ctx in [top1, top2])
    assert do_list(wild1) == [wild_branch1]
    assert set(do_list(wild2)) == {wild_branch2, 'branch/other'}
    assert set(do_list(changesets['other_base'])) == {'branch/other',
                                                      wild_branch1,
                                                      wild_branch2,
                                                      }
    for top in (top1, top2):
        assert do_list(top) == ['topic/default/zzetop']
    assert do_list(changesets['default']) == ['branch/default']
    all_branches = {'branch/other',
                    'branch/default',
                    'topic/default/zzetop',
                    wild_branch1,
                    wild_branch2,
                    }
    base = changesets['base']
    assert set(do_list(base)) == all_branches
    limited = set(do_list(base, limit=3))
    assert len(limited) == 3
    # until we have the ordering, we can only assert sub set.
    assert limited.issubset(all_branches)

    wrapper.update(top2)
    amended = wrapper.amend_file('foo')
    assert do_list(top2) == []
    assert do_list(amended) == ['topic/default/zzetop']


def test_list_tag_names_containing_commit(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    base = wrapper.write_commit('foo', message='Base')
    default = wrapper.write_commit('foo', message='Head of default')
    wrapper.command('tag', b'v3.2.1', rev=default.hex())

    other = wrapper.write_commit('foo', message='Start other',
                                 branch='other', parent=base)
    wrapper.command('tag', b'other-tag', rev=other.hex())

    def do_list(ctx, limit=0):
        chunks_iter = ref_stub.ListTagNamesContainingCommit(
            ListTagNamesContainingCommitRequest(
                repository=grpc_repo,
                commit_id=pycompat.sysstr(ctx.hex()),
                limit=limit,
            ))
        return [pycompat.sysstr(tag_name) for chunk in chunks_iter
                for tag_name in chunk.tag_names]

    all_tags = {'v3.2.1', 'other-tag'}
    assert set(do_list(base)) == all_tags
    assert do_list(default) == ['v3.2.1']
    assert do_list(other) == ['other-tag']

    limited = do_list(base, limit=1)
    assert len(limited) == 1
    assert limited[0] in all_tags

    wrapper.update(default)
    amended = wrapper.amend_file('foo')
    # The obsolete changeset is not filtered yet, as it has a child
    # that is not obsolete (but unstable).
    # TODO to avoid this nonsense in default opts, provide a
    # method of wrapper
    wrapper.command('evolve', stop=False, abort=False, rev=None,
                    dry_run=False, confirm=False, update=False,
                    phase_divergent=False, content_divergent=False,
                    orphan=True, tool=b'',
                    **{'continue': False, 'any': True, 'all': True,
                       'list': False})
    assert do_list(default) == []
    assert do_list(amended) == []


def test_get_tags_messages(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    wrapper.write_commit('foo', message='Base')
    wrapper.command('tag', b'v3.2.1', rev=b'.',
                    message=b"The tag message")
    tag_hex = wrapper.repo[b'tip'].hex()

    def do_list(tag_ids):
        resp_iter = ref_stub.GetTagMessages(
            GetTagMessagesRequest(
                repository=grpc_repo,
                tag_ids=(pycompat.sysstr(tag_id) for tag_id in tag_ids),
            ))
        return [pycompat.sysstr(resp.message) for resp in resp_iter]

    assert do_list([tag_hex]) == ["The tag message"]


def test_list_refs(ref_fixture):
    fixture = ref_fixture
    wrapper = fixture.repo_wrapper
    repo = wrapper.repo

    PSEUDO_REF_ALL = (b'ALL', ZERO_SHA_STR)

    # empty repo
    assert fixture.list_refs() == []
    assert fixture.list_refs(head=True) == []

    # with branches
    now = time.time()
    ctx1 = fixture.commit_file('foo', utc_timestamp=now - 30)
    sha1 = ctx1.hex().decode()
    ctx2 = fixture.commit_file('other', branch='aaa')
    sha2 = ctx2.hex().decode()

    assert fixture.list_refs(head=False) == [
        PSEUDO_REF_ALL,
        (b'refs/heads/branch/aaa', sha2),  # lexicographic sort ok
        (b'refs/heads/branch/default', sha1),
    ]
    # head (aka default GitLab branch)
    set_default_gitlab_branch(repo, b'branch/default')
    assert fixture.list_refs(head=True) == [
        PSEUDO_REF_ALL,
        (b'HEAD', sha1),
        (b'refs/heads/branch/aaa', sha2),
        (b'refs/heads/branch/default', sha1),
    ]

    # with tags
    wrapper.command('tag', b'v1.4', rev=ctx1.hex())
    tagging_sha = scmutil.revsingle(repo, b'.').hex().decode()
    assert fixture.list_refs() == [
        PSEUDO_REF_ALL,
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
        (b'refs/tags/v1.4', sha1),
    ]

    # special refs
    special = b'environments/17'
    special_ref = b'refs/' + special
    write_gitlab_special_ref(repo, special, ctx2.hex())
    assert fixture.list_refs() == [
        PSEUDO_REF_ALL,
        (special_ref, sha2),
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
        (b'refs/tags/v1.4', sha1),
    ]

    # with a keep around
    create_keep_around(repo, ctx1.hex())
    assert fixture.list_refs() == [
        PSEUDO_REF_ALL,
        (special_ref, sha2),
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
        (b'refs/keep-around/' + ctx1.hex(), sha1),
        (b'refs/tags/v1.4', sha1),
    ]

    # pattern used by gitaly-backup
    assert fixture.list_refs(patterns=[b'refs/']) == [
        PSEUDO_REF_ALL,
        (special_ref, sha2),
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
        (b'refs/keep-around/' + ctx1.hex(), sha1),
        (b'refs/tags/v1.4', sha1),
    ]

    # pattern used by Rails app for queries about branches and tags
    assert fixture.list_refs(patterns=[b'refs/heads/']) == [
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
    ]
    assert fixture.list_refs(patterns=[b'refs/tags/']) == [
        (b'refs/tags/v1.4', sha1),
    ]

    # more general patterns
    assert fixture.list_refs(patterns=[b'refs/heads/branch/a*']) == [
        (b'refs/heads/branch/aaa', tagging_sha),
    ]
    assert fixture.list_refs(patterns=[b'refs/t*/*']) == [
        (b'refs/tags/v1.4', sha1),
    ]
    assert fixture.list_refs(patterns=[b'refs/e*/*']) == [
        (special_ref, sha2),
    ]
    assert fixture.list_refs(patterns=[b'refs/heads/*/a*']) == [
        (b'refs/heads/branch/aaa', tagging_sha),
    ]
    # number of segments has to match
    assert fixture.list_refs(patterns=[b'*/a*']) == []
    assert fixture.list_refs(patterns=[b'refs/heads/br*']) == []
    assert fixture.list_refs(patterns=[b'refs/heads/br*/*']) == [
        (b'refs/heads/branch/aaa', tagging_sha),
        (b'refs/heads/branch/default', sha1),
    ]
    assert fixture.list_refs(
        patterns=[b'refs/keep-around/%s*' % ctx1.hex()[0:2]]
    ) == [
        (b'refs/keep-around/' + ctx1.hex(), sha1),
    ]

    # pointing_at_oids
    assert fixture.list_refs(pointing_at_oids=[ctx2.hex()]) == [
        (b'refs/environments/17', sha2)
    ]
    assert fixture.list_refs(head=True, pointing_at_oids=[ctx2.hex()]) == [
        (b'HEAD', sha1),
        (b'refs/environments/17', sha2)
    ]

    # sort options
    SortBy = ListRefsRequest.SortBy
    assert fixture.list_refs(patterns=[b'refs/heads/branch/'],
                             sort_by=SortBy(key=SortBy.Key.AUTHORDATE)) == [
                                 (b'refs/heads/branch/default', sha1),
                                 (b'refs/heads/branch/aaa', tagging_sha),
                             ]
    assert fixture.list_refs(patterns=[b'refs/heads/branch/'],
                             sort_by=SortBy(
                                 key=SortBy.Key.AUTHORDATE,
                                 direction=SortDirection.DESCENDING)) == [
                                 (b'refs/heads/branch/aaa', tagging_sha),
                                 (b'refs/heads/branch/default', sha1),
                             ]

    # reusing the fixture for the FindRefsByOID sibling method
    sha1 = ctx1.hex().decode()
    for oid in (sha1, sha1[:10]):
        assert fixture.find_refs_by_oid(oid=oid) == [
            'refs/heads/branch/default',
            'refs/tags/v1.4'
        ]
    assert fixture.find_refs_by_oid(oid=sha1, limit=1) == [
        'refs/heads/branch/default',
    ]
    assert fixture.find_refs_by_oid(oid=sha1, ref_patterns=['refs/tags/']) == [
        'refs/tags/v1.4',
    ]
    # TODO test 'creatordate' when implemented in ListRefs
    assert fixture.find_refs_by_oid(
        oid=sha1, sort_field='refname', limit=1
    ) == ['refs/heads/branch/default']


def test_update_references(ref_fixture):
    fixture = ref_fixture
    wrapper = fixture.repo_wrapper

    sha0 = wrapper.write_commit('afoo', message="Some foo").hex()
    sha1 = wrapper.write_commit('afoo', message="Some foo").hex()

    pipeline_1 = b'refs/pipelines/1'
    ka_0 = b'refs/keep-around/' + sha0
    fixture.update_refs([(pipeline_1, ZERO_SHA, sha1),
                         (ka_0, ZERO_SHA, sha0),
                         ])
    assert fixture.ref_exists(ka_0)
    assert fixture.ref_exists(pipeline_1)
    assert fixture.list_refs(patterns=[b'refs/pipelines/']) == [
        (pipeline_1, sha1.decode())
    ]

    fixture.update_refs([(pipeline_1, sha1, sha0),
                         (ka_0, sha0, ZERO_SHA),
                         ])
    assert not fixture.ref_exists(ka_0)
    assert fixture.list_refs(patterns=[b'refs/pipelines/']) == [
        (pipeline_1, sha0.decode())
    ]

    # edge case equivalent to no-op
    fixture.update_refs([(pipeline_1, sha0, sha0)])
    assert fixture.list_refs(patterns=[b'refs/pipelines/']) == [
        (pipeline_1, sha0.decode())
    ]

    # error cases
    with pytest.raises(grpc.RpcError) as exc_info:
        fixture.update_refs([(pipeline_1, None, b'branch/default')])
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    with pytest.raises(grpc.RpcError) as exc_info:
        fixture.update_refs([(ka_0, None, sha1)])
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    with pytest.raises(grpc.RpcError) as exc_info:
        fixture.update_refs([(pipeline_1, ZERO_SHA, sha1)])
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'reference already exists' in exc_info.value.details()

    with pytest.raises(grpc.RpcError) as exc_info:
        fixture.update_refs([(pipeline_1, sha1, sha0)])
    assert exc_info.value.code() == grpc.StatusCode.ABORTED

    # deletions
    fixture.update_refs([(pipeline_1, sha0, ZERO_SHA)])
    assert not fixture.ref_exists(pipeline_1)
