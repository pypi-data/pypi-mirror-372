# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities to generate Mercurial revset expressions.

Notably used to convert Git revision specifications, see the
gitrevisions(7) man page.
"""

from .revision import (
    gitlab_revision_changeset,
)


class FollowNotImplemented(NotImplementedError):
    pass


def revset_from_git_revspec(repo, revspec, for_follow=False):
    """Generate Mercurial revset from a given Git revspec.

    In many cases, `revision` arguments to Gitaly gRPC methods can be
    any valid Git revision specifications (revspecs), since they often are
    simply forwarded to an actual Git subprocess.

    At this point, we only support most common Git revision ranges, and
    the case of a single revision.

    No symbolic name like bookmarks, GitLab branches or tags are in the
    resulting revset: there are only operators and revnos or node ids.
    Hence it is appropriate (and often needed) to use it on unfiltered
    repositories.

    The resulting revset includes the sorting directive to make it consistent
    with the default `git log` ordering.

    :param bytes revspec: Git revision specification
    :param for_follow: if ``True``, indicates that the caller intends to use
       the resulting revset with additional following of copy tracking. In
       that case, specifying ancestors is to be avoided, as it would lead
       to iterate quadratically on them (ancestors of each ancestor), which
       can exhaust all system resources on large repositories (hgitaly#117).
    :return: the resulting Mercurial `revset`, or ``None`` if not found.
    """
    if b'...' in revspec:
        r1, r2 = revspec.split(b'...')
        revset = revset_symmetric_difference(repo, r1, r2,
                                             for_follow=for_follow)
    elif b'..' in revspec:
        r1, r2 = revspec.split(b'..')
        revset = revset_git_range(repo, r1, r2, for_follow=for_follow)

    else:  # single revision
        ctx = gitlab_revision_changeset(repo, revspec)
        if ctx is None:
            return None
        return ctx.hex() if for_follow else b"reverse(::%s)" % ctx

    return b"sort(%s, -rev)" % revset


def revset_git_range(repo, r1, r2, for_follow=False):
    """Make a revset for a Git (two-dot) Range Notation

    Remind that the Dotted Range Notations are just notations looking like
    ranges, but do not express actual DAG ranges.

    Excerpt from gitrevisions(7):

      The ``..`` (two-dot) Range Notation
        The ``^r1 r2`` set operation appears so often that there is a
        shorthand for it. When you have two commits ``r1`` and ``r2`` (named
        according to the syntax explained in SPECIFYING REVISIONS above),
        you can ask for commits that are reachable from ``r2`` excluding those
        that are reachable from ``r1`` by ``^r1 r2`` and it can be written as
        ``r1..r2``.

      (...)

      In these [two] shorthand notations, you can omit one end and let it
      default to HEAD.

    :param for_follow: same meaning as in :`func`:`revset_from_git_revspec`
    """
    if for_follow:
        raise FollowNotImplemented()

    ctx_start, ctx_end = resolve_git_range(repo, r1, r2)
    return b"::%s - ::%s" % (ctx_end, ctx_start)


def revset_symmetric_difference(repo, r1, r2, for_follow=False):
    """Make a revset for a Git Symmetric Difference.

    Excerpt from gitrevisions(7):

      The ``...`` (three-dot) Symmetric Difference Notation
          A similar notation ``r1...r2`` is called symmetric difference of
          ``r1`` and ``r2`` and is defined as
          ``r1 r2 --not $(git merge-base --all r1 r2)``.
          It is the set of commits that are reachable from either one of
          ``r1`` (left side) or ``r2`` (right side) but  not from both.

      In these [two] shorthand notations, you can omit one end and let it
      default to HEAD.

    :param for_follow: same meaning as in :`func`:`revset_from_git_revspec`
    """
    if for_follow:
        raise FollowNotImplemented()

    ctx_start, ctx_end = resolve_git_range(repo, r1, r2)
    left = ctx_start.rev()
    right = ctx_end.rev()
    branchpoint = repo.revs(b"ancestor(%d, %d)" % (left, right)).first()
    return b"only(%d + %d, %d)" % (left, right, branchpoint)


def resolve_git_range(repo, r1, r2):
    """Resolve the two ends of a Git Dotted Range Notation.

    Remind that the Dotted Range Notations are just notations looking like
    ranges, but do not express actual DAG ranges.

    :return: a pair of changeset contexts

    Excerpt from gitrevisions(7):

      In these two shorthand notations (two and three dot range notations),
      you can omit one end and let it default to ``HEAD``. For example,
      ``origin..`` is a shorthand for ``origin..HEAD`` and asks "What did I do
      since I forked from the ``origin`` branch?" Similarly, ``..origin`` is
      a shorthand for ``HEAD..origin`` and asks "What did the origin do since
      I forked from them?"
    """
    if not r1:
        r1 = b'HEAD'
    if not r2:
        r2 = b'HEAD'
    return tuple(gitlab_revision_changeset(repo, r) for r in (r1, r2))


def changeset_descr_regexp(pattern, ignore_case=False):
    """Generate a revset regular expression for changeset description.

    This takes care of any necessary escaping.
    """
    predicate = b'hpd_dsc_irx' if ignore_case else b'hpd_dsc_rx'
    return b"%s(r'%s')" % (predicate, pattern)
