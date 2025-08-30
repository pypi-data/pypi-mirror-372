# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from grpc_health.v1.health_pb2 import (
    HealthCheckRequest,
)
from grpc_health.v1.health_pb2_grpc import HealthStub
from hgitaly.stub.server_pb2 import (
    ServerInfoRequest,
    ServerSignatureRequest,
)
from hgitaly.stub.server_pb2_grpc import ServerServiceStub

from . import skip_comparison_tests

if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_compare_server_info(hgitaly_rhgitaly_comparison_no_repo):
    fixture = hgitaly_rhgitaly_comparison_no_repo
    rpc_helper = fixture.rpc_helper(
        stub_cls=ServerServiceStub,
        method_name='ServerInfo',
        request_cls=ServerInfoRequest,
        repository_arg=False,
    )

    rpc_helper.assert_compare()


def test_compare_server_signature(gitaly_comparison):
    fixture = gitaly_comparison
    rpc_helper = fixture.rpc_helper(
        stub_cls=ServerServiceStub,
        method_name='ServerSignature',
        request_cls=ServerSignatureRequest,
        repository_arg=False,
    )

    rpc_helper.assert_compare()


def test_compare_health_check(hgitaly_rhgitaly_comparison_no_repo):
    fixture = hgitaly_rhgitaly_comparison_no_repo
    rpc_helper = fixture.rpc_helper(
        stub_cls=HealthStub,
        method_name='Check',
        request_cls=HealthCheckRequest,
        repository_arg=False,
    )

    rpc_helper.assert_compare()
