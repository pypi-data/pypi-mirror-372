# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for the RHGitalyServer helper

These don't involve RHGitaly and not even Mercurial. The purpose is to
alert when the foundation of all Gitaly Comparison tests with RHGitaly is
broken, so that developers can focus right away on startup issues and the
like.
"""
import pytest

from hgitaly.stub.server_pb2 import (
    ServerInfoRequest,
)
from hgitaly.stub.server_pb2_grpc import ServerServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_rhgitaly_channel_with_sidecar(rhgitaly_channel, grpc_channel):
    server_stub = ServerServiceStub(rhgitaly_channel)
    assert server_stub.ServerInfo(ServerInfoRequest()).server_version
