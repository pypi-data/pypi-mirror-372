# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from ..revset import (
    FollowNotImplemented,
    revset_from_git_revspec,
)


def test_follow_not_implemented():
    # we don't even need to pass a true repo or revisions to test this
    with pytest.raises(FollowNotImplemented):
        revset_from_git_revspec(None, b'foo..bar', for_follow=True)

    with pytest.raises(FollowNotImplemented):
        revset_from_git_revspec(None, b'foo...bar', for_follow=True)
