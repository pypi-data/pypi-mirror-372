# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import logging
from typing import Any


_missing = object()

CORRELATION_ID_MD_KEY = 'x-gitlab-correlation-id'


def extract_correlation(context):
    """Extract and cache correlation info for a gRPC context."""

    corr_id = getattr(context, 'correlation_id', _missing)
    if corr_id is _missing:
        for md in context.invocation_metadata():
            if md.key == CORRELATION_ID_MD_KEY:
                corr_id = md.value
                break
        else:
            # avoid searching again
            corr_id = None
        context.correlation_id = corr_id
    return corr_id


@attr.define
class LoggerAdapter(logging.LoggerAdapter):
    logger: Any
    grpc_context: Any

    def process(self, msg, kwargs):
        extra = kwargs.get('extra')
        if extra is None:
            kwargs['extra'] = extra = {}

        # set on context by interceptor
        extra['correlation_id'] = extract_correlation(self.grpc_context)
        return msg, kwargs
