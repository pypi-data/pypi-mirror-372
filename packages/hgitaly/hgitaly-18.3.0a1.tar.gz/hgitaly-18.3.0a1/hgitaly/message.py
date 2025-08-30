# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""High level utilities for Gitaly protocol messages."""

from mercurial.utils import stringutil as hg_stringutil
from mercurial import (
    node,
    pycompat,
)

from .stub.shared_pb2 import (
    Branch,
    CommitAuthor,
    CommitStatInfo,
    GitCommit,
    SignatureType,
    Tag,
)
from .stub.commit_pb2 import (
    ListLastCommitsForTreeResponse,
)
from .stub.mercurial_changeset_pb2 import (
    MercurialChangeset,
    MercurialChangesetField,
)
from google.protobuf import text_encoding
from google.protobuf.text_format import (
    _Printer as ProtobufPrinter,
    TextWriter,
)
from google.protobuf.timestamp_pb2 import Timestamp

from .diff import (
    diff_opts,
    chunk_stats,
)
from .gitlab_ref import reverse_refs


LONG_BYTES_TRUNCATION = 50
"""Threshold to truncate long bytes fields.

Keep in mind that with the escaping, a single byte can be represented as
up to 4 bytes.
"""


class Printer(ProtobufPrinter):
    """Modified version to truncate long bytes fields."""

    def PrintFieldValue(self, field, value):
        if isinstance(value, bytes) and len(value) > LONG_BYTES_TRUNCATION:
            self.out.write('"')
            self.out.write(text_encoding.CEscape(
                b'%s... (truncated, actual size %d bytes)' % (
                    value[LONG_BYTES_TRUNCATION:], len(value)),
                False))
            self.out.write('"')
        else:
            super(Printer, self).PrintFieldValue(field, value)


def message_to_string(message):
    """Using our own :class:`Printer` and our own defaults."""
    out = TextWriter(as_utf8=False)
    printer = Printer(
        out,
        indent=0,
        as_utf8=False,
        as_one_line=True,
        use_short_repeated_primitives=True,
        pointy_brackets=False,
        use_index_order=False,
        float_format=False,
        double_format=False,
        use_field_number=False,
        descriptor_pool=None,
        message_formatter=None,
        print_unknown_fields=False,
        force_colon=False)
    printer.PrintMessage(message)
    result = out.getvalue().rstrip()
    return result


def as_dict(message):
    return {descr.name: value for descr, value in message.ListFields()}


class Logging:
    """Wrapper of requests and responses for sensible logging.

    Still has the formatting happen lazily, only if the message
    is emitted. We still pay the price of at least one instantiation though.
    """

    def __init__(self, message):
        self.msg = message

    def __repr__(self):
        return '%s { %s }' % (self.msg.__class__.__name__,
                              message_to_string(self.msg),
                              )

    __str__ = __repr__


def commit_author(ctx):
    """Produce a `GitCommit` message from a :class:`changectx` instance.
    """
    auth = ctx.user()
    date = Timestamp()
    # hg time resolution is the second, see
    # https://www.mercurial-scm.org/wiki/ChangeSet
    seconds, offset = ctx.date()
    date.FromSeconds(int(seconds))
    if offset <= 0:
        # Mercurial sign convention is opposite of UTC+2 etc.
        tz_sign = b'+'
        offset_abs = -offset
    else:
        tz_sign = b'-'
        offset_abs = offset

    # Mercurial offset is in seconds
    tz_hours = offset_abs // 3600
    tz_minutes = (offset_abs % 3600) // 60

    return CommitAuthor(
        email=hg_stringutil.email(auth),
        name=hg_stringutil.person(auth),
        date=date,
        timezone=b"%s%02d%02d" % (tz_sign, tz_hours, tz_minutes),
        )


def commit_stats(ctx):
    if len(ctx.parents()) > 1:
        # Gitaly does not provide the stats for merge commits
        # (see Gitaly Comparison tests)
        return None

    ctx_from = ctx.p1()
    adds = dels = files = 0
    chunks = ctx.diff(ctx_from, opts=diff_opts(ctx.repo()))
    for stats in chunk_stats(chunks, ctx_from, ctx):
        adds += stats.additions
        dels += stats.deletions
        files += 1
    return CommitStatInfo(additions=adds, deletions=dels, changed_files=files)


def ref_segments_match(ref, pattern):
    """Tell if given ref first segments are exactly as in pattern."""
    pat_split = pattern.rstrip(b'/').split(b'/')
    ref_split = ref.split(b'/', len(pat_split))
    for r, p in zip(ref_split, pat_split):
        if r != p:
            return False
    return True


def commit_referenced_by(ctx, patterns):
    """Return references to the given commit, as full ref paths."""
    if not patterns:
        return

    repo = ctx.repo()
    refs = reverse_refs(repo).get(ctx.hex(), ())
    return [r for r in refs
            if any(ref_segments_match(r, pat) for pat in patterns)]


def commit(ctx, with_short_stats=False, include_referenced_by=()):
    """Return :class:`GitCommit` object from Mercurial :class:`changectx`.

    :param bool with_short_stats: if ``True``, fill-in the ``short_stats``
       field of :class:`GitCommit` messages.

    subject and body are as in gitaly/internal/git/log/commitmessage.go::

      var body string
      if split := strings.SplitN(commitString, "\n\n", 2); len(split) == 2 {
          body = split[1]
      }
      subject := strings.TrimRight(strings.SplitN(body, "\n", 2)[0], "\r\n")

    See also slightly different stripping gitlab/lib/gitlab/git/commit.rb::

        message_split = raw_commit.message.split("\n", 2)
        Gitaly::GitCommit.new(
          id: raw_commit.oid,
          subject: message_split[0] ? message_split[0].chomp.b : "",
          body: raw_commit.message.b,
          parent_ids: raw_commit.parent_ids,
          author: gitaly_commit_author_from_rugged(raw_commit.author),
          committer: gitaly_commit_author_from_rugged(raw_commit.committer)
        )

    Special case for caller convenience::

        >>> commit(None) is None
        True
    """
    if ctx is None:
        return None

    descr = ctx.description()
    author = commit_author(ctx)
    short_stats = commit_stats(ctx) if with_short_stats else None
    referenced_by = commit_referenced_by(ctx, include_referenced_by)
    return GitCommit(id=ctx.hex(),
                     subject=descr.split(b'\n', 1)[0].rstrip(b'\r\n'),
                     body=descr,
                     body_size=len(descr),
                     parent_ids=[p.hex().decode()
                                 for p in ctx.parents()
                                 if p.rev() != node.nullrev],
                     author=author,
                     committer=author,
                     short_stats=short_stats,
                     referenced_by=referenced_by,
                     )


def branch(name, target):
    return Branch(name=name, target_commit=commit(target))


def tag(name, target, tagging=None, signature_type=None):
    """Produce a :class:`Tag` instance

    :param target: a :class:`changectx` for the target of the tag
    :param tagging: optional :class:`changectx` for the changeset that
                    sets the tag.
    :pram signature_type: a :class:`SignatureType` or ``None``.
    """
    if signature_type is None:
        signature_type = SignatureType.NONE

    if tagging is None:
        tag_id = message = tag_author = None
        message_size = 0
    else:
        # TODO SPEC comment in `shared.proto` says the message will be
        # nullified if above a certain size and the size will be carried over,
        # but it doesn't say whose responsibility it is to do that,
        # nor how that threshold is to be determined
        # (information should be found by reading Gitaly Golang source).
        message = tagging.description()
        message_size = len(message)
        tag_id = pycompat.sysstr(tagging.hex())
        tag_author = commit_author(tagging)

    return Tag(name=name,
               id=tag_id,
               target_commit=commit(target),
               message=message,
               message_size=message_size,
               tagger=tag_author,
               signature_type=signature_type
               )


CommitForTree = ListLastCommitsForTreeResponse.CommitForTree


def commit_for_tree(changeset, path):
    """Message indicating the last changeset having modified a path"""
    return CommitForTree(commit=commit(changeset), path_bytes=path)


def mercurial_changeset(changeset, fields=None) -> MercurialChangeset:
    """Serialize changeset information.

    :param changeset: a :class:`changectx` instance
    :param fields: if specified, only the given fields are set in the
      returned message, otherwise alll currently implemented are.
    """
    all_fields = fields is None
    attrs = dict(id=changeset.hex())
    if all_fields or MercurialChangesetField.PHASE in fields:
        attrs['phase'] = changeset.phase()
    if all_fields or MercurialChangesetField.OBSOLETE in fields:
        attrs['obsolete'] = changeset.obsolete()
    if all_fields or MercurialChangesetField.BRANCH in fields:
        attrs['branch'] = changeset.branch()
    if all_fields or MercurialChangesetField.TOPIC in fields:
        attrs['topic'] = changeset.topic()
    if all_fields or MercurialChangesetField.FQBN in fields:
        attrs['fqbn'] = changeset.fqbn()
    if all_fields or MercurialChangesetField.TOPIC_NAMESPACE in fields:
        attrs['topic_namespace'] = changeset.topic_namespace()
    if all_fields or MercurialChangesetField.PARENT_IDS in fields:
        attrs['parent_ids'] = [ctx.hex() for ctx in changeset.parents()]
    return MercurialChangeset(**attrs)
