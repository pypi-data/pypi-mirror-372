# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import logging

from mercurial import (
    error,
)

from .. import message
from ..util import (
    chunked,
)

from ..stub.mercurial_changeset_pb2 import (
    ListMercurialChangesetsRequest,
    ListMercurialChangesetsResponse,
    MercurialChangesetField,
    MercurialRepositoryView,
)
from ..stub.mercurial_changeset_pb2_grpc import (
    MercurialChangesetServiceServicer,
)
from ..servicer import HGitalyServicer

logger = logging.getLogger(__name__)


class MercurialChangesetServicer(MercurialChangesetServiceServicer,
                                 HGitalyServicer):
    """MercurialChangesetService implementation.

    The ordering of methods in this source file is the same as in the proto
    file.
    """
    def ListMercurialChangesets(self,
                                request: ListMercurialChangesetsRequest,
                                context) -> ListMercurialChangesetsResponse:
        repo = self.load_repo(request.repository, context)
        if request.view == MercurialRepositoryView.UNFILTERED:
            repo = repo.unfiltered()

        try:
            revs = repo.revs(request.revset)
        except error.RepoLookupError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          "%r (hint=%r)" % (exc, exc.hint))

        fields = set(request.fields)
        if MercurialChangesetField.ALL in fields:
            fields = None

        for chunk in chunked(revs):
            yield ListMercurialChangesetsResponse(
                changesets=(message.mercurial_changeset(repo[rev],
                                                        fields=fields)
                            for rev in chunk)
            )
