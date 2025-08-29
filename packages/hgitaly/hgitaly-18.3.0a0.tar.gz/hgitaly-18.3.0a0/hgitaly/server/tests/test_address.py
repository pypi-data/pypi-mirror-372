# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from socket import (
    AF_INET,
    AF_INET6,
)
import pytest

from ..address import (
    DEFAULT_TCP_PORT,
    analyze_netloc,
    apply_default_port,
)


def test_analyze_netloc():
    analyze = analyze_netloc

    assert analyze('127.1.2.3') == (AF_INET, '127.1.2.3', None)
    assert analyze('127.1.2.3:66') == (AF_INET, '127.1.2.3', 66)

    for ip6 in ('::1', '2001:db8:cafe::1', '2001:db8:1:2:3:4:5:6'):
        assert analyze('[%s]' % ip6) == (AF_INET6, ip6, None)
        assert analyze('[%s]:66' % ip6) == (AF_INET6, ip6, 66)

    with pytest.raises(ValueError) as exc_info:
        analyze('[::1')
    assert exc_info.value.args == ('[::1', )

    with pytest.raises(ValueError) as exc_info:
        analyze('[::]foo')
    assert exc_info.value.args == ('[::]foo', )


def test_apply_default_port():
    adp = apply_default_port
    for host in ('localhost', '[::1]', '127.0.0.1'):
        assert adp(host + ':123') == host + ':123'
        assert adp(host) == host + ':' + str(DEFAULT_TCP_PORT)
