# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

def assert_recv(pipe, expected, timeout=2):
    """Read data from a pipe and assert it is as expected, without blocking.

    Using this rather than just `pipe.recv()` prevents blocking the
    tests upon errors.

    The default timeout is long, but acceptable to humans and CI jobs.
    """
    assert pipe.poll(timeout=timeout)
    received = pipe.recv()  # being nice (and necessary) for pdb debugging
    assert received == expected
