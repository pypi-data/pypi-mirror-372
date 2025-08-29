# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from mercurial import util as hgutil

from hgitaly import __version__
from ..servicer import HGitalyServicer
from ..stub.server_pb2 import (
    ServerInfoRequest,
    ServerInfoResponse,
    ServerSignatureRequest,
    ServerSignatureResponse,
)
from ..stub.server_pb2_grpc import ServerServiceServicer

base_logger = logging.getLogger(__name__)


class ServerServicer(ServerServiceServicer, HGitalyServicer):

    def ServerInfo(self,
                   request: ServerInfoRequest,
                   context) -> ServerInfoResponse:
        hg_version = hgutil.version().decode()
        return ServerInfoResponse(server_version=__version__,
                                  git_version=hg_version,
                                  )

    def ServerSignature(self,
                        request: ServerSignatureRequest,
                        context) -> ServerSignatureResponse:
        # Gitaly's signing key path configuration is optional (defaults to
        # empty string, see  `gitaly.toml.example`). We return the same value
        # as Gitaly does in that case, since Mercurial signing is currently
        # not implemented.
        return ServerSignatureResponse()
