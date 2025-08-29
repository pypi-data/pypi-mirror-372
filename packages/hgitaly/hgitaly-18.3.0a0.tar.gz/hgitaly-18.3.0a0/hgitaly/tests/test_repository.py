# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..repository import (
    config_inherits,
)


def test_config_inherits(tmpdir):
    wrapper = LocalRepoWrapper.init(tmpdir / 'repo')
    repo = wrapper.repo
    assert config_inherits(repo) is False

    # all other cases are covered by MercurialRepositoryService tests
