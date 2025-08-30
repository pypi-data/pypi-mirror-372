# Copyright 2025 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from hgitaly.stub.mercurial_operations_pb2 import (
    MergeAnalysisRequest,
    InvalidateMergeAnalysisRequest,
)
from hgitaly.stub.mercurial_operations_pb2_grpc import (
    MercurialOperationsServiceStub,
)

from . import skip_comparison_tests

if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_compare_merge_analysis(hgitaly_rhgitaly_comparison):
    fixture = hgitaly_rhgitaly_comparison
    repo_wrapper = fixture.hg_repo_wrapper
    commit_file = repo_wrapper.commit_file
    default_ctx = commit_file('foo')
    top_cs = commit_file('foo', parent=default_ctx, topic='zetop')

    rpc_helper = fixture.rpc_helper(
        stub_cls=MercurialOperationsServiceStub,
        method_name='MergeAnalysis',
        request_cls=MergeAnalysisRequest,
    )
    assert_compare = rpc_helper.assert_compare
    target_rev = b'branch/default'
    assert_compare(source_revision=b'topic/default/zetop',
                   target_revision=target_rev)
    # second time to exert the cache
    assert_compare(source_revision=b'topic/default/zetop',
                   target_revision=target_rev)

    obs_hex = top_cs.hex()
    repo_wrapper.amend_file('foo')

    # without invalidation, we have a problem:
    obs_args = dict(source_revision=obs_hex, target_revision=target_rev)
    resp = rpc_helper.rpc('rhgitaly', **obs_args)
    assert not resp.has_obsolete_changesets  # oops
    resp = rpc_helper.rpc('hgitaly', **obs_args)
    assert resp.has_obsolete_changesets  # as expected

    # invalidation (RHGitaly only)
    resp = rpc_helper.stubs['rhgitaly'].InvalidateMergeAnalysis(
        InvalidateMergeAnalysisRequest(
            repository=fixture.hgitaly_repo)
    )
    assert resp.invalidated_count == 1

    # third time that works thanks to cache invalidation.
    assert_compare(**obs_args)

    # resolution errors (uncached)
    assert_errors = rpc_helper.assert_compare_errors
    assert_errors(source_revision=b'topic/default/unknown',
                  target_revision=b'branch/default')
    assert_errors(source_revision=b'topic/default/zetop',
                  target_revision=b'branch/unknown')
