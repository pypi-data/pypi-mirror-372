# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import logging
import shutil

from hgitaly import feature
from hgitaly.logging import CORRELATION_ID_MD_KEY
from hgitaly.servicer import (
    HEPTAPOD_PERMISSION_KEY,
    NATIVE_PROJECT_MD_KEY,
    PY_HEPTAPOD_SKIP_HOOKS,
    SKIP_HOOKS_MD_KEY,
)
from hgitaly.stub.shared_pb2 import Repository

from heptapod.testhelpers import (
        LocalRepoWrapper,
)
from heptapod.testhelpers.git import GitRepo
from hgitaly.tests.common import (
    make_empty_repo_uniform,
)
from hgitaly.service.interceptors import base_logger as intercept_logger

from hgitaly.stub.ref_pb2_grpc import (
    RefServiceStub,
)
from hgitaly.stub.ref_pb2 import (
    ListRefsRequest,
)
from hgitaly.stub.shared_pb2 import (
    User,
)
from hgitaly.testing.storage import (
    stowed_away_git_repo_path,
)

# for coverage of hgitaly.logging
intercept_logger.setLevel(logging.DEBUG)


@attr.s
class ServiceFixture:
    """Fixture base class to absorb some of the boilerplate.

    See test_ref for example usage.

    There is still a lot of duplication between this class and
    :mod:`hgitaly.tests.common` we should probably merge them together
    at some point.

    Interesting attributes not defined as `attr.ib()`:

    - ``grpc_repo``: gRPC :class:`Repository` instance specifying the
       managed repo
    - ``repo_wrapper``: can be used to handle the managed repo directly
    - ``changesets``: a dict mapping convenient names to changeset contexts
      (returned by :attr:`repo_factory`)
    """

    stub_cls = None
    """Class attribute to be provided by concrete classes."""

    grpc_channel = attr.ib()
    server_repos_root = attr.ib()
    with_repo = attr.ib(default=True)
    """If ``True``, create a repository in the default storage upon setup.

    The repository details are then accessible in :attr:`grpc_repo`
    and :attr:`repo_wrapper`. If :attr:`with_repo` is ``False``, these
    attributes are initialised to None
    """
    auto_cleanup = attr.ib(default=False)
    """If ``True``, remove repositories tracked by this class upon tear down.

    For other repositories than the one created if :attr:`with_repo` is
    ``True``, this relies on downstream code adding them to
    attr:`repos_to_cleanup`.

    This can be useful for certain services because the
    ``server_repos_root`` fixture has the module scope, but most
    services won't need it because the path of the repository provided by
    this class is unique.
    """

    feature_flags = attr.ib(factory=list)
    """Feature flags to send to the server.

    Tests can set feature flags by inner mutation, e.g.::

       fixture.feature_flags.append(('my-flag', True))

    As of this writing, they are passed only if the subclasses uses the
    generic `self.rpc`, something like::

      self.rpc('MyRpc', request)
    """

    correlation_id = attr.ib(default=None)
    """Correlation id, to test/exert the logging system
    """

    repo_factory = attr.ib(default=make_empty_repo_uniform)
    """Callable with the same signature as :func:`make_empty_repo_uniform`.
    """

    def __enter__(self):
        self.stub = self.stub_cls(self.grpc_channel)
        if self.with_repo:
            self.repo_wrapper, self.grpc_repo, self.changesets = (
                self.repo_factory(self.server_repos_root))
            self.repos_to_cleanup = [self.repo_wrapper.path]
        else:
            self.repo_wrapper = self.grpc_repo = self.changesets = None
            self.repos_to_cleanup = []
        return self

    def __exit__(self, *exc_args):
        if not self.auto_cleanup:
            return

        for repo_path in self.repos_to_cleanup:
            if repo_path.exists():
                shutil.rmtree(repo_path)

    def additional_repo(self, rel_path, storage_name='default'):
        """Register an additional repository by storage relative path.

        The repository is not created (a future option may be introduced
        to do it).

        :returns: repository absolute path and :class:`Repository` instance
          (gRPC message).
        """
        repo_path = self.repo_path(rel_path, storage_name=storage_name)
        repo_msg = Repository(storage_name=storage_name,
                              relative_path=rel_path)
        self.repos_to_cleanup.append(repo_path)
        return repo_path, repo_msg

    def storage_path(self, storage_name='default'):
        """Utility method to avoid depending too much on actual disk layout.

        This repeats the actual implementation just once.
        """
        return self.server_repos_root / storage_name

    def repo_path(self, rel_path, **kw):
        """Utility method to avoid depending too much on actual disk layout.

        This makes no assumption whether the repo nor the storage actually
        exist.
        """
        return self.storage_path(**kw) / rel_path

    def side_git_repo_path(self, hg_path, **kw):
        return stowed_away_git_repo_path(self.server_repos_root, hg_path,
                                         **kw)

    def side_git_repo(self, *a, **kw):
        return GitRepo(self.side_git_repo_path(*a, **kw))

    def make_repo_wrapper(self, rel_path, **kw):
        """Utility method to avoid depending too much on actual disk layout.

        The repository is expected to exist.
        """
        return LocalRepoWrapper.load(self.repo_path(rel_path, **kw))

    def rpc(self, method_name, request):
        """Call a method, taking care of metadata."""
        return getattr(self.stub, method_name)(
            request,
            metadata=self.grpc_metadata()
        )

    def grpc_metadata(self):
        """Bake method call metadata.
        """
        metadata = feature.as_grpc_metadata(self.feature_flags)
        corr_id = self.correlation_id
        if corr_id is not None:
            metadata.append((CORRELATION_ID_MD_KEY, corr_id))
        return metadata

    def git_repo(self, **storage_kw):
        return self.side_git_repo(self.repo_wrapper.path, **storage_kw)


class MutationServiceFixture(ServiceFixture):
    """A feature meant for mutating methods.

    It has a default :attr:`user`, generates the appropriate gRPC metadata,
    etc.
    """

    heptapod_permission = None

    def __enter__(self):
        super(MutationServiceFixture, self).__enter__()
        self.ref_stub = RefServiceStub(self.grpc_channel)
        self.user = User(gl_id='user-37',
                         name=b'Test User',
                         email=b'testuser@heptapod.test',
                         gl_username='testuser')
        self.repo_wrapper.repo.ui.environ[PY_HEPTAPOD_SKIP_HOOKS] = b'yes'
        return self

    def grpc_metadata(self):
        mds = super(MutationServiceFixture, self).grpc_metadata()
        native = getattr(self, 'hg_native', True)
        mds.append((NATIVE_PROJECT_MD_KEY, str(native)))
        mds.append((SKIP_HOOKS_MD_KEY, 'true'))
        perm = self.heptapod_permission
        if perm is not None:
            mds.append((HEPTAPOD_PERMISSION_KEY, perm))
        return mds

    def list_refs(self, repo=None):
        if repo is None:
            repo = self.grpc_repo

        return {
            r.name: r.target for resp in self.ref_stub.ListRefs(
                ListRefsRequest(repository=repo))
            for r in resp.references
        }
