# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from mercurial import error

from heptapod.testhelpers import (
    LocalRepoWrapper,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(hgitaly=''),
                                 ))


def test_description_revsets(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    wrapper.write_commit('foo', message="It does not appear in message")
    ctx2 = wrapper.write_commit('bar',
                                user="Jane Foo <jfoo@heptapod.test>",
                                message=r"nor in that one! Yes \ is antislash")
    ctx3 = wrapper.write_commit('baz', message="Finally, a foo in title")
    ctx4 = wrapper.write_commit('baz',
                                message="And also deeper in description\n\n"
                                "here is the foo that was wanted.")

    foo_revs = {ctx3.rev(), ctx4.rev()}

    # hpd_dsc_rx matches changeset description only
    assert set(repo.revs("hpd_dsc_rx('foo')")) == foo_revs
    # …and is case-sensitive
    assert len(repo.revs("hpd_dsc_rx('Foo')")) == 0
    # hpd_dsc_irx works the same except that it ignores case
    assert set(repo.revs("hpd_dsc_irx('Foo')")) == foo_revs
    # The pattern is really a regular expression
    assert set(repo.revs(r"hpd_dsc_rx('[fg]o{2,}\s')")) == foo_revs
    # special cases
    assert set(repo.revs(r"hpd_dsc_rx(r'\\')")) == {ctx2.rev()}

    with pytest.raises(error.ParseError) as exc_info:
        repo.revs("hpd_dsc_rx('[]')")
    assert 'invalid regexp' in str(exc_info.value)

    with pytest.raises(error.ParseError) as exc_info:
        repo.revs("hpd_dsc_rx()")
    assert 'requires a string' in str(exc_info.value)
