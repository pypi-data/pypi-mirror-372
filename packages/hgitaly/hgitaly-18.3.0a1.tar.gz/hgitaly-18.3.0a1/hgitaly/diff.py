# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities for comparison of content between changesets."""
import attr
from functools import cached_property
import re
import subprocess

from mercurial import (
    copies,
    diffutil,
    error,
    match as matchmod,
    patch as patchmod,
)

from .file_context import git_perms
from .git import (
    FILECTX_FLAGS_TO_GIT_MODE_BYTES,
    NULL_BLOB_OID,
    OBJECT_MODE_DOES_NOT_EXIST,
)
from .oid import (
    blob_oid,
    ctx_blob_oid,
)

from .stub.diff_pb2 import (
    ChangedPaths,
    DiffStats,
)

GIT_PATCH_ID_TIMEOUT_SECONDS = 10
"""Time given to `git patch-id` to finish after we've streamed the content.

Given that `git patch-id` is a C program (verified assertion), we expect it
to be much faster than HGitaly feeding it. A timeout of 10 seconds after
we're done streaming the patch content is therefore enormous.
"""

Status_Type_Map = dict(
    added=ChangedPaths.Status.ADDED,
    modified=ChangedPaths.Status.MODIFIED,
    removed=ChangedPaths.Status.DELETED,
    renamed=ChangedPaths.Status.RENAMED,
    # Note: Mercurial includes TYPE_CHANGE
    # (symlink, regular file, submodule...etc) in MODIFIED status
)
"""Mapping status object attributes to ChangedPaths enum."""

COPIED = ChangedPaths.Status.COPIED
RENAMED = ChangedPaths.Status.RENAMED
DIFF_HUNKS_START_RX = re.compile(rb'^(--- )|^(Binary file)')
"""To match the header line right before hunks start getting dumped."""


def changed_paths(repo, from_ctx, to_ctx, base_path, find_renames=False):
    if base_path is None:
        matcher = None
        path_trim_at = 0
    else:
        # scmutil's match is more geared towards the CLI
        # `hg log` etc and its include patterns would
        # force us to convert everything to absolute paths
        # since $CWD is not the repo root.
        # It is much simpler to use the lower-level match module.
        matcher = matchmod.match(
            root=repo.root,
            # cwd is required, yet should not be relevant
            # in this case.
            cwd=repo.root,
            patterns=[b'path:' + base_path])
        path_trim_at = len(base_path) + 1

    copy_info = copies.pathcopies(from_ctx, to_ctx, match=matcher)
    # copies do not distinguish actual copies from renames. The difference
    # will be that a rename goes with deletion of the original.

    status = from_ctx.status(to_ctx, match=matcher)
    # this will remove renames from copy_info, keeping only actual copies
    yield from status_changed_paths(from_ctx, to_ctx, status, copy_info,
                                    find_renames=find_renames,
                                    trim_at=path_trim_at)
    yield from copy_changed_paths(from_ctx,
                                  to_ctx,
                                  copy_info,
                                  trim_at=path_trim_at)


def status_changed_paths(from_ctx, to_ctx, status, copy_info,
                         find_renames=False, trim_at=0):
    rcopy_info = {v: k for k, v in copy_info.items()}
    """Return ChangedPaths from Mercurial status object"""
    for stype in ['added', 'modified', 'removed']:
        for path in status.__getattribute__(stype):
            copied_from = copy_info.get(path)
            if copied_from is not None:
                if copied_from not in status.removed or find_renames:
                    continue

            old_path = b''
            if stype == 'added':
                old_mode = OBJECT_MODE_DOES_NOT_EXIST
                old_blob_id = NULL_BLOB_OID
            else:
                old_mode = git_perms(from_ctx.filectx(path))
                old_blob_id = ctx_blob_oid(from_ctx, path)

            if stype == 'removed':
                new_path = rcopy_info.get(path)
                if new_path is None:
                    new_mode = OBJECT_MODE_DOES_NOT_EXIST
                    new_blob_id = NULL_BLOB_OID
                else:
                    del copy_info[new_path]
                    if find_renames:
                        stype = 'renamed'
                        old_path = path
                        path = new_path
                        new_mode = git_perms(to_ctx.filectx(new_path))
                        new_blob_id = ctx_blob_oid(to_ctx, new_path)
                    else:
                        new_mode = OBJECT_MODE_DOES_NOT_EXIST
                        new_blob_id = NULL_BLOB_OID
            else:
                new_mode = git_perms(to_ctx.filectx(path))
                new_blob_id = ctx_blob_oid(to_ctx, path)

            yield ChangedPaths(
                path=path[trim_at:],
                old_mode=old_mode,
                new_mode=new_mode,
                old_blob_id=old_blob_id,
                new_blob_id=new_blob_id,
                old_path=old_path,
                status=Status_Type_Map[stype]
            )


def copy_changed_paths(from_ctx, to_ctx, path_copies,
                       trim_at=0, find_renames=False):
    """Return ChangedPaths for the given paths, relative to base_path.

    Given that Gitaly currently (gitaly@c54d613d0) does not pass
    `--find-copies-harder` to `git diff-tree`, we cannot be sure of
    what is expected. That being said, `git diff-tree` gives the permission
    at source path as `old_mode`, so we're doing the same.
    """
    for target, source in path_copies.items():
        yield ChangedPaths(path=target[trim_at:],
                           status=COPIED,
                           old_mode=git_perms(from_ctx.filectx(source)),
                           old_blob_id=ctx_blob_oid(from_ctx, source),
                           new_mode=git_perms(to_ctx.filectx(target)),
                           new_blob_id=ctx_blob_oid(to_ctx, target),
                           old_path=source[trim_at:],
                           )


def chunk_stats(chunks, from_ctx, to_ctx):
    """Yield the DiffStats messages from the given diff chunks.

    Changectx params are there for uniformity and not really needed as
    of this writing
    """
    for hg_chunk in patchmod.parsepatch(chunks):
        chunk = Chunk(hg_chunk, from_ctx, to_ctx)

        old_path, path = chunk.from_to_file_paths
        if old_path == path:
            old_path = b''
        adds, dels = chunk.additions_deletions()
        yield DiffStats(
            path=path,
            old_path=old_path,
            additions=adds,
            deletions=dels,
        )


def diff_opts(repo, git=True):
    opts = {b'git': git}
    return diffutil.difffeatureopts(repo.ui, opts=opts, git=git)


def _get_filectx(changeset, path):
    try:
        return changeset[path]
    except error.ManifestLookupError:
        return None


@attr.define
class Chunk:
    """Wrap a Mercurial chunk with extracted information.

    This notably avoids repeated lookups in manifests.

    Perfomance notes: we assume that looking up in the manifest is the
    expensive task, not building :class:`filectx` instances, hence we
    do not make methods to check if a file is in one of the changesets,
    just use, e.g.,  :meth:`from_filectx` and check for ``None``.
    """

    hg_chunk = attr.ib()
    from_ctx = attr.ib()
    to_ctx = attr.ib()

    @cached_property
    def from_to_file_paths(self):
        """Return a tuple of (old, new) file path for a diff chunk header

        Takes case of renames into account
        """
        header = self.hg_chunk
        fname = header.filename()
        from_path, to_path = fname, fname
        if len(header.files()) > 1:
            # file is renamed
            from_path, to_path = header.files()
        return from_path, to_path

    @cached_property
    def from_filectx(self):
        return _get_filectx(self.from_ctx, self.from_file_path)

    @cached_property
    def to_filectx(self):
        return _get_filectx(self.to_ctx, self.to_file_path)

    @property
    def from_file_path(self):
        return self.from_to_file_paths[0]

    @property
    def to_file_path(self):
        return self.from_to_file_paths[1]

    def from_to_blob_oids(self):
        from_bid = to_bid = NULL_BLOB_OID
        from_path, to_path = self.from_to_file_paths

        if self.from_filectx is not None:
            cid = self.from_ctx.hex().decode('ascii')
            from_bid = blob_oid(None, cid, from_path)
        if self.to_filectx is not None:
            cid = self.to_ctx.hex().decode('ascii')
            to_bid = blob_oid(None, cid, to_path)
        return from_bid, to_bid

    def from_to_file_mode(self):
        from_path, to_path = self.from_to_file_paths
        from_mode, to_mode = b'0', b'0'
        from_filectx = self.from_filectx
        if from_filectx is not None:
            from_mode = FILECTX_FLAGS_TO_GIT_MODE_BYTES[from_filectx.flags()]
        to_filectx = self.to_filectx
        if to_filectx is not None:
            to_mode = FILECTX_FLAGS_TO_GIT_MODE_BYTES[to_filectx.flags()]
        return from_mode, to_mode

    def additions_deletions(self):
        """Return the pair (addition, deletions) for the chunk."""
        adds, dels = 0, 0
        for hunk in self.hg_chunk.hunks:
            add_count, del_count = hunk.countchanges(hunk.hunk)
            adds += add_count
            dels += del_count
        return adds, dels

    def header_with_index_line(self):
        """Generate header with the index line and binary indication.

        The index line is the expected Git-style one, with file modes etc.
        The binary indication tells whether there should be a placeholder
        instead actual Git binary content section. Callers can use it to
        generate the appropriate placeholder for their needs.
        """
        fname = self.hg_chunk.filename()
        old_bid, new_bid = self.from_to_blob_oids()
        indexline = ('index %s..%s' % (old_bid, new_bid)).encode('ascii')

        # Note: <mode> is required only when it didn't change between
        # the two changesets, otherwise it has a separate line
        if self.to_filectx is not None and self.to_filectx.path() == fname:
            oldmode, mode = self.from_to_file_mode()
            if mode == oldmode:
                indexline += b' ' + mode
        indexline += b'\n'
        headerlines = self.hg_chunk.header

        binary = False
        for index, line in enumerate(headerlines[:]):
            m = DIFF_HUNKS_START_RX.match(line)
            if m is None:
                continue

            binary = not bool(m.group(1))
            headerlines.insert(index, indexline)
            break
        return b''.join(headerlines), binary


def write_diff_to_file(fobj, changeset_from, changeset_to, dump_binary=True):
    """Compute diff and stream it to a file-like object

    The diff includes the expected "index line" as Git does: change of OID
    and of permissions for each file.

    :param fobj: a file-like object
    :param dump_binary: if ``True``, the Git binary content is dumped.
      Otherwise a placeholder is inserted, made of the file node ids. This
      matches Gitaly's behaviour in ``GetPatchId`` implementation (quoting
      internal/gitaly/service/diff/patch_id.go as of v16.6)::

        // git-patch-id(1) will ignore binary diffs, and computing binary
        // diffs would be expensive anyway for large blobs. This means that
        // we must instead use the pre- and post-image blob IDs that
        // git-diff(1) prints for binary diffs as input to git-patch-id(1),
        // but unfortunately this is only honored in Git v2.39.0 and newer.
        // We have no other choice than to accept this though, so we instead
        // just ask git-diff(1) to print the full blob IDs for the pre- and
        // post-image blobs instead of abbreviated ones so that we can avoid
        // any kind of potential prefix collisions.
        git.Flag{Name: "--full-index"},
    """
    repo = changeset_from.repo()
    # hg diff --git --no-binary does not include the index line
    # hg diff --git does include the index line but also dumps binary
    #   content, which is uselessly expensive in some cases (GetPatchID)
    # TODO generally avoid actual binary content in DiffService
    #   when Gitaly does the same.
    low_level_diff_opts = diff_opts(repo)
    low_level_diff_opts.nobinary = not dump_binary

    hg_chunks = changeset_to.diff(changeset_from, opts=low_level_diff_opts)
    for hg_chunk in patchmod.parsepatch(hg_chunks):
        chunk = Chunk(hg_chunk, changeset_from, changeset_to)
        from_path, to_path = chunk.from_to_file_paths
        header, binary_placeholder = chunk.header_with_index_line()
        fobj.write(header)

        if binary_placeholder:
            filename = hg_chunk.filename()
            fobj.write(b'--- a/%s\n' % filename)
            fobj.write(b'+++ b/%s\n' % filename)
            fobj.write(b'@@ -1 +1 @@\n')
            from_bid = to_bid = NULL_BLOB_OID.encode()
            if chunk.from_filectx is not None:
                from_bid = chunk.from_filectx.hex()
            if chunk.to_filectx is not None:
                to_bid = chunk.to_filectx.hex()
            fobj.write(b'-%s\n' % from_bid)
            fobj.write(b'+%s\n' % to_bid)
        else:
            for hunk in hg_chunk.hunks:
                hunk.write(fobj)


def run_git_patch_id(git_path, writer):
    """Call `git patch-id` in a subprocess

    :param writer: a callable writing the diff content to a file-like object
    """
    git = subprocess.Popen((git_path, b'patch-id', b'--verbatim'),
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    writer(git.stdin)

    try:
        # this also takes care of flushing/closing stdin
        out, err = git.communicate(timeout=GIT_PATCH_ID_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        # Quoting https://docs.python.org/3/library/subprocess.html:
        #   The child process is not killed if the timeout expires,
        #   so in order to cleanup properly a well-behaved application
        #   should kill the child process and finish communication
        git.kill()
        git.communicate()
        raise

    if git.returncode != 0:
        raise RuntimeError("git-patch-id returned code %d, stderr=%r" % (
            git.returncode, err))

    return out.strip().decode('ascii')


def git_patch_id(git_path, changeset_from, changeset_to):
    return run_git_patch_id(
        git_path,
        lambda stdin: write_diff_to_file(stdin, changeset_from, changeset_to,
                                         dump_binary=False)
    )
