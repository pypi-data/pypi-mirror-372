# Copyright 2020-2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
from grpc import StatusCode
from google.protobuf.any_pb2 import Any
from google.rpc.status_pb2 import Status
import logging

from .stub.errors_pb2 import (
    CustomHookError,
)

from heptapod.gitlab.hooks import (
    GitLabPreReceiveError,
    GitLabPostReceiveError,
)

logger = logging.getLogger(__name__)

HGITALY_ISSUES_URL = "https://foss.heptapod.net/heptapod/hgitaly/-/issues"
STATUS_DETAILS_KEY = 'grpc-status-details-bin'


class ServiceError(RuntimeError):
    """An exception class to complement setting of context.

    In cases where a more precise exception than the bare `Exception()` raised
    by `ServicerContext.abort()` is useful.

    Caller is expected to set code and optionally details.
    """


def not_implemented(context, issue: int):
    """Raise with NOT_IMPLEMENTED status code and link to issue.
    """
    msg = "Not implemented. Tracking issue: %s/%d" % (HGITALY_ISSUES_URL,
                                                      issue)
    logger.error(msg)
    context.abort(StatusCode.UNIMPLEMENTED, msg)


def structured_abort(context, code, msg, structured_error):
    """Abort method with Gitaly's structured error.
    """
    metadata = context.trailing_metadata()
    # ensure mutability (as a list since that is how we'll do it)
    metadata = [] if metadata is None else list(metadata)

    as_grpc_any = Any()
    as_grpc_any.Pack(structured_error)
    status = Status(code=code.value[0], message=msg, details=[as_grpc_any])
    metadata.append((STATUS_DETAILS_KEY, status.SerializeToString()))
    context.set_trailing_metadata(metadata)
    context.abort(code, msg)


def msg_type_url(msg_cls):
    """Return the type url associated with `msg_cls` in `Any` messages."""
    sample = Any()
    sample.Pack(msg_cls())
    return sample.type_url


def parse_structured_error(exc, msg_cls):
    """Test helper for structured errors.

    Asserts that the structured error has the given Message class.

    :returns: (numeric code, user message, instance of `msg_cls`)
    """
    for md in exc.trailing_metadata():
        if md.key == STATUS_DETAILS_KEY:
            status = Status.FromString(md.value)
            break
    else:  # pragma no cover (case just to make tests easier to debug)
        raise LookupError("gRPC status details not found in trailing metadata")
    details = status.details[0]

    assert details.type_url == msg_type_url(msg_cls)

    return status.code, status.message, msg_cls.FromString(details.value)


def parse_assert_structured_error(exc, msg_cls, expected_code):
    """Assert code and type and return details and message object.
    """
    assert exc.code() == expected_code
    code, details, msg = parse_structured_error(exc, msg_cls)
    assert code == expected_code.value[0]
    return details, msg


@contextmanager
def operation_error_treatment(context, error_message_class, logger,
                              error_message_attr='gitlab_hook'):
    try:
        yield
    except GitLabPreReceiveError as exc:
        message = exc.message
        if isinstance(message, str):
            # should not normally happen, but let's make sure it is not
            # a problem
            message = message.encode('utf-8')
        attrs = {
            error_message_attr: CustomHookError(
                hook_type=CustomHookError.HOOK_TYPE_PRERECEIVE,
                stderr=message
            )
        }
        structured_abort(context, StatusCode.PERMISSION_DENIED,
                         "not allowed",
                         error_message_class(**attrs))
    except GitLabPostReceiveError as exc:
        # post-receive errors should not abort. Quoting current (v16.6)
        # Gitaly tests for UserMergeBranch:
        #   // The post-receive hook runs after references have been updated
        #   // and any failures of it are ignored.
        logger.error("Error in GitLab post-receive hook: %r", exc.message)


class MercurialNotFound(LookupError):
    """General class for all failed lookups.

    Better for us that to use `hg.errors.LookupError` because the latter is
    not systematically raised. Anyway, we need our own articulation point.
    """


class MercurialPathNotFound(MercurialNotFound):
    """Express that some path could not be found.

    This is generally in the context of some changeset that the caller is
    aware of, but it could be in an entire revset, in the workdir…
    """


class MercurialChangesetNotFound(MercurialNotFound):
    """Express that one or serveral changesets could not be found.

    In case the caller did a call possibly involving several changesets,
    the failing, perhaps more specific, expression can be set as argument.
    """
