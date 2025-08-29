# Copyright 2025 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities for identificaton of servers and client.

An HGitaly client always have a pair of identifiers:

- the Client ID is a globally unique and persistent identifier
- the Incarnation ID is volatile. It is convenient for it to be the UNIX
  timestamp in seconds, serialized as a decimal string, but that is not
  mandatory.

If an operation records some Client / Incarnation ID pair, a subsequent
change of the Incarnation ID for the same client means that the client has
restarted since the recording, and thus that the operation is obsolete
(whether it finished normally or not, the latter including having been harshly
killed).

An HGitaly server is always consider to be its own client, even if it accesses
the resources flagged with these IDs in-process rathere than through gRPC.
"""
from pathlib import Path
import time
import uuid

INCARNATION_ID = str(int(time.time()))
CLIENT_ID_SLUG = '+hgitaly/self-client.uuid'
CLIENT_ID = None  # initialized at startup


def ensure_client_id(config_root):
    """To be used in startup sequence, before any concurrency is possible."""
    global CLIENT_ID

    path = Path(config_root) / CLIENT_ID_SLUG
    if path.exists():
        CLIENT_ID = path.read_text().strip()
        return

    client_id = str(uuid.uuid4())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(client_id)
    CLIENT_ID = client_id
