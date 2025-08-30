# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Complementary tests of the testing harness for coverage.

Can also be useful to help with compatibility issues in hg-git
"""
import pytest

from hgitaly.gitlab_ref import (
    gitlab_special_ref_target,
)


from hgitaly.stub.commit_pb2 import FindCommitRequest
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


@pytest.fixture
def rpc_helper(gitaly_comparison):
    """Provide a fully working RpcCHelper.

    The associated method is taken from `test_commit.test_compare_find_commit`,
    but it should not matter so much as the setup with the
    Mercurial and Git repositories.
    """
    yield gitaly_comparison.rpc_helper(
        stub_cls=CommitServiceStub,
        method_name='FindCommit',
        request_cls=FindCommitRequest,
        request_sha_attrs=['revision'],
        response_sha_attrs=['commit.id', 'commit.parent_ids[]'],
        )


def test_hg2git_and_invalidation(rpc_helper):
    comp = rpc_helper.comparison

    # at startup, despite the absence of the hg_git attribute, its
    # invalidation does not fail
    assert 'hg_git' not in comp.__dict__
    comp.invalidate()
    assert 'hg_git' not in comp.__dict__  # still not there

    # Commits are converted to Git and hg2git gives the correspondence
    wrapper = comp.hg_repo_wrapper
    hg_sha0 = wrapper.commit_file('foo', message="Converted to Git").hex()
    git_sha0 = rpc_helper.hg2git(hg_sha0)
    # this is a real Git commit:
    assert comp.git_repo.branches()[b'branch/default'] == dict(
        title=b"Converted to Git",
        sha=git_sha0
    )
    # check a posteriori that earlier absence checks were relevant
    assert 'hg_git' in comp.__dict__

    # hg2git defaults on its input for this use-case:
    assert rpc_helper.hg2git(b'branch/something') == b'branch/something'

    # before invalidation, the helpers don't see new commits
    hg_sha1 = wrapper.commit_file('foo', message="New commit").hex()
    assert rpc_helper.hg2git(hg_sha1) == hg_sha1

    # solved by invalidation
    comp.invalidate()
    git_sha1 = rpc_helper.hg2git(hg_sha1)
    assert git_sha1 != hg_sha1
    assert comp.git_repo.branches()[b'branch/default'] == dict(
        title=b"New commit",
        sha=git_sha1
    )


def test_write_special_ref(gitaly_comparison):
    comp = gitaly_comparison
    wrapper = comp.hg_repo_wrapper
    git_repo = comp.git_repo
    changeset = wrapper.commit_file('foo')
    hg_sha = changeset.hex()
    git_sha = comp.hg_git.map_git_get(hg_sha)

    ref_name = b'pipelines/1'
    ref_path = b'refs/' + ref_name
    comp.write_special_ref(ref_name, hg_sha)
    assert gitlab_special_ref_target(wrapper.repo, ref_path) == changeset
    assert git_repo.all_refs()[ref_path] == git_sha

    with pytest.raises(LookupError):
        comp.write_special_ref(b'will/not/work', b'0123dead' * 5)

    with pytest.raises(LookupError):
        comp.write_special_ref(b'will/not/work', b'not-even-a-sha')
