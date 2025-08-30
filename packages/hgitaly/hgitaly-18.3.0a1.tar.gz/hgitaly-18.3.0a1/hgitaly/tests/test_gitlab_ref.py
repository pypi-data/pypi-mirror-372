# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from copy import deepcopy
import shutil

import pytest
from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from heptapod.testhelpers.gitlab import GitLabMirrorFixture

from hgext3rd.heptapod.branch import read_gitlab_typed_refs
from hgext3rd.heptapod.special_ref import (
    write_gitlab_special_ref,
)
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)
from .common import (
    MINIMAL_HG_CONFIG,
)
from ..gitlab_ref import (
    gitlab_special_ref_target,
    iter_gitlab_special_refs_as_refs,
    iter_keep_arounds_as_refs,
    keep_around_ref_path,
    parse_keep_around_ref_path,
)
from .. import gitlab_ref as glref_mod  # for monkey-patching


@pytest.fixture
def repo_wrapper(tmpdir):
    config = deepcopy(MINIMAL_HG_CONFIG)
    config.setdefault('heptapod', {})['repositories-root'] = tmpdir
    wrapper = LocalRepoWrapper.init(tmpdir / 'repo.hg', config=config)
    yield wrapper.repo, wrapper


@pytest.fixture
def mirror(tmpdir, monkeypatch):
    config = MINIMAL_HG_CONFIG.copy()
    config['extensions']['heptapod'] = ''
    config.setdefault('heptapod', {}).update((
        ('native', 'no'),
        ('repositories-root', tmpdir),
    ))

    with GitLabMirrorFixture.init(tmpdir / 'repos', monkeypatch,
                                  common_repo_name='repo',
                                  hg_config=config) as mirror:
        mirror.activate_mirror()
        yield mirror


def test_gitlab_special_ref_target(repo_wrapper):
    repo, wrapper = repo_wrapper

    ref_name = b'merge-requests/1/head'
    ref_path = b'refs/merge-requests/1/head'

    # empty repo, the file doesn't even exist
    assert gitlab_special_ref_target(repo, ref_path) is None

    base = wrapper.commit_file('foo')
    write_gitlab_special_ref(repo, ref_name, base)

    assert gitlab_special_ref_target(repo, ref_path) == base

    # making target obsolete doesn't hide it to the special refs subsystem
    successor = wrapper.amend_file('foo')
    assert gitlab_special_ref_target(repo, ref_path) == base

    # updates are applied immediately (cache is updated)
    write_gitlab_special_ref(repo, ref_name, successor.hex())
    assert gitlab_special_ref_target(repo, ref_path) == successor

    # unknown, not special, alien and completely bogus cases
    assert gitlab_special_ref_target(repo, b'refs/pipelines/123') is None
    assert gitlab_special_ref_target(repo, b'refs/heads/branch/main') is None
    assert gitlab_special_ref_target(repo, b'refs/pull/123/head') is None
    assert gitlab_special_ref_target(repo, b'bogus') is None


def test_gitlab_special_ref_target_ensure(mirror):
    wrapper = mirror.hg_repo_wrapper
    git_repo = mirror.git_repo

    ctx = wrapper.commit_file('foo')
    git_sha = git_repo.branches()[b'branch/default']['sha']

    ref_path = b'refs/environments/654'
    git_repo.write_ref(ref_path, git_sha)

    assert gitlab_special_ref_target(wrapper.repo, ref_path) == ctx


def should_not_be_called(*a, **kw):  # pragma: no cover
    raise AssertionError("should not have been called")


def test_special_ref_not_ensure(mirror, monkeypatch):
    wrapper = mirror.hg_repo_wrapper
    git_repo = mirror.git_repo

    shutil.rmtree(git_repo.path)
    monkeypatch.setattr(glref_mod, 'ensure_gitlab_special_refs',
                        should_not_be_called)
    monkeypatch.setattr(glref_mod, 'ensure_gitlab_keep_arounds',
                        should_not_be_called)

    ref_path = b'refs/environments/654'
    assert gitlab_special_ref_target(wrapper.repo, ref_path) is None
    assert tuple(iter_keep_arounds_as_refs(wrapper.repo)) == ()


def test_write_special_ref(repo_wrapper):
    repo, wrapper = repo_wrapper

    ref_name = b'pipelines/123'
    ref_path = b'refs/pipelines/123'

    base = wrapper.commit_file('foo')
    write_gitlab_special_ref(repo, ref_name, base)

    # direct read without cache
    assert read_gitlab_typed_refs(repo, 'special-refs') == {
        ref_name: base.hex()}

    # cache got updated (actually, created) anyway
    assert gitlab_special_ref_target(repo, ref_path) == base

    # passing a hex sha (bytes) also works and cache is updated
    ctx1 = wrapper.commit_file('foo')
    write_gitlab_special_ref(repo, ref_name, ctx1.hex())
    assert read_gitlab_typed_refs(repo, 'special-refs') == {
        ref_name: ctx1.hex()}
    assert gitlab_special_ref_target(repo, ref_path) == ctx1


def test_iterate_special_ref(repo_wrapper):
    repo, wrapper = repo_wrapper

    ref_name = b'pipelines/123'
    ref_path = b'refs/pipelines/123'

    base = wrapper.commit_file('foo')
    base_hex = base.hex().decode()

    assert list(iter_gitlab_special_refs_as_refs(repo)) == []
    write_gitlab_special_ref(repo, ref_name, base)

    assert list(iter_gitlab_special_refs_as_refs(repo)) == [
        (ref_path, base)]
    assert list(iter_gitlab_special_refs_as_refs(repo, deref=False)) == [
        (ref_path, base_hex)]


def test_iterate_keep_arounds(repo_wrapper):
    repo, wrapper = repo_wrapper
    ctx = wrapper.commit_file('foo')
    sha_bytes = ctx.hex()
    sha_str = sha_bytes.decode()

    assert list(iter_keep_arounds_as_refs(repo)) == []
    create_keep_around(repo, sha_bytes)

    assert list(iter_keep_arounds_as_refs(repo)) == [
        (b'refs/keep-around/' + sha_bytes, ctx)]
    assert list(iter_keep_arounds_as_refs(repo, deref=False)) == [
        (b'refs/keep-around/' + sha_bytes, sha_str)]


def test_parse_keep_around_ref_path():
    sha = b'12abdc43' * 5
    ka_ref = b'refs/keep-around/' + sha
    assert parse_keep_around_ref_path(ka_ref) == sha
    assert keep_around_ref_path(sha) == ka_ref

    assert parse_keep_around_ref_path(b'refs/pipeline/17') is None
