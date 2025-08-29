# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Listen address commmon utilities.
"""
import socket


DEFAULT_TCP_PORT = 9237


class UnsupportedUrlScheme(ValueError):
    pass


class InvalidUrl(ValueError):
    pass


def analyze_netloc(netloc):
    """Everything needed to bind a TCP socket from a parsed URL

    :return: family, host, port. port is ``None`` if the netloc does not
       specify it.
    """
    if netloc.startswith('['):
        h_end = netloc.find(']')
        if h_end < 0:
            raise ValueError(netloc)
        host = netloc[1:h_end]
        family = socket.AF_INET6

        if h_end + 1 == len(netloc):
            return family, host, None

        if netloc[h_end + 1] != ':':
            raise ValueError(netloc)
        return family, host, int(netloc[h_end + 2:])

    split = netloc.rsplit(':', 1)
    if len(split) == 1:
        host, port = netloc, None
    else:
        host, port = split
        port = int(port)

    # here actually I should let gai do the job
    # the thing is, we *must* do the same
    # as gRPC and I don't know yet what this is
    family = socket.AF_INET
    return family, host, port


def apply_default_port(netloc):
    """Return a netloc with default port applied if port wasn't specified."""
    family, host, port = analyze_netloc(netloc)
    if port is None:
        port = DEFAULT_TCP_PORT
    if family == socket.AF_INET6:
        return '[%s]:%d' % (host, port)
    return '%s:%d' % (host, port)
