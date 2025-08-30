# Copyright 2024 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import shutil

from grpc import (
    RpcError,
    StatusCode
)
import pytest

from hgitaly.oid import (
    blob_oid,
)
from hgitaly.stub.analysis_pb2 import (
    CheckBlobsGeneratedRequest,
)
from hgitaly.stub.analysis_pb2_grpc import AnalysisServiceStub

from .fixture import ServiceFixture


class AnalysisFixture(ServiceFixture):

    stub_cls = AnalysisServiceStub

    def check_blobs_generated(self, rev_paths, **kw):
        Blob = CheckBlobsGeneratedRequest.Blob
        kw.setdefault('repository', self.grpc_repo)
        return [
            (blob.revision.decode(), blob.generated)
            for resp in self.rpc(
                    'CheckBlobsGenerated',
                    iter([CheckBlobsGeneratedRequest(
                        blobs=(Blob(revision=rp[0].encode(), path=rp[1])
                               for rp in rev_paths),
                        **kw)]))
            for blob in resp.blobs
        ]


@pytest.fixture
def analysis_fixture(grpc_channel, server_repos_root):
    with AnalysisFixture(grpc_channel, server_repos_root) as fixture:
        yield fixture


def test_check_blobs_generated(analysis_fixture):
    fixture = analysis_fixture
    wrapper = fixture.repo_wrapper

    sub = (wrapper.path / 'sub')
    sub.mkdir()

    cargo_path = b'sub/Cargo.lock'
    (wrapper.path / cargo_path.decode()).write_text("Content will not matter")
    xcode_path = b'something.nib'
    (wrapper.path / xcode_path.decode()).write_text("Content will not matter")
    (wrapper.path / 'foo').write_text("foo")

    stub_path = b'commit_pb2.py'
    import hgitaly.stub.commit_pb2 as stub_exmp
    shutil.copy(stub_exmp.__file__, wrapper.path / stub_path.decode())

    changeset = wrapper.commit(rel_paths=[cargo_path, stub_path, 'foo'],
                               add_remove=True,
                               message="Bunch of files")
    hg_sha = changeset.hex().decode()

    cargo_oid = blob_oid(wrapper.repo, hg_sha, cargo_path)
    xcode_oid = blob_oid(wrapper.repo, hg_sha, xcode_path)
    foo_oid = blob_oid(wrapper.repo, hg_sha, b'foo')
    stub_oid = blob_oid(wrapper.repo, hg_sha, stub_path)

    res = fixture.check_blobs_generated(((cargo_oid, cargo_path),
                                         (xcode_oid, xcode_path),
                                         (foo_oid, b'foo'),
                                         (stub_oid, stub_path)))
    assert res == [(cargo_oid, True), (xcode_oid, True),
                   (foo_oid, False), (stub_oid, True)]

    # call with the csid:path syntax works as well
    def blob_rev_path(csid, path):
        return (':'.join((csid, path.decode())), path)

    res = fixture.check_blobs_generated((blob_rev_path(hg_sha, cargo_path),
                                         blob_rev_path(hg_sha, b'foo'),
                                         blob_rev_path(hg_sha, stub_path)))
    assert [r[1] for r in res] == [True, False, True]

    # formally valid not resolving oids
    missing_path = b'unknown'
    missing_oid = blob_oid(wrapper.repo, hg_sha, missing_path)
    with pytest.raises(RpcError) as exc_info:
        fixture.check_blobs_generated([(missing_oid, missing_path)])
    assert exc_info.value.code() == StatusCode.INTERNAL

    arbitrary_sha1 = '12fe34ca' * 5
    missing_oid = blob_oid(wrapper.repo, arbitrary_sha1, missing_path)
    with pytest.raises(RpcError) as exc_info:
        fixture.check_blobs_generated([(missing_oid, missing_path)])
    assert exc_info.value.code() == StatusCode.INTERNAL

    # invalid oid
    missing_oid = '123'
    with pytest.raises(RpcError) as exc_info:
        fixture.check_blobs_generated([(missing_oid, missing_path)])
    assert exc_info.value.code() == StatusCode.INTERNAL
