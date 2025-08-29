# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for the GitalyServer helper

These don't involve HGitaly and not even Mercurial. The purpose is to
ensure that the foundation of all Gitaly comparison tests keeps working.
"""
import pytest

from hgitaly.stub.repository_pb2 import (
    CreateRepositoryRequest,
    RepositoryExistsRequest,
)
from hgitaly.stub.shared_pb2 import Repository
from hgitaly.stub.repository_pb2_grpc import RepositoryServiceStub
from hgitaly.testing.storage import (
    DEFAULT_STORAGE_NAME,
    git_repo_path,
)

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_gitaly_channel(gitaly_channel, server_repos_root):
    channel = gitaly_channel
    repo_stub = RepositoryServiceStub(channel)

    relpath = 'foo.git'
    repo = Repository(relative_path=relpath, storage_name=DEFAULT_STORAGE_NAME)
    repo_stub.CreateRepository(CreateRepositoryRequest(repository=repo))

    git_path = git_repo_path(server_repos_root, relpath)
    assert git_path.is_dir()
    assert (git_path / 'HEAD').exists

    assert repo_stub.RepositoryExists(
        RepositoryExistsRequest(repository=repo)
    ).exists
