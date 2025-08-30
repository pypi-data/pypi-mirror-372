# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
import attr
import errno
import logging
import os
from pathlib import Path
import shutil
import time
from typing import Any
import weakref

from mercurial import (
    cmdutil,
    commands,
    error,
    hg,
    lock,
)
from mercurial.repoview import _filteredrepotypes

from .identification import CLIENT_ID, INCARNATION_ID
from .procutil import is_current_service_process
from .revision import gitlab_revision_changeset

logger = logging.getLogger(__name__)

ROSTER_FILE_NAME = b'hgitaly-working-dirs'
ROSTER_LOCK_NAME = ROSTER_FILE_NAME + b'.lock'
ROSTER_FILE_VERSION = 2
ROSTER_VERSION_LINE = b'%03d\n' % ROSTER_FILE_VERSION


def clear_repo_class(repo_class):
    _filteredrepotypes.pop(repo_class, None)


def wd_path(per_repo_root, wd_id):
    return Path(f'{per_repo_root}/{wd_id}')


class WorkingDirectoryError(RuntimeError):
    """Represent an error obtaining a working directory.

    The first argument is the type of action, currently one of
    ``(load, create, update)``.
    The second argument is the original exception
    """


@attr.define
class WorkingDirectory:
    """Represents a semi-permanent working directory."""
    id: int
    branch: bytes
    path: Path
    repo: Any = attr.field(repr=False, default=None)

    def roster_line(self, client_id, incarnation_id, timestamp=None):
        """Return a line suitable to put in the roster file.

        :param pid: use ``None`` to give back the working directory to the
          pool, current process id to reserve it.
        :return: bytes, since this is to write in files managed by Mercurial's
         vfs, with end of line included, suitable for use in ``writelines``
         and ``write`` methods.
        """
        if timestamp is None:
            timestamp = int(time.time())

        if client_id is None:
            client_id = incarnation_id = '-'

        return (b'%d %s %s %d %s\n' % (self.id,
                                       client_id.encode('ascii'),
                                       incarnation_id.encode('ascii'),
                                       timestamp, self.branch))

    def load_or_create(self, ui, src_repo):
        path_bytes = bytes(self.path)
        if self.path.exists():
            try:
                self.init_repo(hg.repository(ui, path_bytes))
            except error.Abort as exc:
                raise WorkingDirectoryError('load', exc)
        else:
            try:
                self.init_repo(hg.share(ui, src_repo.root, path_bytes,
                                        update=False))
            except error.Abort as exc:
                raise WorkingDirectoryError('create', exc)

    def command(self, name, *args, hidden=False, **kwargs):
        cmd = cmdutil.findcmd(name, commands.table)[1][0]
        repo = self.repo
        if hidden:
            repo = repo.unfiltered()
        return cmd(repo.ui, repo, *args, **kwargs)

    def clean_update(self, target_rev):
        try:
            self.uncaught_update(target_rev, clean=True, hidden=True)
        except error.Abort as exc:
            raise WorkingDirectoryError('update', exc)

    def uncaught_update(self, target_rev, **kw):
        self.command(b'update', target_rev, **kw)

    def purge(self):
        self.command(b'purge', all=True, hidden=True, confirm=False)

    def init_repo(self, repo):
        weakref.finalize(repo, clear_repo_class, repo.unfiltered().__class__)
        self.repo = repo
        # any existing wlock is lingering, since the whole point of
        # this module is to provide a higher level locking system
        repo.vfs.tryunlink(b'wlock')

    def file_path(self, relative_path):
        return os.path.join(bytes(self.path), relative_path)


@contextmanager
def working_directory(workdirs_root, repo, *args, **kwargs):
    """Context manager for temporary working directories

    Entering this context manager, (typically with the ``with`` statement
    yields a clean working directory for the given repository, cleanly updated
    at the specified changeset.

    The working directory is represented by a :class:`WorkingDirectory`
    instance and is guaranteed to be for exclusive use by the caller.
    It is relturned to the underlying pool when exiting the context.

    The changeset Mercurial branch is used as a heuristic for reuse: it
    is assumed that a working directory previously updated to a changeset
    with the same branch can be quickly updated to the given one.

    The given changeset can be obsolete, allowing to revive it with more than
    a simple `hg touch` equivalent. It is therefore up to the caller to
    check for obsolescence if undesireable (e.g., in mergeability checks).

    :param workdirs_root: path to the directory where working directories
      for the given repo are kept.
    :param repo: Mercurial repository object
    :param changeset: a :class:`changectx` instance. Use `None` to get an
      empty working directory. It will in this case be considered to be for
      the ``default`` branch. This should be used only in the case of
      empty repositories.
    """

    wd = reserve_prepare_workdir(workdirs_root, repo, *args, **kwargs)
    try:
        yield wd
    finally:
        release_workdir(repo, wd)


def reserve_prepare_workdir(workdirs_root, repo,
                            client_id, incarnation_id,
                            changeset=None):
    branch = b'default' if changeset is None else changeset.branch()
    wd = reserve_workdir(workdirs_root, repo.ui, repo, branch,
                         client_id=client_id,
                         incarnation_id=incarnation_id)
    wd.load_or_create(repo.ui, repo)
    wd.purge()
    if changeset is not None:
        wd.clean_update(changeset.hex())
    return wd


class rosterlock(lock.lock):

    def _lockshouldbebroken(self, locker):
        pid = int(locker.split(b":", 1)[-1].decode('ascii').strip())
        return not is_current_service_process(pid)


def trylock(ui, vfs, lockname, timeout, warntimeout, *args, step=0.1,
            **kwargs):
    """return an acquired lock or raise an a LockHeld exception

    This function is responsible to issue logs about
    the held lock while trying to acquires it.

    Derived from Mercurial's `lock.trylock`, with these differences:

    - using :data:`logger`
    - using :class:`rosterlock`
    - configurable sleep interval (param ``step``), both because roster
      file operations are designed to be fast, and to reach the warntimeout
      in tests without overlong sleeps.
    - timeouts always exist, since server operation must not be stalled
      forever.
    - `acquirefn` is ignored, as we don't need it for the roster lock.
    """

    def log(level, locker):
        """log the "waiting on lock" message through at the given level"""
        pid = locker.split(b":", 1)[-1].decode('ascii')
        logger.log(level, "waiting for lock on %r held by process %r",
                   lk.desc, pid)

    lk = rosterlock(vfs, lockname, 0, *args, dolock=False, **kwargs)

    debugidx = 0
    warningidx = int(warntimeout / step)

    delay = 0
    while True:
        try:
            lk._trylock()
            break
        except error.LockHeld as inst:
            if delay == debugidx:
                log(logging.DEBUG, inst.locker)
            if delay == warningidx:
                log(logging.WARNING, inst.locker)
            if timeout <= delay * step:
                raise error.LockHeld(
                    errno.ETIMEDOUT, inst.filename, lk.desc, inst.locker
                )
            time.sleep(step)
            delay += 1

    lk.delay = delay
    if delay:
        if 0 <= warningidx <= delay:
            logger.warning("got lock after %.2f seconds", delay * step)
        else:
            logger.debug("got lock after %.2f seconds", delay * step)

    return lk


@contextmanager
def locked_roster(repo, timeout=1):
    """Locked read/write access to the repo working directories roster file.

    This context manager provides a pair of open files.
    The first is to be used to read the roster, the second to write it,
    with atomic update occurring at the end of the context.

    The lock is not reentrant, which is good enough for this simple need of
    a very short-lived lock protecting both readind and writing.

    :param timeout: maximum time to wait until the roster lock is acquired.
      The default value is intended for production, tests will set it to
      shorter values.
    """
    vfs = repo.vfs
    # TODO Mercurial lock system does not allow to customize its breaking
    # logic, which is actually causing deadlocks in containers.
    # In HGitaly, we can have much more certainty because of the general
    # prerequisites that a HGitaly service (typically several processes)
    # has exclusive access to this resource.
    # This is more general than the working directories roster lock, but
    # it is dubious that HGitaly ever gets exclusive access to Mercurial
    # content (HTTP pushes could be handled if HGitaly eventually manages
    # the hgwebdir services, but SSH pushes would not).
    ui = repo.ui
    warntimeout = 3 * timeout / 10
    # internal config: ui.signal-safe-lock
    signalsafe = ui.configbool(b'ui', b'signal-safe-lock')

    with trylock(ui, vfs,
                 lockname=ROSTER_LOCK_NAME,
                 timeout=timeout,
                 warntimeout=warntimeout,
                 releasefn=None,
                 acquirefn=None,
                 desc=b'Working directories roster file for %s' % repo.root,
                 signalsafe=signalsafe,
                 step=timeout / 10,
                 ):
        try:
            inf = vfs(ROSTER_FILE_NAME, b'rb')
        except FileNotFoundError:
            inf = None

        with vfs(ROSTER_FILE_NAME, b'wb', atomictemp=True) as outf:
            outf.write(ROSTER_VERSION_LINE)
            try:
                yield inf, outf
            finally:
                if inf is not None:
                    inf.close()


def roster_iter(fobj):
    if fobj is None:
        return

    version_line = fobj.read(4)
    if not version_line.endswith(b'\n'):
        fobj.seek(0)
        yield from roster_iter_v1(fobj)
        return

    version = int(version_line)  # ignores left 0 padding, whitespace and EOL
    if version != ROSTER_FILE_VERSION:
        raise RuntimeError(f"Unknown roster file version {version}")

    yield from roster_iter_v2(fobj)


def roster_iter_v2(fobj):
    for line in fobj:
        (wd_id, client_id, incarnation_id,
         timestamp, wd_branch) = line.split(b' ', 4)
        if client_id == b'-':
            client = None
        else:
            client = (client_id.decode('ascii'),
                      incarnation_id.decode('ascii'))
        yield (int(wd_id), client, int(timestamp), wd_branch.strip()), line


def roster_iter_v1(fobj):
    """Interpret a version 1 roster file.

    Since we are running a later version, we are sure that HGitaly got
    restarted since last write, hence any existing reservation can be
    safely ignored (the processing using it has necessarily stopped).
    Knowledge about the working directory has to be kept, though.
    """
    for line in fobj:
        wd_id, _pid, timestamp, wd_branch = line.split(b' ', 3)
        wd_branch = wd_branch.strip()
        current_fmt_line = b'%s - - %s %s\n' % (wd_id, timestamp, wd_branch)
        yield (int(wd_id), None, int(timestamp), wd_branch), current_fmt_line


def roster_branch_match(fobj, branch, client_id, incarnation_id):
    matching = None
    max_id = - 1
    lines = []
    for (wd_id, client, _ts, wd_branch), line in roster_iter(fobj):
        if wd_id > max_id:
            max_id = wd_id
        if wd_branch == branch and matching is None:
            # if we are reserving on behalf of the same client with
            # a different incarnation, it means that the client has
            # restarted, hence any request done with the previous incarnation
            # is finished.
            if client is None or (client[0] == client_id
                                  and client[1] != incarnation_id):
                matching = wd_id
                continue
        lines.append(line)
    return matching, max_id + 1, lines


def reserve_workdir(workdirs_root, ui, repo, branch,
                    client_id, incarnation_id):
    with locked_roster(repo) as (rosterf, new_rosterf):
        matching_id, unused_id, other_lines = roster_branch_match(
            rosterf, branch,
            client_id, incarnation_id)
        wd_id = unused_id if matching_id is None else matching_id
        wd = WorkingDirectory(id=wd_id,
                              branch=branch,
                              path=wd_path(workdirs_root, wd_id),
                              )
        new_rosterf.writelines(other_lines)
        new_rosterf.write(wd.roster_line(client_id, incarnation_id))
    return wd


class ClientMismatch(ValueError):
    """Indicates that the Client ID was not as expected"""


def release_workdir_by_id(repo, wd_id, client_id):
    """Release a working directory specified by ID.

    For sanity / authorization, the provided Client ID is checked against
    the one in the roster file.
    """
    with locked_roster(repo) as (rosterf, new_rosterf):
        for (read_wd_id, client, _ts, branch), line in roster_iter(rosterf):
            if read_wd_id == wd_id:
                holder_id = client[0]
                if holder_id != client_id:
                    raise ClientMismatch(holder_id, client_id)

                wd = WorkingDirectory(id=wd_id, branch=branch, path=None)
                line = wd.roster_line(client_id=None, incarnation_id=None)
            new_rosterf.write(line)


def release_workdir(repo, wd):
    """Release a working directory object.

    No Client ID check is needed in this case, as the `WorkingDirectory`
    object is considered proof enough.
    """
    with locked_roster(repo) as (rosterf, new_rosterf):
        for parsed, line in roster_iter(rosterf):
            if parsed[0] == wd.id:
                line = wd.roster_line(client_id=None, incarnation_id=None)
            new_rosterf.write(line)


def workdirs_gc(workdirs_root, repo, max_age_seconds, now=None):
    """Purge working directories that have not been used for long.

    At least one working directory for the GitLab default branch is
    always kept.
    If later on we start seeding working directories from other working
    directories, even if branches differ (it could indeed be faster on
    average), then we might want to always keep at least one, just preferably
    for the default branch if possible.

    In case a removal fails, the corresponding roster line is kept for
    consistency, and so that subsequent allocation does not end in error
    (assuming the disk is working again anyway).

    :param max_age: time, in seconds since last time the working directory
       was used.
    :param now: current time in seconds since Unix epoch (should be used in
       tests only)
    """
    if now is None:
        now = time.time()

    # using gitlab_revision_changeset spares us the back-and-forth between
    # GitLab and Mercurial branches, with its special cases (topic…)
    head = gitlab_revision_changeset(repo, b'HEAD')
    default_branch = None if head is None else head.branch()
    default_branch_kept = False
    to_remove = {}
    to_keep = {}
    reserved_for_removal = []
    with locked_roster(repo) as (rosterf, new_rosterf):
        for (wd_id, pid, timestamp, branch), line in roster_iter(rosterf):
            if pid is None and now - timestamp > max_age_seconds:
                to_remove.setdefault(branch, {})[wd_id] = line
            else:
                to_keep[wd_id] = line
                if branch == default_branch:
                    default_branch_kept = True

        if not default_branch_kept:
            default_branch_to_rm = to_remove.get(default_branch)
            if default_branch_to_rm:
                # keep any of them
                wd_id = next(iter(default_branch_to_rm.keys()))
                to_keep[wd_id] = default_branch_to_rm.pop(wd_id)

        for branch, to_rm in to_remove.items():
            for wd_id, line in to_rm.items():
                wd = WorkingDirectory(id=wd_id,
                                      path=wd_path(workdirs_root, wd_id),
                                      branch=branch)
                new_rosterf.write(wd.roster_line(
                    client_id=CLIENT_ID,
                    incarnation_id=INCARNATION_ID))
                reserved_for_removal.append((wd, line))

        new_rosterf.writelines(to_keep.values())

    removed = set()
    to_restore = []
    for wd, orig_line in reserved_for_removal:
        if not wd.path.exists():
            removed.add(wd.id)
            continue

        try:
            shutil.rmtree(wd.path)
        except Exception:
            logger.exception("Failed to remove working directory '%s' "
                             "for repo at %r", wd.path, repo.root)
            # we put it back with the original timestamp so that removal
            # will be attempted back and either succeed or finally catch
            # some humans attention with the logged error.
            to_restore.append(line)
        else:
            removed.add(wd.id)

    with locked_roster(repo) as (rosterf, new_rosterf):
        for (wd_id, _pid, _ts, _branch), line in roster_iter(rosterf):
            if wd_id not in removed:
                new_rosterf.write(line)
        for line in to_restore:
            new_rosterf.write(line)


def remove_unlisted_workdirs(workdirs_root, repo):
    """Remove working directories that are present on disk but not registered.

    It's been seen in the wild (reason unclear, perhaps due to previously
    fixed bugs) and can take up lots of disk space. The symptoms would be
    a working directory sitting at its expected path, but not listed in the
    roster file, hence that will never be used.
    """
    if not workdirs_root.exists():
        return

    # first, reserve them so that they cannot enter use by accident
    stray_wds = []
    listed = set()
    with locked_roster(repo) as (rosterf, new_rosterf):
        for parsed, line in roster_iter(rosterf):
            listed.add(parsed[0])
            new_rosterf.write(line)

        for stray in os.listdir(workdirs_root):
            try:
                wd_id = int(stray)
            except ValueError:
                continue  # this is something else

            if wd_id in listed:
                continue

            stray_path = workdirs_root / stray
            if not stray_path.is_dir():
                continue

            wd = WorkingDirectory(id=wd_id,
                                  path=wd_path(workdirs_root, wd_id),
                                  branch=b'irrelevant')
            stray_wds.append(wd)
            new_rosterf.write(wd.roster_line(client_id=CLIENT_ID,
                                             incarnation_id=INCARNATION_ID))

    # remove them
    for wd in stray_wds:
        try:
            shutil.rmtree(wd.path)
        except Exception:
            # not much else we can do
            logger.error(
                "Could not remove stray working directory at '%s'" % wd.path)

    # produce the new roster. It is best not to simply release those that
    # we failed to remove, because it increases the odds that they could
    # be in use (since new workdirs always have a higher id than the existing
    # ones, chances are good that it would also be hgigher than the stray ones)
    stray_ids = {wd.id for wd in stray_wds}
    with locked_roster(repo) as (rosterf, new_rosterf):
        for (wd_id, _, _, _), line in roster_iter(rosterf):
            if wd_id not in stray_ids:
                new_rosterf.write(line)


def remove_all_workdirs(workdirs_root, repo):
    """Remove all workdirs for the given repository.

    This is to be used when preparing to remove the repository itself.
    """
    with locked_roster(repo) as (rosterf, new_rosterf):
        remove_all_workdirs_bare(workdirs_root)
        # new_rosterf being empty, this will void the existing one.


def remove_all_workdirs_bare(workdirs_root):
    """Removal of workdirs_root with no roster management.

    To be used either with roster being managed (lock acquired by caller etc.)
    or if the roster does not matter any more (repository is being entirely
    removed).

    Does not raise exceptions, as the caller typically will prefer to proceed
    with other cleanups if possible.
    """
    try:
        if os.path.exists(workdirs_root):
            shutil.rmtree(workdirs_root)
    except Exception:
        logger.exception("Failed to remove working directories at %r",
                         workdirs_root)
