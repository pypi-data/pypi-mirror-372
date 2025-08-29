# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""High level utilities for Mercurial manifest handling.

The purpose is both to provide exactly what the HGitaly services need
and to abstract away from the actual manifest implementation: we might
at some point switch to some version of Tree Manifest if one appears that
fills our basic needs (namely to be a peer implementation detail, having no
effect on changeset IDs).

The module is meant to harbour several classes, according to the
underlying Mercurial core implementations. The dispatching is done by
the :func:`miner` fatory function.

It is legitimate to optimize each class according to the (stable) properties
of the core manifest object it works on.
"""
import attr
from mercurial.context import filectx
from mercurial.utils.stringutil import binary as is_binary


@attr.s
class ManifestMiner:
    """High level data extraction for basic Mercurial manifest.
    """
    changeset = attr.ib()

    def ls_dir(self, path):
        """List direct directory contents of path at given changeset.

        Anything from inside subdirectories of ``path`` is ignored.

        :param changeset: a :class:`changectx` instance
        :param bytes path: path in the repository of the directory to list.
           Can be empty for the root directory, but not ``b'/'``.
        :returns: a pair ``(subdirs, filepaths)`` of lists, where
          ``subdirs`` contains the sub directories and ``filepaths`` the direct
          file entries within ``path``.
          Both lists are lexicographically sorted.
          All elements are given by their full paths from the root.
        """
        subtrees = set()
        file_paths = []
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        for file_path in self.changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                continue
            split = file_path[prefix_len:].split(b'/', 1)
            if len(split) > 1:
                subtrees.add(prefix + split[0])
            else:
                file_paths.append(file_path)
        file_paths.sort()
        return sorted(subtrees), file_paths

    def iter_dir_recursive(self, path):
        """Iterate on recursive directory contents of path in order.

        :returns: yields pairs (path, is_directory)
        """
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        changeset = self.changeset

        in_dir = False
        seen_subdirs = set()

        for file_path in changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                if in_dir:
                    break
                continue  # pragma no cover (see coverage#198 and PEP626)

            in_dir = True

            split = file_path[prefix_len:].rsplit(b'/', 1)

            # accumulate ancestor dirs that need to be yielded
            acc = []
            while len(split) > 1:
                subdir = split[0]
                if subdir in seen_subdirs:
                    # if yielded yet, all its ancestors also are
                    break
                acc.append(subdir)
                seen_subdirs.add(subdir)
                split = subdir.rsplit(b'/', 1)

            for subdir in reversed(acc):
                yield (prefix + subdir, True)

            yield (file_path, False)

    def iter_dir_with_flat_paths(self, path):
        """Iterate on directory direct contents with "flat_path" information.

        :returns: yields triplets (full path, is_dir, flat_path) where
                  ``full_path`` is the path of a file or directory from
                  the repo root, ``is_dir`` indicates whether it is a
                  directory and ``flat_path`` is as explained below.

        About ``flat_path``, here is a comment from the current version of
        commit.proto::

          // Relative path of the first subdir that doesn't have only
          // one directory descendant


        Gitaly reference implementation (Golang)::

          func populateFlatPath(ctx context.Context, c catfile.Batch,
                                entries []*gitalypb.TreeEntry) error {
            for _, entry := range entries {
              entry.FlatPath = entry.Path

              if entry.Type != gitalypb.TreeEntry_TREE {
                continue
              }

              for i := 1; i < defaultFlatTreeRecursion; i++ {
                subEntries, err := treeEntries(
                    ctx, c, entry.CommitOid,
                    string(entry.FlatPath), "", false)

                if err != nil {
                  return err
                }

                if (len(subEntries) != 1 ||
                    subEntries[0].Type != gitalypb.TreeEntry_TREE) {
                  break
                }

                entry.FlatPath = subEntries[0].Path
              }
            }

            return nil
          }

        Implementation for the standard Mercurial manifest has of course
        to be very different, since it lists full paths to leaf
        (non-directory) files. In particular, there are no empty directories.

        The interpretation  is that the "flat path" is the longest
        common directory ancestor of all file entries that are inside the
        considered directory entry. Here is a proof (can certainly be much
        simplified in a direct reasoning not involving reductio at absurdum,
        but writing it down was enough to convince ourselves).

        0. Assumptions and conventions:

           + there is no empty directory (guaranteed by the manifest data
             structure in the Mercurial case).
           + by X≤Y, we mean that Y is a path ancestor of X (inclusive)
           + let E be the considered directory entry and Fp its flat path
             as computed by the Golang implementation

        1. Fp is a common directory ancestor of all file entries f such that
           f≤E

           Let G be the greatest common ancestor of Fp and f.
           The crawling performed by the implementation went through G,
           since Fp≤G, so let's see what happened then.
           If f is a direct child of G, then Fp=G. If not, then let h be the
           direct child of G such that f≤h. h cannot be the only directory
           child of g: otherwise we would have Fp≤h, and h would be a greater
           common ancestor of Fp and f. Therefore the crawling stopped at G,
           hence Fp=G.

        2. Let G be the greatest common directory ancestor of all file entries
           f such that f≤E are ancestors of Fp.

           By derinition of "greatest", G≤Fp because Fp is a common directory
           ancestor.
           Let's see what the crawling implementation did at G if G≠Fp:

           Because of the halting condition of the implementation,
           either Fp has a file child and is therefore the greatest common
           directory ancestor, or Fp has at least two distinct directory
           children. Obviously, Only one of those can be an ancestor of G.
           So let h be a child of Fp such that G≤h is false. There is at least
           a file entry k such that k≤h, because directory entries cannot be
           empty. G is not an ancestor of k, contradicting its definition,
           so G must be equal to Fp.

        This implementation relies on manifest to emit paths in sorted manner.
        """
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        changeset = self.changeset

        in_dir = False
        subdir, flat_path = None, ()

        for file_path in changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                if in_dir:
                    break
                continue  # pragma no cover (see coverage#198 and PEP626)

            in_dir = True

            split = file_path[prefix_len:].split(b'/')
            if subdir is not None and split[0] != subdir:
                # we are leaving subdir, yield it
                dir_path = prefix + subdir
                yield (dir_path, True,
                       prefix + b'/'.join(flat_path) if flat_path else dir_path
                       )
                subdir, flat_path = None, ()

            if len(split) == 1:
                yield (file_path, False, file_path)
                subdir, flat_path = None, ()
            elif subdir is None:
                subdir, flat_path = split[0], split[:-1]
                continue

            flat_path = [
                segments[0] for segments in zip(flat_path, split)
                if segments[0] == segments[1]
            ]

        if subdir is not None:
            dir_path = prefix + subdir
            yield (dir_path, True,
                   prefix + b'/'.join(flat_path) if flat_path else dir_path
                   )

    def file_names_by_regexp(self, rx, subdir=b''):
        manifest = self.changeset.manifest()
        subdir_prefix = subdir + b'/' if subdir else b''

        for file_path in manifest.iterkeys():
            if not file_path.startswith(subdir_prefix):
                continue

            if rx is not None and rx.search(file_path) is None:
                continue

            yield file_path

    def iter_files_with_content(self, exclude_binary=False):
        manifest = self.changeset.manifest()
        repo = self.changeset.repo().unfiltered()
        for file_path, file_node, flags in manifest.iterentries():
            # filectx has a `isbinary` method, but it would actually
            # read the data once more (not cached on self)
            content = filectx(repo, file_path, fileid=file_node).data()
            if exclude_binary and is_binary(content):
                continue
            yield file_path, content, flags


def miner(changeset):
    """Return an appropriate manifest extractor for the given changeset.

    This factory function abstracts over possible future manifest
    types, for which we might write different implementations
    """
    return ManifestMiner(changeset)
