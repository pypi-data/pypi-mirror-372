# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest

from hgitaly.stub.mercurial_changeset_pb2 import (
    ListMercurialChangesetsRequest,
    MercurialChangeset,
    MercurialChangesetField,
    MercurialChangesetPhase,
    MercurialRepositoryView,
)
from hgitaly.stub.mercurial_changeset_pb2_grpc import (
    MercurialChangesetServiceStub,
)

from .fixture import ServiceFixture


class ChangesetFixture(ServiceFixture):

    stub_cls = MercurialChangesetServiceStub

    def list_changesets(self, **kw):
        return [changeset
                for resp in self.stub.ListMercurialChangesets(
                        ListMercurialChangesetsRequest(
                            repository=self.grpc_repo, **kw)
                        )
                for changeset in resp.changesets
                ]


@pytest.fixture
def changeset_fixture(grpc_channel, server_repos_root):
    with ChangesetFixture(grpc_channel, server_repos_root) as fixture:
        yield fixture


def test_list_changesets(changeset_fixture):
    commit_file = changeset_fixture.repo_wrapper.commit_file
    default_ctx = commit_file('foo')
    default_hex = default_ctx.hex()
    changeset_fixture.repo_wrapper.set_phase('public', [default_hex])

    obs_hex = commit_file('foo', parent=default_ctx, topic='zetop').hex()
    topic_hex = changeset_fixture.repo_wrapper.amend_file('foo').hex()

    list_changesets = changeset_fixture.list_changesets

    ALL = MercurialChangesetField.ALL
    PHASE = MercurialChangesetField.PHASE
    DRAFT = MercurialChangesetPhase.DRAFT
    PUBLIC = MercurialChangesetPhase.PUBLIC
    OBSOLETE = MercurialChangesetField.OBSOLETE
    UNFILTERED = MercurialRepositoryView.UNFILTERED

    assert list_changesets(
        revset=obs_hex, fields=[OBSOLETE], view=UNFILTERED
    ) == [
        MercurialChangeset(id=obs_hex, obsolete=True)
    ]
    assert list_changesets(
        revset=obs_hex, fields=[ALL], view=UNFILTERED
    ) == [
        MercurialChangeset(id=obs_hex,
                           phase=DRAFT,
                           parent_ids=[default_hex],
                           branch=b'default',
                           topic=b'zetop',
                           topic_namespace=b'none',
                           fqbn=b'default//zetop',
                           obsolete=True,
                           )
    ]
    assert list_changesets(revset=b'::zetop', fields=[PHASE, OBSOLETE]) == [
        MercurialChangeset(id=default_hex, obsolete=False, phase=PUBLIC),
        MercurialChangeset(id=topic_hex, obsolete=False, phase=DRAFT),
    ]

    with pytest.raises(grpc.RpcError) as exc_info:
        list_changesets(revset=obs_hex, fields=[ALL])

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
