# Copyright 2024 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from grpc import StatusCode

from ..errors import MercurialNotFound
from ..file_content import is_blob_generated
from ..servicer import HGitalyServicer

from ..stub.analysis_pb2 import (
    CheckBlobsGeneratedRequest,
    CheckBlobsGeneratedResponse,
)
from ..stub.analysis_pb2_grpc import AnalysisServiceServicer

base_logger = logging.getLogger(__name__)


class AnalysisServicer(AnalysisServiceServicer, HGitalyServicer):
    """AnalysisService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """

    def CheckBlobsGenerated(self, request: CheckBlobsGeneratedRequest,
                            context) -> CheckBlobsGeneratedResponse:
        first = True
        RespBlob = CheckBlobsGeneratedResponse.Blob
        for req in request:
            if first:
                # blobs are given by oid, hence as in direct changeset Node
                # IDs, the unfiltered repo is the right one for the task
                repo = self.load_repo(req.repository, context).unfiltered()
                first = False

            try:
                yield CheckBlobsGeneratedResponse(
                    blobs=(RespBlob(revision=blob.revision,
                                    generated=is_blob_generated(repo, blob))
                           for blob in req.blobs)
                )
            except (MercurialNotFound, ValueError):
                context.abort(StatusCode.INTERNAL,
                              "reading object: object not found")
