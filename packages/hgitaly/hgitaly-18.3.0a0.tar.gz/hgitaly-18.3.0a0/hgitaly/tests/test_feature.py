# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

# TODO bring full coverage directly from here, because there might
# be points in time where it won't be used at all by gRPC methods
import pytest

from ..testing.context import FakeServicerContext
from .. import feature


class FakeContext(FakeServicerContext):

    def __init__(self, invocation_metadata):
        self._invocation_metadata = invocation_metadata

    def invocation_metadata(self):
        return self._invocation_metadata


@pytest.fixture
def feature_flags(monkeypatch):
    monkeypatch.setattr(feature, 'FEATURE_FLAGS',
                        {'default-disabled': False,
                         'default-enabled': True,
                         })
    # in case we do a full tests run with the all-enabling environment
    # variable (can be useful to detect flags that we should implement)
    monkeypatch.setattr(feature, 'ALL_ENABLED', False)
    yield monkeypatch


def test_is_enabled_defaults(feature_flags):
    context = FakeContext(())
    assert feature.is_enabled(context, 'default-enabled')
    assert not feature.is_enabled(context, 'default-disabled')
    with pytest.raises(feature.UndefinedError) as exc_info:
        feature.is_enabled(context, 'not-defined')
    assert exc_info.value.args == ('not-defined', )


def test_is_enabled_all_enabled(feature_flags):
    context = FakeContext(())
    feature_flags.setattr(feature, 'ALL_ENABLED', True)
    assert feature.is_enabled(context, 'default-disabled')

    # still raises when HGitaly wants to use an undefined flag
    with pytest.raises(feature.UndefinedError) as exc_info:
        feature.is_enabled(context, 'not-defined')
    assert exc_info.value.args == ('not-defined', )


def test_is_enabled_context(feature_flags):
    context = FakeContext((
        ('gitaly-feature-default-disabled', 'true'),
    ))
    assert feature.is_enabled(context, 'default-disabled')


def test_as_grpc_metadata():
    assert feature.as_grpc_metadata(None) is None
    assert feature.as_grpc_metadata((
        ('my-flag', True),
        ('their-flag', False),
    )) == [
        (b'gitaly-feature-my-flag', b'true'),
        (b'gitaly-feature-their-flag', b'false'),
    ]
