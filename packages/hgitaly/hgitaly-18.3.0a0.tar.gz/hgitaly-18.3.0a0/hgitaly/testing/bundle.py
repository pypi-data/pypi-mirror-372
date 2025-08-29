# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Mercurial bundle utilities meant for tests.

"""
from mercurial import (
    changegroup,
    exchange,
    hg,
    ui as uimod,
)
from mercurial.node import hex as node_hex
from mercurial_testhelpers import (
    as_bytes,
)


def list_bundle_contents(path):
    """Simple utility to list the contents.

    Inspired from mercurial.debugcommands. As usual Mercurial provides
    not much between very low level binary streaming methods meant for
    actual application or UI methods meant to write to stdout.
    """
    nodes = []
    ui = uimod.ui()
    with hg.openpath(ui, as_bytes(path)) as bundle:
        gen = exchange.readbundle(ui, bundle, as_bytes(path.basename))
        for part in gen.iterparts():
            if part.type == b'changegroup':
                version = part.params.get(b'version', b'01')
                cg = changegroup.getunbundler(version, part, b'UN')
                cg.changelogheader()
                nodes.extend(node_hex(delta[0]) for delta in cg.deltaiter())
    return dict(nodes=nodes)
