# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import re
from pkg_resources import parse_version

from hgitaly.stub.server_pb2 import (
    ServerInfoRequest,
    ServerSignatureRequest,
)
from hgitaly.stub.server_pb2_grpc import ServerServiceStub
from grpc_health.v1.health_pb2 import (
    HealthCheckRequest,
    HealthCheckResponse,
)
from grpc_health.v1.health_pb2_grpc import HealthStub


def test_server_info(grpc_channel):
    grpc_stub = ServerServiceStub(grpc_channel)

    resp = grpc_stub.ServerInfo(ServerInfoRequest())
    version = resp.server_version
    assert version
    assert re.match(r'\d+[.]\d+[.]\d+',
                    parse_version(version).base_version) is not None
    hg_version = resp.git_version
    assert re.match(r'\d+[.]\d+', hg_version)


def test_server_signature(grpc_channel):
    grpc_stub = ServerServiceStub(grpc_channel)

    resp = grpc_stub.ServerSignature(ServerSignatureRequest())
    assert resp.public_key == b''


def test_health(grpc_channel):
    # does not test much, as the implementation is just registering the
    # provided servicer, which is entirely duplicated
    # in `confest.py`. At least it helps knowing the principle works
    # for us, and Comparison Tests will do something more end-to-end.
    grpc_stub = HealthStub(grpc_channel)
    resp = grpc_stub.Check(HealthCheckRequest())
    assert resp.status == HealthCheckResponse.SERVING
