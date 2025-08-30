# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from multiprocessing import Process, Pipe
from pathlib import Path
import random
import shutil
import signal
import uuid

import warnings

from mercurial import (
    error,
    hg,
)
from mercurial.merge import merge
from mercurial.node import nullrev as NULL_REVISION
from hgext3rd.heptapod.branch import set_default_gitlab_branch

import pytest
from pytest_cov.embed import cleanup_on_signal

from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from ..identification import INCARNATION_ID
from ..testing.multiprocessing import assert_recv
from ..workdir import (
    ROSTER_FILE_NAME,
    ROSTER_VERSION_LINE,
    WorkingDirectory,
    WorkingDirectoryError,
    locked_roster,
    roster_iter,
    roster_iter_v2,
    wd_path,
    release_workdir,
    remove_all_workdirs,
    reserve_workdir,
    working_directory,
    workdirs_gc,
    remove_unlisted_workdirs,
)

parametrize = pytest.mark.parametrize

CLIENT_ID = str(uuid.uuid4())


@pytest.fixture
def wd_fixture(tmpdir):
    """Shared fixture for working directories tests

    the first object is the `Path` to the working directories root.
    The second object is the wrapper for a freshly created, empty,
    repository.
    """
    workdirs_root = Path(tmpdir / 'working-directories')
    wrapper = LocalRepoWrapper.init(tmpdir / 'repo',
                                    config=dict(
                                     extensions=dict(topic='', evolve=''),
                                    ))
    yield workdirs_root, wrapper


def assert_roster_length(repo, n):
    """Check the number of lines *after* the version line in the roster."""
    with repo.vfs(ROSTER_FILE_NAME, b'rb') as rosterf:
        assert len(rosterf.readlines()) == n + 1


def test_working_directory_basic(wd_fixture):
    wds_root, wrapper = wd_fixture
    src_repo = wrapper.repo

    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID) as wd:
        wd_path = wd.path
        wd_id = wd.id
        # caller would typically use `wd.repo`, yet not necessarily
        wd_wrapper = LocalRepoWrapper.load(wd.path)
        sha = wd_wrapper.commit_file('foo').hex()

    # The commit done in the temporary working directory is visbile from
    # the main repository.
    wrapper.reload()

    ctx = src_repo[sha]
    assert ctx.hex() == sha

    # Simple reuse, with an error in usage
    try:
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID) as wd:
            assert wd.path == wd_path
            raised = RuntimeError("Workdir tests error")
            raise raised
    except RuntimeError as caught:
        assert caught is raised

    # The working dir has been released despite of the RuntimeError,
    # we can use it again
    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=ctx) as wd:
        assert wd.path == wd_path
        wd_wrapper = LocalRepoWrapper.load(wd.path)
        assert wd_wrapper.repo[sha].branch() == b'default'

    # Two working directories for the same branch
    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=ctx) as wd1:
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=ctx) as wd2:
            assert wd1.path == wd_path
            assert wd2.path != wd_path
            wd2_path = wd2.path
            wd2_id = wd2.id

    # We now have two available working directories for the default branch
    with src_repo.vfs(ROSTER_FILE_NAME, b'rb') as rosterf:
        wds = {wd_id: branch
               for (wd_id, _, _, branch), _l in roster_iter(rosterf)}
    assert wds == {wd_id: b'default', wd2_id: b'default'}

    # And the roster file has the expected size
    assert_roster_length(src_repo, 2)

    # Both can be reused
    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=ctx) as wd1:
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=ctx) as wd2:
            assert set((wd1.path, wd2.path)) == {wd_path, wd2_path}

    # with no undue growth of the roster file (hgitaly#226)
    assert_roster_length(src_repo, 2)


def test_working_directory_roster_v1(wd_fixture):
    wds_root, wrapper = wd_fixture
    src_repo = wrapper.repo

    cs_default = wrapper.commit_file('foo')
    cs_other = wrapper.commit_file('bar', branch='other')

    # using the current logic to actually create working directories
    for changeset in (cs_default, cs_other):
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=changeset):
            pass

    # overwrite the roster with v1 data:
    # - no version line,
    # - each line has just a pid or '-' instead of Client and Incarnation IDs
    with locked_roster(wrapper.repo) as (inf, outf):
        outf.seek(0)  # version line has already been written, overwrite it
        outf.writelines((b"0 123456 10000 default\n",
                         b"1 - 10000 other\n",
                         ))

    # reservation works
    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_default) as wd:
        assert wd.id == 0

    # roster file has been converted
    with wrapper.repo.vfs(ROSTER_FILE_NAME, b'rb') as rosterf:
        assert rosterf.read(4) == b'002\n'
        wds = {
            wd_id: branch
            for (wd_id, _cl, _ts, branch), _line in roster_iter_v2(rosterf)
        }
        assert wds == {0: b'default', 1: b'other'}

    # reservation for the 'other' branch also works
    with working_directory(wds_root, src_repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_other) as wd:
        assert wd.id == 1


def test_roster_file_unknown_version(wd_fixture):
    wrapper = wd_fixture[1]

    with locked_roster(wrapper.repo) as (inf, outf):
        outf.seek(0)  # version line has already been written, overwrite it
        outf.write(b"999\n")

    with wrapper.repo.vfs(ROSTER_FILE_NAME, b'rb') as rosterf:
        with pytest.raises(RuntimeError) as exc_info:
            next(roster_iter(rosterf))
        assert '999' in exc_info.value.args[0]


def test_working_directory_subrepos(wd_fixture):
    wds_root, wrapper = wd_fixture
    src_repo = wrapper.repo
    nested_path = wrapper.path / 'nested'
    nested = LocalRepoWrapper.init(nested_path)
    nested.write_commit("bar", content="in nested")

    wrapper.path.join('.hgsub').write("nested = nested")
    wrapper.command(b'add', subrepos=True)
    wrapper.command(b'commit', subrepos=True, message=b"invalid")
    changeset = wrapper.repo[b'tip']

    (wrapper.path / '.hg/hgrc').write('\n'.join((
        '[extensions]',
        'heptapod=',
        ''
        )))
    wrapper.reload()

    src_repo = wrapper.repo
    # perhaps one day there will not be an error any more, check
    # heptapod#310 and heptapod#1287
    with pytest.raises(WorkingDirectoryError) as exc_info:
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=changeset):
            pass
    assert exc_info.value.args[0] == 'update'


@parametrize('stage', ('create', 'load', 'update'))
def test_working_directory_errors(wd_fixture, monkeypatch, stage):
    def raiser(*a, **kw):
        raise error.Abort(b"test-wd")

    wds_root, wrapper = wd_fixture
    src_repo = wrapper.repo
    ctx = wrapper.commit_file('foo')

    if stage == 'load':
        with working_directory(wds_root, src_repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=ctx):
            pass
        monkeypatch.setattr(hg, 'repository', raiser)
    elif stage == 'create':
        monkeypatch.setattr(hg, 'share', raiser)
    elif stage == 'update':
        monkeypatch.setattr(WorkingDirectory, 'uncaught_update', raiser)

    with pytest.raises(WorkingDirectoryError) as exc_info:
        with working_directory(wds_root, wrapper.repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=ctx):
            pass
    assert exc_info.value.args[0] == stage
    assert exc_info.value.args[1].args[0] == b'test-wd'


def test_working_directory_branches(wd_fixture):
    wds_root, wrapper = wd_fixture
    src_repo = wrapper.repo

    cs_default = wrapper.commit_file('foo')
    cs_topic = wrapper.commit_file('bar', content="top bar", topic='zetop')
    cs_other = wrapper.commit_file('branch', branch='other', parent=cs_default)

    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_topic) as wd:
        default_wd_id = wd.id

        wctx = wd.repo[None]
        assert wctx.p1() == cs_topic
        assert wctx.branch() == b'default'
        assert wctx.topic() == b'zetop'

        assert (wd.path / 'foo').exists()
        assert (wd.path / 'bar').exists()

    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_other) as wd:
        assert wd.id != default_wd_id
        other_wd_id = wd.id

        wctx = wd.repo[None]
        assert wctx.p1() == cs_other
        assert wctx.branch() == b'other'
        assert not wctx.topic()

        assert (wd.path / 'foo').exists()
        assert (wd.path / 'branch').exists()
        assert not (wd.path / 'bar').exists()

        other_wd_path = wd.path

    with src_repo.vfs(ROSTER_FILE_NAME, b'rb') as rosterf:
        wds = {wd_id: branch
               for (wd_id, _, _, branch), _l in roster_iter(rosterf)}

    assert wds == {default_wd_id: b'default', other_wd_id: b'other'}

    # If the working directory is missing despite being listed, it is not
    # an issue. Could happen with restore from backup (although we should
    # simply not backup the roster file) or be accidental.
    shutil.rmtree(other_wd_path)
    assert not other_wd_path.exists()

    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_other) as wd:
        assert wd.id == other_wd_id
        assert wd.path == other_wd_path

    # Working directories are reused regardless of topic
    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_default) as wd:
        assert wd.id == default_wd_id

        wctx = wd.repo[None]
        assert wctx.p1() == cs_default
        assert wctx.branch() == b'default'
        assert not wctx.topic()

        # testing purge/clean update
        (wd.path / 'bar').write_bytes(b"Some conflicting unversioned content")

    # Even with conflicting unversioned file, a clean working directory is
    # provided on next usage
    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_topic) as wd:
        assert wd.id == default_wd_id

        wctx = wd.repo[None]
        assert wctx.p1() == cs_topic

        assert (wd.path / 'bar').read_bytes() == b"top bar"

        # Acquire Mercurial's wlock, but doesn't release it, as would happen
        # on SIGKILL. It is essential for the test to be meaningful to keep
        # a reference to the lock.
        wlock = wd.repo.wlock()

    # Working directory locks are broken on entering if needed.
    # This would block otherwise, due to the update to the given changeset:
    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_default) as wd:
        assert wd.id == default_wd_id

    # Ironically, there's a warning to use `wlock.release` instead of `del`
    # to release a lock, which is not exactly why we delete it (mostly keeping
    # flake8 happy with this test code).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        del wlock

    # working directories on obsolete changesets are legitimate
    wrapper.update_bin(cs_topic.node())
    wrapper.amend_file('bar', content="new_bar")

    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_topic) as wd:
        assert wd.id == default_wd_id

        wctx = wd.repo[None]
        parent_cs = wctx.p1()
        assert parent_cs == cs_topic
        assert parent_cs.obsolete()


@parametrize('merge_result', ('conflict', 'mergeable'))
def test_working_directory_merge(wd_fixture, merge_result):
    wds_root, wrapper = wd_fixture
    commit_file = wrapper.commit_file
    conflict = merge_result == 'conflict'

    # a simple merge setup with a conflicting topic and a non-conflicting one
    ctx0 = commit_file('foo')
    cs_default = commit_file('foo', content="default")
    topic_file = 'foo' if conflict else 'bar'
    cs_topic = commit_file(topic_file, parent=ctx0, topic='top', content="top")

    # leaving merge result in a working directory
    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_default) as wd:
        default_wd_id = wd.id
        stats = merge(wd.repo[cs_topic.rev()])
        if conflict:
            assert stats.unresolvedcount > 0

    # re-acquisition cleans up remnants
    with working_directory(wds_root, wrapper.repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=cs_default) as wd:
        assert wd.id == default_wd_id

        wctx = wd.repo[None]
        assert wctx.p1() == cs_default
        assert wctx.p2().rev() == NULL_REVISION
        # TODO clean status (provide in mercurial_testhelpers)


@pytest.fixture
def purge_fixture(wd_fixture):
    wds_root, wrapper = wd_fixture
    repo = wrapper.repo
    # using a custom default branch to illustrate that 'default' is not
    # hardcoded
    wrapper.commit_file('foo', branch='mydefault')
    set_default_gitlab_branch(repo, b'branch/mydefault')

    return wd_fixture


def test_workdirs_gc_active_default(purge_fixture):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # no error if there is no working directory
    workdirs_gc(wds_root, repo, 1)

    wd_path(wds_root, 1).mkdir(parents=True)
    wd_path(wds_root, 2).mkdir()
    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 client-id 10 10000 mydefault\n",
                         b"1 - - 10000 other\n",
                         b"2 - - 10000 mydefault\n",
                         ))

    workdirs_gc(wds_root, repo, max_age_seconds=100, now=11000)

    # The active work dir for default branch is kept, considered to be enough
    with locked_roster(repo) as (inf, outf):
        lines = inf.readlines()
        assert lines == [b"002\n", b"0 client-id 10 10000 mydefault\n"]


def test_workdirs_gc_stale_default(purge_fixture):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # no error if there is no working directory
    workdirs_gc(wds_root, repo, 1)

    wd_path(wds_root, 0).mkdir(parents=True)
    wd_path(wds_root, 2).mkdir()
    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 - - 10000 mydefault\n",
                         b"2 - - 15000 mydefault\n",
                         ))

    workdirs_gc(wds_root, repo, max_age_seconds=100, now=20000)

    # The active work dir for default branch is kept, considered to be enough
    with locked_roster(repo) as (inf, outf):
        lines = [parsed for parsed, _line in roster_iter(inf)]
        assert len(lines) == 1
        assert lines[0][3] == b'mydefault'


@parametrize('outdated', ('outdated', 'not-outdated'))
def test_workdirs_gc_duplicate_lines(purge_fixture, outdated):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo
    is_outdated = outdated == 'outdated'

    # no error if there is no working directory
    workdirs_gc(wds_root, repo, 1)

    wd_path(wds_root, 0).mkdir(parents=True)
    wd_path(wds_root, 1).mkdir()
    with locked_roster(repo) as (inf, outf):
        # See hgitaly#226
        outf.writelines((b"0 - - 10000 mydefault\n",
                         b"1 - - 11000 mydefault\n",
                         b"0 - - 12000 mydefault\n",
                         b"1 - - 13000 mydefault\n",
                         ))

    max_age = 100 if is_outdated else 10000
    workdirs_gc(wds_root, repo, max_age_seconds=max_age, now=20000)

    # The active work dir for default branch is kept, considered to be enough
    with locked_roster(repo) as (inf, outf):
        lines = [parsed for parsed, _line in roster_iter(inf)]
        assert len(lines) == 1 if is_outdated else 2
        for line in lines:
            assert line[3] == b'mydefault'


def test_workdirs_gc_no_default(purge_fixture):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # no error if there is no working directory
    workdirs_gc(wds_root, repo, 1)

    wd_path(wds_root, 0).mkdir(parents=True)
    wd_path(wds_root, 1).mkdir()
    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 - - 10000 other\n",
                         b"1 - - 15000 another\n",
                         ))

    workdirs_gc(wds_root, repo, max_age_seconds=100, now=20000)

    # The active work dir for default branch is kept, considered to be enough
    with locked_roster(repo) as (inf, outf):
        assert len(inf.read()) == 4  # just the version line


def test_workdirs_gc_missing_workdir(purge_fixture):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # no error if there is no working directory
    workdirs_gc(wds_root, repo, 1)

    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 - - 10000 other\n",
                         b"1 - - 15000 mydefault\n",
                         ))

    workdirs_gc(wds_root, repo, max_age_seconds=100, now=20000)

    with locked_roster(repo) as (inf, outf):
        wds = {parsed[0]: parsed[3] for parsed, _line in roster_iter(inf)}
        assert wds == {1: b'mydefault'}


def test_workdirs_gc_rmerror(purge_fixture, monkeypatch):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    wd_path(wds_root, 0).mkdir(parents=True)
    wd_path(wds_root, 1).mkdir()
    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 - - 10000 other\n",
                         b"1 - - 15000 mydefault\n",
                         ))

    def raiser(path):
        raise RuntimeError(f"Cannot remove {path}")

    monkeypatch.setattr(shutil, 'rmtree', raiser)
    workdirs_gc(wds_root, repo, max_age_seconds=100, now=20000)

    with locked_roster(repo) as (inf, outf):
        wds = {parsed[0]: parsed[3] for parsed, _line in roster_iter(inf)}
        assert wds == {0: b'other', 1: b'mydefault'}


def test_remove_unlisted_workdirs(purge_fixture, monkeypatch):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # does not fail if working dirs root does not even exist
    remove_unlisted_workdirs(wds_root, repo)

    wd_path(wds_root, 0).mkdir(parents=True)
    wd_path(wds_root, 1).mkdir()
    wd_path(wds_root, 2).mkdir()
    (wds_root / 'README').write_bytes(b"innocent bystander")
    (wds_root / '4').write_bytes(b"innocent asking for trouble")

    with locked_roster(repo) as (inf, outf):
        outf.writelines((b"0 - - 10000 mydefault\n",
                         ))
    rmtree = shutil.rmtree

    def raiser(path):
        if path.name == '1':
            rmtree(path)
        else:
            raise RuntimeError(f"Cannot remove {path}")

    monkeypatch.setattr(shutil, 'rmtree', raiser)
    remove_unlisted_workdirs(wds_root, repo)

    with locked_roster(repo) as (inf, outf):
        wds = {parsed[0]: parsed[3] for parsed, _line in roster_iter(inf)}
        assert wds == {0: b'mydefault'}

    assert not wd_path(wds_root, 1).exists()
    assert wd_path(wds_root, 2).exists()  # our raiser did its job
    assert (wds_root / 'README').exists()
    assert (wds_root / '4').exists()


@parametrize('inner_success', ('ok', 'rm-error'))
def test_remove_all_workdirs(purge_fixture, monkeypatch, inner_success):
    wds_root, wrapper = purge_fixture
    repo = wrapper.repo

    # acquiring like ordinary caller should
    with working_directory(wds_root, repo,
                           client_id=CLIENT_ID,
                           incarnation_id=INCARNATION_ID,
                           changeset=repo[0]) as wd:
        assert wd.path.exists()

    assert_roster_length(repo, 1)  # for comparison with after

    if inner_success == 'rm-error':
        def raiser(*args):
            raise RuntimeError(*args)

        monkeypatch.setattr(shutil, 'rmtree', raiser)

    remove_all_workdirs(wds_root, repo)

    if inner_success == 'ok':
        assert not wd.path.exists()
        assert not wds_root.exists()

    assert_roster_length(repo, 0)


ROSTER_LOCK_TIMEOUT = 0.1
ROSTER_LOCK_ATTEMPTS_DELAY = ROSTER_LOCK_TIMEOUT / 10


def locking_subpro(repo_path, conn):
    """Subprocess taking the roster lock and then taking commands from a pipe.

    The lock is taken at startup after sending the initial message and
    is held until the 'shutdown' message is received
    """
    cleanup_on_signal(signal.SIGTERM)
    cleanup_on_signal(signal.SIGINT)
    from hgitaly import procutil
    procutil.IS_CHILD_PROCESS = True

    repo = LocalRepoWrapper.load(repo_path).repo
    conn.send('started')
    try:
        with locked_roster(repo, timeout=ROSTER_LOCK_TIMEOUT) as (inf, outf):
            conn.send('locked')
            while True:
                msg = conn.recv()
                if msg == 'shutdown':
                    conn.send('bye')
                    conn.close()
                    return
                if isinstance(msg, tuple) and msg[0] == 'write':
                    outf.write(msg[1].encode('utf8'))
                    # atomictempfile does not implement flush
                    conn.send('written')
                if msg == 'read':
                    if inf is None:
                        conn.send(None)
                    else:
                        pos = inf.tell()
                        inf.seek(0)
                        content = inf.read()
                        assert content.startswith(ROSTER_VERSION_LINE)
                        content = content[len(ROSTER_VERSION_LINE):]
                        conn.send(content.decode('utf8'))
                        inf.seek(pos)
    except error.LockHeld:
        conn.send('timeout')


@parametrize('lock_attempts', (1, 4))
def test_locked_roster(wd_fixture, lock_attempts):
    wrapper = wd_fixture[1]
    repo_path = wrapper.path

    pipe1, child_pipe1 = Pipe()
    pipe2, child_pipe2 = Pipe()
    pipe3, child_pipe3 = Pipe()
    pipe4, child_pipe4 = Pipe()
    proc1 = Process(target=locking_subpro, args=(repo_path, child_pipe1))
    proc2 = Process(target=locking_subpro, args=(repo_path, child_pipe2))
    proc3 = Process(target=locking_subpro, args=(repo_path, child_pipe3))
    proc4 = Process(target=locking_subpro, args=(repo_path, child_pipe4))
    procs = [proc1, proc2, proc3, proc4]

    try:
        # proc1 starts, write a line, but does not see it in its input file
        # (atomicity)
        proc1.start()
        assert_recv(pipe1, 'started')
        assert_recv(pipe1, 'locked')
        pipe1.send(('write', 'content1'))
        assert_recv(pipe1, 'written')
        pipe1.send('read')
        assert_recv(pipe1, None)

        # proc2 starts but cannot acquire the lock yet
        proc2.start()
        assert_recv(pipe2, 'started')
        assert not pipe2.poll(
            timeout=ROSTER_LOCK_ATTEMPTS_DELAY * lock_attempts)

        # shutting down proc1
        pipe1.send('shutdown')
        assert_recv(pipe1, 'bye')
        proc1.join()

        # now that proc1 has released the lock, proc2 acquires it and sees the
        # write done by proc1
        assert_recv(pipe2, 'locked')
        pipe2.send('read')
        assert_recv(pipe2, 'content1')

        # proc2 overwrites the file, but does not see the change yet in its
        # input stream
        pipe2.send(('write', 'content2'))
        assert_recv(pipe2, 'written')
        pipe2.send('read')
        assert_recv(pipe2, 'content1')

        # proc3 starts, cannot acquire the lock immediately either
        proc3.start()
        assert_recv(pipe3, 'started')
        assert not pipe3.poll(timeout=ROSTER_LOCK_ATTEMPTS_DELAY)

        # after proc2 shutdown, proc3 sees the new content
        pipe2.send('shutdown')
        assert_recv(pipe2, 'bye')
        proc2.join()
        assert_recv(pipe3, 'locked')
        pipe3.send('read')
        assert_recv(pipe3, 'content2')

        # proc4 starts but proc3 does not release the lock in time
        proc4.start()
        assert_recv(pipe4, 'started')
        assert_recv(pipe4, 'timeout')

        pipe3.send('shutdown')
        assert_recv(pipe3, 'bye')
    finally:
        # avoid blocking the test run if there are errors
        for proc in procs:
            if proc.is_alive():
                proc.terminate()
                proc.join()


def test_roster_lock_breaking(wd_fixture):
    wrapper = wd_fixture[1]
    repo_path = wrapper.path

    pipe1, child_pipe1 = Pipe()
    pipe2, child_pipe2 = Pipe()
    proc1 = Process(target=locking_subpro, args=(repo_path, child_pipe1))
    proc2 = Process(target=locking_subpro, args=(repo_path, child_pipe2))
    procs = [proc1, proc2]

    # let's grab the lock from the main tests process, which is not allowed
    # to take it, as it is not one of the HGitaly worker processes. This
    # simulates the case where the PID has been reused: there *is* a process
    # with that pid.
    try:
        with locked_roster(wrapper.repo) as (inf, outf):
            # proc1 takes the lock, ignoring the lock held with an invalid PID
            proc1.start()
            assert_recv(pipe1, 'started')
            assert_recv(pipe1, 'locked')
            pipe1.send(('write', 'content1'))
            assert_recv(pipe1, 'written')

            # of course the lock taken by proc1 blocks proc2
            # Note that exiting normally the `locked_roster` context manager
            # of the main process would release the lock, even if held by
            # proc1, which looks bad, but is irrelevant: in actual operation,
            # roster locks have to be broken if the holding process have died
            # abruptly enough not to have been able to release the lock.
            proc2.start()
            assert_recv(pipe2, 'started')
            assert not pipe2.poll(timeout=ROSTER_LOCK_ATTEMPTS_DELAY)

            # shutting down proc1
            pipe1.send('shutdown')
            assert_recv(pipe1, 'bye')
            proc1.join()

            # now that proc1 has released the lock, proc2 acquires it
            # and sees the write done by proc1
            assert_recv(pipe2, 'locked')
            pipe2.send('read')
            assert_recv(pipe2, 'content1')
    finally:
        # avoid blocking the test run if there are errors
        for proc in procs:
            if proc.is_alive():
                proc.terminate()
                proc.join()


def reserving_subpro(wds_root, repo_path, incarnation_id, conn):
    cleanup_on_signal(signal.SIGTERM)
    cleanup_on_signal(signal.SIGINT)
    repo = LocalRepoWrapper.load(repo_path).repo
    from hgitaly import procutil
    conn.send('started')

    while True:
        msg = conn.recv()
        if msg == 'shutdown':
            conn.send('bye')
            conn.close()
            return

        if msg == 'attach':
            procutil.IS_CHILD_PROCESS = True
            conn.send('service-child')
        if msg == 'detach':
            procutil.IS_CHILD_PROCESS = False
            conn.send('mono-process')
        if msg == 'reserve':
            wd = reserve_workdir(wds_root, repo.ui, repo, b'default',
                                 client_id=CLIENT_ID,
                                 incarnation_id=incarnation_id)
            conn.send(wd.id)
        if msg == 'release':
            release_workdir(repo, wd)
            conn.send('released')


def test_release_workdir_old_incarnation(wd_fixture):
    """Reservations by previous client incarnations have to be ignored."""
    wds_root, wrapper = wd_fixture
    repo_path = wrapper.path

    pipe1, child_pipe1 = Pipe()
    pipe2, child_pipe2 = Pipe()
    pipe3, child_pipe3 = Pipe()

    incarnations = [str(random.randint(0, 1 << 32)) for _ in range(2)]

    proc1 = Process(target=reserving_subpro,
                    args=(wds_root, repo_path, incarnations[0], child_pipe1))
    proc2 = Process(target=reserving_subpro,
                    args=(wds_root, repo_path, incarnations[1], child_pipe2))
    proc3 = Process(target=reserving_subpro,
                    args=(wds_root, repo_path, incarnations[1], child_pipe3))
    procs = [proc1, proc2, proc3]
    try:
        # 1st scenario: working directory reserved with a former incarnation
        #
        # proc1 makes a wd, then dies before it could release it
        # proc2, having a different incarnation id, overrides the reservation.
        proc1.start()
        assert_recv(pipe1, 'started')
        pipe1.send('attach')
        assert_recv(pipe1, 'service-child')
        pipe1.send('reserve')
        assert pipe1.poll(timeout=2)
        wd_id = pipe1.recv()
        # shutdown message would *currently* be enough to get the wished stale
        # workdir, but killing the subprocess makes sure the test will
        # not become tautological if there are changes later on
        proc1.kill()
        proc1.join()

        proc2.start()
        assert_recv(pipe2, 'started')
        pipe2.send('attach')
        assert_recv(pipe2, 'service-child')
        pipe2.send('reserve')
        assert_recv(pipe2, wd_id)

        # 2nd scenario: working directory reserved (by proc2), then proc3
        # requests a wd. Having the same incarnation_id as proc2, it is
        # handed a fresh one.
        proc3.start()
        assert_recv(pipe3, 'started')
        pipe3.send('attach')
        assert_recv(pipe3, 'service-child')
        pipe3.send('reserve')
        assert pipe3.poll(timeout=2)
        assert pipe3.recv() != wd_id

        # Normal shutdowns for the two running processes
        pipe2.send('release')
        pipe2.send('shutdown')
        proc2.join()
        pipe3.send('release')
        pipe3.send('shutdown')
        proc3.join()
    finally:
        # avoid blocking the test run if there are errors
        for proc in procs:
            if proc.is_alive():
                proc.terminate()
                proc.join()
