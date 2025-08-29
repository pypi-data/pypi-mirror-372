# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from mercurial.node import nullrev

from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from hgext3rd.heptapod.special_ref import (
    write_gitlab_special_ref,
)
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)

from ..gitlab_ref import (
    keep_around_ref_path,
)
from ..revision import (
    ALL_CHANGESETS,
    RevisionNotFound,
    gitlab_revision_changeset,
    gitlab_revision_hash,
    resolve_revspecs_positive_negative,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic='', evolve=''),
                                 ))


def test_gitlab_revision_changeset_by_hex(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')

    assert gitlab_revision_changeset(repo, ctx.hex()) == ctx

    # special node ids
    # collision very unlikely, but still a prefix
    assert gitlab_revision_changeset(repo, b'f' * 39) is None
    assert gitlab_revision_changeset(repo, b'0' * 39).rev() == nullrev
    # full node hex
    assert gitlab_revision_changeset(repo, b'f' * 40) is None
    assert gitlab_revision_changeset(repo, b'00000000' * 5).rev() == nullrev

    wrapper.command('amend', message=b'amended')

    obs_ctx = gitlab_revision_changeset(repo, ctx.hex())
    assert obs_ctx == ctx
    assert obs_ctx.obsolete()


def test_gitlab_revision_changeset_empty_repo(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    assert gitlab_revision_changeset(repo, b'HEAD') is None


def test_gitlab_revision_special_ref(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')
    ref_name = b'merge-requests/1/head'
    ref_path = b'refs/merge-requests/1/head'

    write_gitlab_special_ref(repo, ref_name, ctx)
    assert gitlab_revision_changeset(repo, ref_path) == ctx


def test_gitlab_revision_keep_around(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')
    sha = ctx.hex()
    create_keep_around(repo, sha)

    assert gitlab_revision_changeset(repo, keep_around_ref_path(sha)) == ctx
    assert gitlab_revision_changeset(
        repo, keep_around_ref_path(b'cafe' * 10)) is None


def test_gitlab_revision_gl_branch(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    assert (
        gitlab_revision_changeset(repo, b'refs/heads/branch/default')
        == ctx
    )
    assert gitlab_revision_changeset(repo, b'branch/default') == ctx

    # precise ref form can be for nothing but a branch
    # here, just stripping the prefix would end over to direct lookup by
    # tag, bookmark or node ID
    assert gitlab_revision_changeset(repo, b'refs/heads/' + ctx.hex()) is None


def test_gitlab_revision_node_id(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    assert gitlab_revision_changeset(repo, ctx.hex()) == ctx
    assert gitlab_revision_changeset(repo, b'12ca34fe' * 5) is None


def test_gitlab_revision_hash(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    assert gitlab_revision_hash(repo, b'branch/default') == ctx.hex()
    with pytest.raises(RevisionNotFound) as exc_info:
        gitlab_revision_hash(repo, b'unknown')
    assert exc_info.value.args == (b'unknown', )


def test_resolve_revspecs_positive_negative(tmpdir):
    wrapper = make_repo(tmpdir)
    sha1 = wrapper.write_commit('foo').hex()
    sha2 = wrapper.write_commit('bar', branch='other').hex()

    def resolve(revisions, **kw):
        return resolve_revspecs_positive_negative(wrapper.repo, revisions,
                                                  **kw)

    empty = set()
    assert resolve([b'branch/default']) == ({sha1}, empty)
    assert resolve([b'branch/default',
                    b'branch/other']) == ({sha1, sha2}, empty)
    assert resolve([b'branch/default',
                    sha2,
                    b'^branch/other']) == ({sha1, sha2}, {sha2})
    assert resolve([b'^branch/default',
                    sha2,
                    b'branch/other']) == ({sha2}, {sha1})
    assert resolve([sha2,
                    b'^branch/default',
                    b'branch/other']) == ({sha2}, {sha1})

    # cases with the `ALL` pseudo ref (stops further resolution and supersedes
    # all previously done ones)
    assert resolve([b'ALL']) == (ALL_CHANGESETS, empty)
    assert resolve([b'ALL',
                    b'branch/other']) == (ALL_CHANGESETS, empty)
    assert resolve([b'branch/default',
                    b'ALL',
                    b'^branch/other']) == (ALL_CHANGESETS, {sha2})
    assert resolve([b'^branch/default',
                    b'ALL',
                    b'branch/other']) == (ALL_CHANGESETS, {sha1})
    assert resolve([b'ALL',
                    b'^branch/default',
                    b'branch/other']) == (ALL_CHANGESETS, {sha1})
    assert resolve([b'ALL',
                    b'unknown']) == (ALL_CHANGESETS, empty)

    # cases of raising because of unknown revision
    with pytest.raises(RevisionNotFound) as exc_info:
        resolve([b'unknown', b'branch/default'])
    assert exc_info.value.args == (b'unknown', )
    with pytest.raises(RevisionNotFound) as exc_info:
        resolve([sha1, b'unknown'])
    assert exc_info.value.args == (b'unknown', )
    with pytest.raises(RevisionNotFound) as exc_info:
        resolve([sha1, b'^unknown'])
    assert exc_info.value.args == (b'unknown', )

    # cases ignoring unknown revision
    assert resolve([b'unknown',
                    b'branch/default'
                    ],
                   ignore_unknown=True) == ({sha1}, empty)
    assert resolve([b'unknown',
                    b'^branch/default'
                    ],
                   ignore_unknown=True) == (empty, {sha1})
    assert resolve([b'^unknown',
                    b'branch/default'
                    ],
                   ignore_unknown=True) == ({sha1}, empty)
