# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
import gc
import logging
import os
from pathlib import Path
import time
import weakref

from grpc import StatusCode
from mercurial import (
    cmdutil,
    commands,
    error,
    hg,
    ui as uimod,
)
from mercurial.repoview import _filteredrepotypes

from .errors import ServiceError
from .identification import CLIENT_ID, INCARNATION_ID
from .logging import LoggerAdapter
from .workdir import working_directory
from .stub.shared_pb2 import (
    Repository,
)

GARBAGE_COLLECTING_RATE_GEN2 = 250
GARBAGE_COLLECTING_RATE_GEN1 = 20
AUX_GIT_REPOS_RELATIVE_DIR = "+hgitaly/hg-git"
HG_GIT_MIRRORING_MD_KEY = 'x-heptapod-hg-git-mirroring'
NATIVE_PROJECT_MD_KEY = 'x-heptapod-hg-native'
# TODO check if there is a GitLab MD for this, it should:
SKIP_HOOKS_MD_KEY = 'x-heptapod-skip-gl-hooks'
ACCEPT_MR_IID_KEY = 'x-heptapod-accept-mr-iid'
# TODO expose it in heptpod.wsgi and import it here
PY_HEPTAPOD_SKIP_HOOKS = b'HEPTAPOD_SKIP_ALL_GITLAB_HOOKS'
HEPTAPOD_PERMISSION_KEY = 'x-heptapod-perm'

logger = logging.getLogger(__name__)

USER_DATA_TO_ENVIRON = {
}
PROJECT_DATA_TO_ENVIRON = {
}

CONFIG_TO_FORWARD_IN_WORKING_DIRS = ((b'heptapod', b'no-git'),
                                     (b'heptapod', b'native'))


def clear_repo_class(repo_class):
    _filteredrepotypes.pop(repo_class, None)


repos_counter = 0


def gc_collect(generation):
    logger.info("A total of %d repository objects have been "
                "instantiated in this thread since startup. "
                "Garbage collecting (generation %d)",
                repos_counter, generation)
    start = time.time()
    gc_result = gc.collect(generation=generation)
    logger.info("Garbage collection (generation %d) "
                "done in %f seconds "
                "(%d unreachable objects). Current GC stats: %r",
                generation, time.time() - start, gc_result, gc.get_stats())


def normalize_rpath(gl_repo: Repository):
    rpath = gl_repo.relative_path
    if rpath.endswith('.git'):
        rpath = rpath[:-4] + '.hg'
    return rpath


class RepositoryCreationError(ServiceError):
    """Specific exception for creation problems."""


class HGitalyServicer:
    """Common features of all HGitaly services.

    Attributes:

    - :attr:`storages`: a :class:`dict` mapping storage names to corresponding
      root directory absolute paths, which are given as bytes since we'll have
      to convert paths to bytes anyway, which is the only promise a filesystem
      can make, and what Mercurial expects.
    - :attr:`ui`: base :class:`mercurial.ui.ui` instance from which repository
      uis are derived. In particular, it bears the common configuration.
    """

    STATUS_CODE_STORAGE_NOT_FOUND = StatusCode.NOT_FOUND
    STATUS_CODE_REPO_NOT_FOUND = StatusCode.NOT_FOUND
    STATUS_CODE_MISSING_REPO_ARG = StatusCode.INVALID_ARGUMENT

    def __init__(self, storages):
        self.storages = storages
        self.init_ui()

    def init_ui(self):
        """Prepare the base ``ui`` instance from which all will derive.

        See also :meth:`hgweb.__init__`
        """

        ui = self.ui = uimod.ui.load()
        # prevents `ui.interactive()` to crash (see heptapod#717)
        ui.setconfig(b'ui', b'nontty', b'true', b'hgitaly')

        # progress bars in stdout (log file at best) would be rather useless
        ui.setconfig(b'progress', b'disable', b'true', b'hgitaly')

        # other settings done in hgweb.__init__():
        #
        # - forcing file pattern resolution to be relative to root would be
        #   nice, but perhaps need more adaptation, and would have to be
        #   done in load_repo()
        # - `signal-safe-locks=no` worth being considered, but this not being
        #   WSGI, we control the server and its signal handling (see hgweb's
        #   comment)
        # - `report_unstrusted=off`: if some perms are unaligned, reporting
        #   the untrust could be the only lead for an obscure behaviour
        #   (typically ignoring some settings that can be critical to
        #   operation)

    def is_repo_aux_git(self, repository: Repository):
        if repository is None:
            return False
        return repository.relative_path.startswith(AUX_GIT_REPOS_RELATIVE_DIR)

    def load_repo(self, repository: Repository, context,
                  for_mutation_by=None,
                  ):
        """Load the repository from storage name and relative path

        :param repository: Repository Gitaly Message, encoding storage name
            and relative path
        :param context: gRPC context (used in error raising)
        :raises: ``KeyError('storage', storage_name)`` if storage is not found.

        Error treatment: the caller doesn't have to do anything specific,
        the status code and the details are already set in context, and these
        are automatically propagated to the client (see corresponding test
        in `test_servicer.py`). For specific error treatment, use
        :meth:`load_repo_inner` and catch the exceptions it raises.
        """
        try:
            repo = self.load_repo_inner(repository, context)
        except KeyError as exc:
            self.handle_key_error(context, exc.args)
        except ValueError as exc:
            self.handle_value_error(context, exc.args)

        if for_mutation_by is not None:
            if not for_mutation_by.gl_id:
                context.abort(StatusCode.INVALID_ARGUMENT, "empty User")
            self.add_mutation_metadata(grpc_repo=repository,
                                       user=for_mutation_by,
                                       ui=repo.ui,
                                       context=context)

        return repo

    def add_mutation_metadata(self, grpc_repo, user, context, ui):
        """Store metadata needed for mutation in repo environ.

        This is roughly the same job as heptapod.wsgi does.

        If we ever cache the repository objects, we will need to rerun this
        and/or reclone ``ui`` from a base config.
        """
        mirroring = native = skip_gl_hooks = False
        accept_mr_iid = None
        self.heptapod_permission = None

        for md in context.invocation_metadata():
            if md.key == HG_GIT_MIRRORING_MD_KEY:
                mirroring = md.value.strip().lower() == 'true'
            elif md.key == NATIVE_PROJECT_MD_KEY:
                native = md.value.strip().lower() == 'true'
            elif md.key == SKIP_HOOKS_MD_KEY:
                skip_gl_hooks = md.value.strip().lower() == 'true'
            elif md.key == ACCEPT_MR_IID_KEY:
                accept_mr_iid = md.value.strip()
            elif md.key == HEPTAPOD_PERMISSION_KEY:
                self.heptapod_permission = md.value.strip()

        mirroring = mirroring or not native

        ui.setconfig(b'heptapod', b'native', native)
        ui.setconfig(b'heptapod', b'no-git', not mirroring)

        environ = ui.environ
        if skip_gl_hooks:
            environ[PY_HEPTAPOD_SKIP_HOOKS] = b'yes'

        environ[b'HEPTAPOD_USERINFO_GL_ID'] = user.gl_id.encode('ascii')
        environ[b'HEPTAPOD_USERINFO_USERNAME'] = (
            user.gl_username.encode('utf-8'))
        environ[b'HEPTAPOD_USERINFO_NAME'] = user.name
        environ[b'HEPTAPOD_USERINFO_EMAIL'] = user.email
        environ[b'GL_PROTOCOL'] = b'web'  # same hardcoding as in Gitaly
        environ[b'GL_REPOSITORY'] = grpc_repo.gl_repository.encode('utf-8')
        # TODO project but apparently not used in py-heptapod hooks but still
        # may be useful for user-defined hooks
        if accept_mr_iid is not None:
            environ[b'HEPTAPOD_ACCEPT_MR_IID'] = accept_mr_iid.encode('ascii')

    def handle_value_error(self, context, exc_args):
        context.abort(self.STATUS_CODE_MISSING_REPO_ARG, exc_args[0])

    def handle_key_error(self, context, exc_args):
        ktype = exc_args[0]
        if ktype == 'storage':
            context.abort(self.STATUS_CODE_STORAGE_NOT_FOUND,
                          "No storage named %r" % exc_args[1])
        elif ktype == 'repo':
            context.abort(self.STATUS_CODE_REPO_NOT_FOUND,
                          exc_args[1])

    def create_and_load_repo(self, repository: Repository, context):
        """Create the repository and load it.

        :raises RepositoryCreationError:
        """
        self.hg_init_repository(repository, context)
        return self.load_repo_inner(repository, context)

    def load_or_create_repo(self, repository: Repository, context):
        """Load the repository, creating it if needed.

        :returns: a boolean being `True` iff creation occurred and the
        repository itself.
        """
        try:
            return False, self.load_repo_inner(repository, context)
        except KeyError as exc:
            if exc.args[0] == 'repo':
                return True, self.create_and_load_repo(repository, context)
            else:
                self.handle_key_error(context, exc.args)
        except ValueError as exc:
            self.handle_value_error(context, exc.args)

    def load_repo_inner(self, repository: Repository, context):
        """Load the repository from storage name and relative path

        :param repository: Repository Gitaly Message, encoding storage name
            and relative path
        :param context: gRPC context (used in error raising)
        :raises:
          - ``KeyError('storage', storage_name)`` if storage is not found
          - ``KeyError('repo', path, details)`` if repo not found or
            cannot be loaded.
        """
        global repos_counter
        if repos_counter % GARBAGE_COLLECTING_RATE_GEN2 == 0:
            gc_collect(2)
        elif repos_counter % GARBAGE_COLLECTING_RATE_GEN1 == 0:
            gc_collect(1)

        repos_counter += 1

        # shamelessly taken from heptapod.wsgi for the Hgitaly bootstrap
        # note that Gitaly Repository has more than just a relative path,
        # we'll have to decide what we make of the extra information
        repo_path = self.repo_disk_path(repository, context)
        logger.debug("loading repo at %r", repo_path)

        try:
            repo = hg.repository(self.ui, repo_path)
        except error.RepoError as exc:
            raise KeyError('repo', repo_path, repr(exc.args))

        weakref.finalize(repo, clear_repo_class, repo.unfiltered().__class__)
        srcrepo = hg.sharedreposource(repo)
        if srcrepo is not None:
            weakref.finalize(srcrepo, clear_repo_class,
                             srcrepo.unfiltered().__class__)

        return repo

    def storage_root_dir(self, storage_name, context):
        """Return the storage directory.

        If the storage is unknown, this raises
        ``KeyError('storage', storage_name)``
        """
        if not storage_name:
            # this is the best detection of a missing `repository` field
            # in request, without having the request object itself
            raise ValueError('repository not set')

        root_dir = self.storages.get(storage_name.rsplit(':', 1)[-1])
        if root_dir is None:
            raise KeyError('storage', storage_name)
        return root_dir

    def repo_disk_path(self, repository: Repository, context):
        rpath = normalize_rpath(repository)
        root_dir = self.storage_root_dir(repository.storage_name, context)

        # GitLab filesystem paths are always ASCII
        repo_path = os.path.join(root_dir, rpath.encode('ascii'))
        return repo_path

    def aux_git_repo_disk_path(self, repository: Repository, context):
        # GitLab filesystem paths are always ASCII. Not normalizing to `.hg`
        # obviously.
        rpath = repository.relative_path.encode('ascii')
        root_dir = self.storage_root_dir(repository.storage_name, context)
        return os.path.join(
            root_dir, AUX_GIT_REPOS_RELATIVE_DIR.encode('ascii'), rpath)

    def temp_dir(self, storage_name, context, ensure=True):
        """Return the path to temporary directory for the given storage

        Similar to what Gitaly uses, with a dedicated path in order
        to be really sure not to overwrite anything. The important feature
        is that the temporary directory is under the root directory of
        the storage, hence on the same file system (atomic renames of
        other files from the storage, etc.)

        :param bool ensure: if ``True``, the temporary directory is created
           if it does not exist yet.
        """
        try:
            return self.temp_dir_inner(storage_name, context, ensure=ensure)
        except KeyError as exc:
            self.handle_key_error(context, exc.args)
        except ValueError as exc:
            self.handle_value_error(context, exc.args)
        except OSError as exc:
            context.abort(StatusCode.INTERNAL,
                          "Error ensuring temporary dir: %s" % exc)

    def temp_dir_inner(self, storage_name, context, ensure=True):
        """Return the path to temporary directory for the given storage

        Similar to what Gitaly uses, with a dedicated path in order
        to be really sure not to overwrite anything. The important feature
        is that the temporary directory is under the root directory of
        the storage, hence on the same file system (atomic renames of
        other files from the storage, etc.)

        :param bool ensure: if ``True``, the temporary directory is created
           if it does not exist yet.
        :raises KeyError: if the storage is unknown
        :raises OSError: if creation fails.
        """
        temp_dir = os.path.join(self.storage_root_dir(storage_name, context),
                                b'+hgitaly', b'tmp')
        if not ensure:
            return temp_dir

        # not the proper time to switch everything to pathlib (operates on
        # str paths, but surrogates returned by os.fsdecode() seem to really
        # work well)
        to_create = []
        current = temp_dir

        while not os.path.exists(current):
            to_create.append(current)
            current = os.path.dirname(current)

        while to_create:
            # same mode as in Gitaly, hence we don't care about groups
            # although this does propagate the setgid bit
            os.mkdir(to_create.pop(), mode=0o755)

        return temp_dir

    def repo_workdirs_root(self, gl_repo: Repository, context):
        tmp = Path(os.fsdecode(
            self.temp_dir(gl_repo.storage_name, context, ensure=True)
        ))
        rpath = normalize_rpath(gl_repo)
        return tmp / 'workdirs' / rpath

    @contextmanager
    def working_dir(self, gl_repo: Repository, repo, context, changeset=None):
        """Provide a working directory updated to the given changeset.

        The working directory is part from the pool of reusable working
        directories and created if needed.
        """

        with working_directory(self.repo_workdirs_root(gl_repo, context),
                               repo,
                               client_id=CLIENT_ID,
                               incarnation_id=INCARNATION_ID,
                               changeset=changeset) as wd:
            # sadly, even passing repo.ui in share creation is not enough
            # for transient config items to be forwarded. Seems to be
            # unrelated to share-safe, since it is on by default since
            # Mercurial 6.1
            for section, key in CONFIG_TO_FORWARD_IN_WORKING_DIRS:
                wd.repo.ui.setconfig(section, key,
                                     repo.ui.config(section, key))
            yield wd

    def hg_init_repository(self, repository: Repository, context):
        """Initialize a mercurial repository from a request object.

        :return: ``None``: the resulting repository has to be loaded in the
           standard way, using its path.
        :raises RepositoryCreationError: and updates context with error
           code and details.
        """
        corr_logger = LoggerAdapter(logger, context)
        try:
            repo_path = self.repo_disk_path(repository, context)
        except KeyError:
            msg = "no such storage: %r" % repository.storage_name
            context.set_details(msg)
            corr_logger.error(msg)
            context.set_code(StatusCode.INVALID_ARGUMENT)
            raise RepositoryCreationError(repository)

        if os.path.lexists(repo_path):
            msg = ("creating repository: repository exists already")
            corr_logger.error(msg)
            context.set_details(msg)
            context.set_code(StatusCode.ALREADY_EXISTS)
            raise RepositoryCreationError(repository)

        try:
            corr_logger.info("Creating repository at %r", repo_path)
            hg.peer(self.ui, opts={}, path=repo_path, create=True)
        except OSError as exc:
            context.set_code(StatusCode.INTERNAL)
            context.set_details("hg_init_repository(%r): %r" % (repo_path,
                                                                exc))
            raise RepositoryCreationError(repository)

    def repo_command(self, repo, context, cmd, *args, **kwargs):
        """Call a Mercurial command on the given repository.

        :param str cmd: name of the command
        """
        cmd = cmdutil.findcmd(cmd.encode('ascii'), commands.table)[1][0]
        return cmd(repo.ui, repo, *args, **kwargs)

    def publish(self, changeset, context):
        self.repo_command(changeset.repo(), context, 'phase',
                          public=True,
                          draft=False,
                          secret=False,
                          force=False,
                          rev=[str(changeset.rev()).encode('ascii')])
