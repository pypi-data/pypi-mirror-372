# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Server startup logic, mono process and mono thread.

Can be used as a standalone server (e.g, for debugging purposes) or as
a worker in a service with multiple processes.

While the exposition as a Mercurial extension is certainly convenient for
many reasons, it is best to separate what is specific to the extension context
and what is just generic gRPC server code.

Note that gRPC will launch several threads no matter what, but only one will
be active at a given time.
"""
from concurrent import futures
import grpc
import logging
import mercurial
import signal
from urllib.parse import urlparse

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc

from ..service.interceptors import (
    RequestLoggerInterceptor,
)

from ..service.analysis import AnalysisServicer
from ..service.blob import BlobServicer
from ..service.commit import CommitServicer
from ..service.ref import RefServicer
from ..service.diff import DiffServicer
from ..service.mercurial_changeset import MercurialChangesetServicer
from ..service.mercurial_operations import MercurialOperationsServicer
from ..service.mercurial_repository import MercurialRepositoryServicer
from ..service.operations import OperationServicer
from ..service.repository import RepositoryServicer
from ..service.server import ServerServicer

from ..stub.analysis_pb2_grpc import add_AnalysisServiceServicer_to_server
from ..stub.blob_pb2_grpc import add_BlobServiceServicer_to_server
from ..stub.commit_pb2_grpc import add_CommitServiceServicer_to_server
from ..stub.ref_pb2_grpc import add_RefServiceServicer_to_server
from ..stub.diff_pb2_grpc import add_DiffServiceServicer_to_server
from ..stub.repository_pb2_grpc import (
    add_RepositoryServiceServicer_to_server
)
from ..stub.operations_pb2_grpc import (
    add_OperationServiceServicer_to_server
)
from ..stub.mercurial_changeset_pb2_grpc import (
    add_MercurialChangesetServiceServicer_to_server
)
from ..stub.mercurial_operations_pb2_grpc import (
    add_MercurialOperationsServiceServicer_to_server
)
from ..stub.mercurial_repository_pb2_grpc import (
    add_MercurialRepositoryServiceServicer_to_server
)
from ..stub.server_pb2_grpc import add_ServerServiceServicer_to_server

from .address import (
    InvalidUrl,
    UnsupportedUrlScheme,
    apply_default_port,
)

logger = logging.getLogger(__name__)


DEFAULT_TCP_PORT = 9237


class BindError(RuntimeError):
    pass


def init(listen_urls, storages):
    """Return server object for given parameters"""

    server_opts = (
        ('grpc.so_reuseport', 1),
        # As of GitLab 14.8.2, this matches the setting used by Rails'
        # Gitlab::GitalyClient.channel_args, hence avoiding the infamous
        # "Too many pings" error. For explanations, see
        # https://github.com/grpc/grpc/blob/master/doc/keepalive.md
        # in which the PARAMETERS_IN_CAPS are apparently to be replaced by the
        # corresponding *values* from https://github.com...
        # .../grpc/grpc/blob/v1.42.x/include/grpc/impl/codegen/grpc_types.h
        ('grpc.http2.min_ping_interval_without_data_ms', 19000),
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1),
                         interceptors=[RequestLoggerInterceptor(),
                                       ],
                         options=server_opts)
    add_AnalysisServiceServicer_to_server(AnalysisServicer(storages), server)
    add_BlobServiceServicer_to_server(BlobServicer(storages), server)
    add_CommitServiceServicer_to_server(CommitServicer(storages), server)
    add_RefServiceServicer_to_server(RefServicer(storages), server)
    add_DiffServiceServicer_to_server(DiffServicer(storages), server)
    add_MercurialChangesetServiceServicer_to_server(
        MercurialChangesetServicer(storages), server)
    add_MercurialOperationsServiceServicer_to_server(
        MercurialOperationsServicer(storages), server)
    add_MercurialRepositoryServiceServicer_to_server(
        MercurialRepositoryServicer(storages), server)
    add_OperationServiceServicer_to_server(
        OperationServicer(storages), server)
    add_RepositoryServiceServicer_to_server(
        RepositoryServicer(storages), server)
    add_ServerServiceServicer_to_server(ServerServicer(storages), server)

    # see https://github.com/grpc/grpc
    #       /blob/master/examples/python/health_checking/greeter_server.py
    # on how to toggle the health status
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    for url in listen_urls:
        try:
            parsed_url = urlparse(url)
        except ValueError as exc:
            raise InvalidUrl(url, *exc.args)
        try:
            if parsed_url.scheme == 'tcp':
                server.add_insecure_port(apply_default_port(parsed_url.netloc))
            elif parsed_url.scheme == 'unix':
                server.add_insecure_port(url)
            else:
                raise UnsupportedUrlScheme(parsed_url.scheme)
        except RuntimeError:
            raise BindError(url)

    return server


def server_process(worker_id, listen_urls, storages,
                   graceful_shutdown_timeout_seconds=300,
                   mono_process=False,
                   pytest_cov=False
                   ):
    if pytest_cov:
        from pytest_cov.embed import cleanup_on_signal
        cleanup_on_signal(signal.SIGTERM)
        cleanup_on_signal(signal.SIGINT)

    from hgitaly import procutil
    procutil.IS_CHILD_PROCESS = not mono_process

    server = init(listen_urls, storages)
    server.start()
    signal.signal(signal.SIGTERM,
                  lambda *a: server.stop(graceful_shutdown_timeout_seconds))

    logger.info("Server %d started", worker_id)
    logger.debug("Graceful shutdown timeout is %d seconds",
                 graceful_shutdown_timeout_seconds)
    try:
        server.wait_for_termination()
    except mercurial.error.SignalInterrupt:  # pragma no cover
        # here it would be better to catch the Mercurial signal
        # in our servicer layers and raise the clean thing that
        # grpc probably expects.
        # Another possibility would be to have our own handler in
        # the worker process, but that would perhaps prevent Mercurial
        # from doing its own cleaning.
        logger.info("Terminating on explicit signal")
