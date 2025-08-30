# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

# TODO bring full coverage directly from here, because there might
# be points in time where it won't be used at all by gRPC methods
import grpc
from grpc.beta import _metadata


class FakeServicerContext(grpc.ServicerContext):
    """A base class for fake servicer contexts in tests.

    This base class allow testing harness to implement only a few methods,
    while still going through the ABC checking that all abstract methods are
    implemented.

    This can detect API changes in the base class. For an example, assume
    that main code relies on the `invocation_metadata` method,
    and corresponding unit  test provides a mock implementation. If the method
    is renamed in :class:`ServicerContext` as `incoming_metadata`, the
    mock implementation suddenly will not implement all abstract methods
    and the test run will fail, alerting us of the needed adaptation.

    This is heavy-handed, but still a bit better than not doing any checking.
    Of course most of HGItaly is covered by integration tests such as
    in `hgitaly.service.tests`, but some might temporarily not be
    (concrete case being the feature flags system at a time where there
    is no relevant Gitaly feature flag for HGitaly), and hence requires
    full coverage in *unit* tests.
    """

    def fake_impl(self):
        """To make ABC consider an abstract method to be implemented."""
        raise NotImplementedError()  # pragma no cover

    abort = fake_impl
    abort_with_status = fake_impl
    add_callback = fake_impl
    auth_context = fake_impl
    cancel = fake_impl
    invocation_metadata = fake_impl
    is_active = fake_impl
    peer = fake_impl
    peer_identities = fake_impl
    peer_identity_key = fake_impl
    send_initial_metadata = fake_impl
    set_code = fake_impl
    set_details = fake_impl
    set_trailing_metadata = fake_impl
    time_remaining = fake_impl


class FakeContextAbort(RuntimeError):
    pass


class FakeContextAborter(FakeServicerContext):
    """A fake context that is good enough to test various `abort()` cases.
    """

    _trailing_metadata = _code = _details = None

    def set_trailing_metadata(self, metadata):
        self._trailing_metadata = metadata

    def trailing_metadata(self):
        return self._trailing_metadata

    def code(self):
        return self._code

    def details(self):
        return self._details

    def abort(self, code, details):
        self._code = code
        self._details = details
        raise FakeContextAbort()


def metadatum(key, val):
    return _metadata._Metadatum(key, val)
