# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""gRPC interceptors for HGitaly.

TODO This could be placed in a subpackage for all HGitaly code relying on
Protobuf/gRPC concepts rather than sitting alongseide services without
being a service implementations. We would thus have
`hgitaly.grpc.interceptors`, `hgitaly.grpc.service.ref`, perhaps even
`hgitaly.grpc.message`.
"""
import itertools
import logging
import time
from typing import (
    Any,
    Callable
)

import grpc
from grpc_interceptor import ServerInterceptor

from .. import message
from ..logging import LoggerAdapter


base_logger = logging.getLogger(__name__)


def is_streaming(message) -> bool:
    """Tell whether a gRPC message is streaming (iterable).

    Note that messages aren't plain strings nor Python collections.
    """
    return hasattr(message, '__iter__')


def stream_with_time_log(response, start, logger, extra_log):
    yield from response

    extra_log['elapsed_seconds'] = time.time() - start
    logger.info("Finished RPC", extra=extra_log)


class RequestLoggerInterceptor(ServerInterceptor):
    """Log every request.

    Mostly taken from the example in grpc-interceptor documentation.

    In case of streaming requests, only the first one of the stream gets
    logged. With Gitaly convention, this is usually the only one carrying
    interesting metadata.
    """

    def intercept(
            self,
            method: Callable,
            request: Any,
            context: grpc.ServicerContext,
            method_name: str,
    ) -> Any:
        if is_streaming(request):
            first = next(iter(request))
            request = itertools.chain([first], request)
        else:
            first = request

        # of course it would be great to change the logger depending
        # on the service, but with (H)Gitaly naming conventions, the class
        # name of the request contains all the information.
        start = time.time()
        extra_log = dict(request=message.Logging(first))
        logger = LoggerAdapter(base_logger, context)
        logger.info("Starting to process RPC", extra=extra_log)

        response = method(request, context)

        if is_streaming(response):
            return stream_with_time_log(response, start, logger, extra_log)
        else:
            extra_log['elapsed_seconds'] = time.time() - start
            logger.info("Finished RPC", extra=extra_log)
            return response
