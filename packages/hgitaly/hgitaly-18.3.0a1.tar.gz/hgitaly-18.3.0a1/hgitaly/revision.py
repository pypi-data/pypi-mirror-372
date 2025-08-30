# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import StatusCode
import logging
import re

from mercurial import (
    error,
    scmutil,
)
from mercurial.context import changectx
from hgext3rd.heptapod.branch import get_default_gitlab_branch
from hgext3rd.heptapod.keep_around import (
    parse_keep_around_ref,
)
from heptapod.gitlab.change import (
    ZERO_SHA,
)
from heptapod.gitlab.branch import (
    gitlab_branch_from_ref,
)
from heptapod.gitlab.tag import (
    gitlab_tag_from_ref,
)
from .branch import (
    gitlab_branch_head
)
from .gitlab_ref import (
    gitlab_special_ref_target
)
from .tag import tagged_changeset

logger = logging.getLogger(__name__)

# 40 hex digits for SHA-1, 64 hex digits for SHA-2
_HASH_RX = r'^([0-9A-Fa-f]{40})|([0-9A-Fa-f]{64})$'
CHANGESET_HASH_BYTES_REGEXP = re.compile(_HASH_RX.encode('ascii'))
CHANGESET_HASH_STR_REGEXP = re.compile(_HASH_RX)

ZERO_SHA_STR = ZERO_SHA.decode('ascii')


class RevisionNotFound(LookupError):
    pass


def gitlab_revision_changeset(repo, revision):
    """Find the changeset for a given GitLab revision.

    In theory, a GitLab revision could be any Git valid revspec, that
    we'd had to translate into its Mercurial counterpart.

    At this point, we support changeset IDs in hex, GitLab branches, tags and
    ``HEAD`` (default GitLab branch).

    Obsolescence
    ------------
    Changeset IDs can return obsolete changesets (this is actually used in
    force push detection, or in Merge Request updates), while symbolic ones
    (branch, tags etc) *should* always return non obsolete changesets.

    :return: the changeset as a :class:`changectx` instance, or ``None``
             if not found.
    """
    if CHANGESET_HASH_BYTES_REGEXP.match(revision):
        try:
            ctx = repo.unfiltered()[revision]
        except error.RepoLookupError:
            return None  # voluntarily explicit

        return ctx if isinstance(ctx, changectx) else None

    if revision == b'HEAD':
        revision = get_default_gitlab_branch(repo)
        if revision is None:
            return None

    ka = parse_keep_around_ref(revision)
    if ka is not None:
        try:
            return repo.unfiltered()[ka]
        except error.RepoLookupError:
            logger.warning("Unresolvable keep-around %r", ka)
            return None

    # non ambigous ref forms: they should obviously take precedence
    gl_tag = gitlab_tag_from_ref(revision)
    if gl_tag is not None:
        return tagged_changeset(repo, gl_tag)

    gl_branch = gitlab_branch_from_ref(revision)
    if gl_branch is not None:
        # can return None
        return gitlab_branch_head(repo, gl_branch)

    # special ref
    ctx = gitlab_special_ref_target(repo.unfiltered(), revision)
    if ctx is not None:
        return ctx

    # direct GitLab tag name
    ctx = tagged_changeset(repo, revision)
    if ctx is not None:
        return ctx

    # direct GitLab branch name
    ctx = gitlab_branch_head(repo, revision)
    if ctx is not None:
        return ctx

    try:
        ctx = scmutil.revsingle(repo.unfiltered(), revision)
        # ctx can be, e.g., workingctx (see heptapod#717)
        # The null node is not to be filtered (it may be used in diffs)
        return ctx if isinstance(ctx, changectx) else None
    except error.RepoLookupError:
        return None  # voluntarily explicit


def gitlab_revision_hash(repo, revision):
    """Return the changeset hexadecimal hash for given GitLab revision

    This is the preferred method to use when handling lists of revisions
    because the contexts retured by func:`gitlab_revision_changeset` may be
    associated to different repository views (filtered or not), hence it
    can be a trap for caller code to use them in revsets.

    Besides the return type, a major difference with
    func:`gitlab_revision_changeset` is that it raises instead of returning
    ``None`` if the revision could not be resolved. This is also more
    handy in loops and comprehensions than checking for or filtering out
    ``None``.

    :returns: the hash, as an hexadecimal bytes string.
    :raises RevisionNotFound:
    """
    ctx = gitlab_revision_changeset(repo, revision)
    if ctx is None:
        raise RevisionNotFound(revision)
    return ctx.hex()


ALL_CHANGESETS = object()
VISIBLE_CHANGESETS = object()


def resolve_revspecs_positive_negative(repo, revisions,
                                       ignore_unknown=False):
    """Sort the given revision specs into positive/negative and resolve them.

    This method understand negative revspecs, such as ``^ref1`` or
    ``^12de34ad56be`` as well as positive ones, such as ``branch/default`` or
    ``12de34ad56be``.

    It also accepts the special ``ALL`` positive revspec,
    which triggers returning :const:`ALL_CHANGESETS` as the positive set
    and avoid all positive resolutions once it is encountered, as they would
    be useless.

    :param revisions: any iterable of bytes. Generators will be consumed.
    :param ignore_unknown: if ``False``, raise ``RevisionNotFound`` on the
       first encountered unknown revision. Otherwise, just ignore it.
    :returns: a pair ``(positive, negative)``. In general, these are
      :class:`set` instances, whose elements are hexadecimal node ids
      as bytes. As a special case, ``positive`` can be ``ALL_CHANGESETS``.

    Typically, the caller will want to interpret each sets with an inner ``OR``
    and connect them as ``AND NOT``. In terms of revset, if ``positive`` is
`   ``{pos1, pos2}`` and ``negative`` is ``{neg1, neg2}``, this translates as
    ``(pos1, pos2) % (neg1, neg2)``
    """
    resolved = {}
    positive = set()
    negative = set()
    for rev in revisions:
        logger.debug("resolve_revspecs_positive_negative repo %r, treating "
                     "revspec %r", repo.root, rev)
        if rev.startswith(b'^'):
            collection = negative
            rev = rev[1:]
        else:
            if rev == b'ALL':
                positive = ALL_CHANGESETS
            elif rev == b'--visible':
                positive = VISIBLE_CHANGESETS
            collection = positive

        if collection in (ALL_CHANGESETS, VISIBLE_CHANGESETS):
            # resolution is useless
            continue

        sha = resolved.get(rev)
        if sha is None:
            try:
                sha = gitlab_revision_hash(repo, rev)
            except RevisionNotFound:
                if ignore_unknown:
                    continue
                raise
        resolved[rev] = sha
        collection.add(sha)

    return positive, negative


def validate_oid(oid: str):
    """Check that the given commit_id is hexadecimal of correct length
    """
    return CHANGESET_HASH_STR_REGEXP.match(oid) is not None


def changeset_by_commit_id(repo, commit_id: str):
    """Return a changeset context from an exact full hexadecimal Node ID.

    :raises ValueError: if `commit_id` is not an hexadecimal number of correct
         length.
    :raises KeyError: if changeset not found.
    """
    if not validate_oid(commit_id):
        raise ValueError(commit_id)
    try:
        return repo[commit_id.encode('ascii')]
    except error.RepoLookupError:
        raise KeyError(commit_id)


def changeset_by_commit_id_abort(repo, commit_id: str, context):
    """Same as :func:`changeset_by_commit_id`, with some error treatment

    aborts gRPC context if ``commit_id`` is not an hexadecimal number of
    correct length.

    :return: the changeset context, or ``None`` if resolution failed
    """
    try:
        return changeset_by_commit_id(repo, commit_id)
    except KeyError:
        return None
    except ValueError:
        context.abort(StatusCode.INVALID_ARGUMENT,
                      f'cannot parse commit ID: "{commit_id}"')
