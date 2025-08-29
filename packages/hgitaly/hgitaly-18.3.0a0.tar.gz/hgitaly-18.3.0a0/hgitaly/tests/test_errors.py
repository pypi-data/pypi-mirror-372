# Copyright 2020-2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import grpc
import pytest
import re

from heptapod.gitlab.hooks import (
    GitLabPreReceiveError,
    GitLabPostReceiveError,
)
from hgitaly.stub.ref_pb2 import (
    GetTagSignaturesRequest,
)
from hgitaly.stub.ref_pb2 import FindTagError
from hgitaly.stub.errors_pb2 import ReferenceNotFoundError
from hgitaly.stub.mercurial_operations_pb2 import PublishChangesetError

from hgitaly.stub.ref_pb2_grpc import RefServiceStub

from ..errors import (
    operation_error_treatment,
    structured_abort
)
from ..testing.context import (
    FakeContextAborter as FakeContext,
)

StatusCode = grpc.StatusCode


class FakeLogger:

    def __init__(self):
        self.records = []

    def error(self, fmt, *args):
        self.records.append(('error', fmt % args))


def test_not_implemented(grpc_channel):
    ref_stub = RefServiceStub(grpc_channel)

    with pytest.raises(grpc.RpcError) as exc_info:
        next(ref_stub.GetTagSignatures(GetTagSignaturesRequest()))
    exc = exc_info.value

    assert exc.code() == grpc.StatusCode.UNIMPLEMENTED
    assert re.search('https://.*/-/issues/75', exc.details()) is not None


def test_structured_abort():
    context = FakeContext()

    # example as close as real life as it gets: found with Gitaly Comparison
    # tests in a call for a non-existing tag.
    with pytest.raises(RuntimeError):
        structured_abort(
            context, StatusCode.NOT_FOUND, "tag does not exist",
            FindTagError(
                tag_not_found=ReferenceNotFoundError(
                    reference_name=b"refs/tags/nosuchtag")
            ))
    assert context.code() == StatusCode.NOT_FOUND
    assert context.details() == "tag does not exist"
    trailing = context.trailing_metadata()
    assert len(trailing) == 1
    assert trailing[0] == ('grpc-status-details-bin',
                           b"\x08\x05\x12\x12tag does not exist\x1aB\n'"
                           b"type.googleapis.com/gitaly.FindTagError\x12\x17\n"
                           b"\x15\n\x13refs/tags/nosuchtag")


def test_operation_error_treatment():
    context = FakeContext()
    logger = FakeLogger()
    with pytest.raises(RuntimeError):
        with operation_error_treatment(context, PublishChangesetError, logger):
            raise GitLabPreReceiveError(b"protected")

    assert context.code() == StatusCode.PERMISSION_DENIED
    trailing = context.trailing_metadata()
    assert len(trailing) == 1
    assert trailing[0] == ('grpc-status-details-bin',
                           b'\x08\x07\x12\x0bnot allowed\x1aD\n1type.'
                           b'googleapis.com/hgitaly.PublishChangesetError'
                           b'\x12\x0f\n\r\x12\tprotected\x18\x01')

    # works with `str` messages as well
    context = FakeContext()  # making sure test does not pass by coincidence
    with pytest.raises(RuntimeError):
        with operation_error_treatment(context, PublishChangesetError, logger):
            raise GitLabPreReceiveError("again protected")

    assert context.code() == StatusCode.PERMISSION_DENIED
    trailing = context.trailing_metadata()
    assert len(trailing) == 1
    assert b'again protected' in trailing[0][1]

    with operation_error_treatment(context, PublishChangesetError, logger):
        raise GitLabPostReceiveError(b"pipeline crash")

    # the b'' due to repr() is not pretty, but it is 100% safe
    assert logger.records == [
        ('error',
         "Error in GitLab post-receive hook: b'pipeline crash'")
    ]
