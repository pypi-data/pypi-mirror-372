# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import contextlib
import logging
import random
import pytest
import shutil

import grpc

from heptapod.testhelpers.hg import RepoWrapper
from heptapod.testhelpers.gitlab import (
    activate_gitlab_state_maintainer,
    patch_gitlab_hooks,
)

from hgitaly.stub.shared_pb2 import Repository
from .comparison import BaseRpcHelper


logger = logging.getLogger(__name__)


@attr.s
class HGitalyRHGitalyComparison():
    """This fixture is for comparison between HGitaly and RHGitaly.

    As an edge case, it can be used to test RHGitaly alone, hence the
    `hgitaly_channel` is optional.

    Gitaly itself is not involved at all, so this is for HGitaly-specific
    calls, often but not necessarily involving the Mercurial services.
    """
    rhgitaly_channel = attr.ib()

    hgitaly_channel = attr.ib(default=None)
    hgitaly_repo = attr.ib(default=None)
    hg_repo_wrapper = attr.ib(default=None)
    gitlab_sent_hooks = attr.ib(default=attr.Factory(list))

    def activate_gitlab_state_maintainer(self, monkeypatch):
        activate_gitlab_state_maintainer(self.hg_repo_wrapper)
        patch_gitlab_hooks(monkeypatch, self.gitlab_sent_hooks)

    def rpc_helper(self, **kw):
        return RpcHelper(self, **kw)

    def invalidate(self):  # pragma no cover
        """Invalidate all caches.

        In particular, reload the Mercurial repo
        """
        wrapper = self.hg_repo_wrapper
        if wrapper is not None:
            wrapper.reload()

    @property
    def gitaly_repo(self):
        """Compatibility wrapper

        RPC helpers and the like usually expect a `gitaly_repo` attribute.
        """
        return self.hgitaly_repo


class RpcHelper(BaseRpcHelper):
    """Encapsulates a comparison fixture with call and compare helpers.

    This is derived from :class:`hgitaly.comparison.RpcHelper`, but it is
    very much simpler.
    """
    error_details_normalizer = None

    def init_stubs(self):
        comparison, stub_cls = self.comparison, self.stub_cls
        self.stubs = dict(rhgitaly=stub_cls(comparison.rhgitaly_channel))
        hgitaly_channel = comparison.hgitaly_channel
        if hgitaly_channel is not None:
            self.stubs['hgitaly'] = stub_cls(comparison.hgitaly_channel)

    def assert_compare(self, **kwargs):
        self.apply_request_defaults(kwargs)
        assert self.rpc('hgitaly', **kwargs) == self.rpc('rhgitaly', **kwargs)

    def assert_compare_errors(self, same_details=True,
                              skip_structured_errors_issue=None,
                              structured_errors_handler=None,
                              **hg_kwargs):
        """Compare errors returned by (R)HGitaly and Gitaly.

        :param:`structured_errors_handler`: if supplied, it is expected to be
          a :class:`dict` with the following keys:

          - `git_cls`: expected error class (gRPC message) from Gitaly
          - `hg_cls`: expected error class (gRPC message) from HGitaly
                      defaults to the value of `git_cls`
          - `to_git`: conversion callable from HGitaly's gRPC error message
            to Gitaly's
          - `git_normalizer`: additional normalizer to apply to Git error
            (some of them involve objects that cannot exist on the Mercurial
             side)
        """
        self.apply_request_defaults(hg_kwargs)

        with pytest.raises(grpc.RpcError) as exc_info_hg:
            self.rpc('hgitaly', **hg_kwargs)
        with pytest.raises(grpc.RpcError) as exc_info_git:
            self.rpc('rhgitaly', **hg_kwargs)
        self.assert_compare_grpc_exceptions(
            exc_info_hg.value,
            exc_info_git.value,
            same_details=same_details,
            vcses=('hg', 'hg'),
            skip_structured_errors_issue=skip_structured_errors_issue,
            structured_errors_handler=structured_errors_handler,
        )


@contextlib.contextmanager
def hgitaly_rhgitaly_comparison_fixture(server_repos_root,
                                        rhgitaly_channel,
                                        monkeypatch=None,
                                        hgitaly_channel=None,
                                        skip_repo=False,
                                        ):
    if skip_repo:
        hgitaly_repo = hg_repo_wrapper = None
    else:
        relative_path = 'repo-' + hex(random.getrandbits(64))[2:] + '.hg'
        storage = 'default'

        hgitaly_repo = Repository(relative_path=relative_path,
                                  storage_name=storage)

        hg_config = dict(
            phases=dict(publish=False),
            ui=dict(username='Hgitaly Tests <hgitaly@heptapod.test>'),
            heptapod={'repositories-root': str(server_repos_root / storage)},
            extensions={name: '' for name in ('evolve',
                                              'topic',
                                              'hgitaly',
                                              'heptapod')})
        hg_repo_wrapper = RepoWrapper.init(
            server_repos_root / storage / relative_path,
            config=hg_config)

    try:
        hrc = HGitalyRHGitalyComparison(rhgitaly_channel=rhgitaly_channel,
                                        hgitaly_channel=hgitaly_channel,
                                        hgitaly_repo=hgitaly_repo,
                                        hg_repo_wrapper=hg_repo_wrapper,
                                        )
        if not skip_repo:
            hrc.activate_gitlab_state_maintainer(monkeypatch)
        yield hrc

    finally:
        if hg_repo_wrapper is not None:
            hg_path = hg_repo_wrapper.path
            try:
                shutil.rmtree(hg_path)
            except Exception:  # pragma no cover
                logger.exception("Error removing the Mercurial repo at %r",
                                 hg_path)
