# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Various changelog operations

These are utilities involving several changesets, either in the arguments or
in the response.
"""


def ancestor(cs1, cs2):
    """Greatest common ancestor of two changesets."""
    return cs1.repo().revs("ancestor(%s, %s)", cs1, cs2).first()


def merge_content(source, target):
    """Iterator of changeset contexts for the merge of source into target."""
    repo = source.repo()
    for rev in repo.revs("only(%s, %s)", source, target):
        yield repo[rev]
