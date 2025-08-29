# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pathlib

TEST_DATA_DIR = pathlib.Path(__file__).parent / 'data'


def license_content(name):  # pragma: no cover
    """Return the full test content of one of the licenses we ship.

    Now used in Comparison tests only.
    """
    return (TEST_DATA_DIR / (name + '.sample')).read_text()
