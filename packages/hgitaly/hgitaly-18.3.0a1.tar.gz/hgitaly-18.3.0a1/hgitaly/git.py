# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Git specific things, mostly constants."""

import fnmatch

ZERO_SHA_1 = '0' * 40

NULL_COMMIT_ID = ZERO_SHA_1
NULL_BLOB_OID = ZERO_SHA_1

# from `sha1-file.c` in Git 2.28 sources
# we're not dealing for now with the fact that there will be
# two kinds of OIDs with SHA-1 and SHA-256 soon.

# The Git tree object hash that corresponds to an empty tree (directory)
EMPTY_TREE_OID = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

# The Git blob object hash that corresponds to an empty blob (file)
EMPTY_BLOB_OID = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'

OBJECT_MODE_DOES_NOT_EXIST = 0  # see, e.g, ChangedPaths in diff.proto
OBJECT_MODE_LINK = 0o120000  # symlink to file or directory
OBJECT_MODE_EXECUTABLE = 0o100755  # for blobs only
OBJECT_MODE_NON_EXECUTABLE = 0o100644  # for blobs only
OBJECT_MODE_TREE = 0o40000

FILECTX_FLAGS_TO_GIT_MODE_BYTES = {
    b'l': b'%o' % OBJECT_MODE_LINK,
    b'x': b'%o' % OBJECT_MODE_EXECUTABLE,
    b'': b'%o' % OBJECT_MODE_NON_EXECUTABLE,
}


class GitPathSpec:
    """File path matching as Git pathspecs do.

    Reference: gitglossary(7)

    This implementation is to be completed (magic words etc.

    Example from the glossary about wildcards matching slashes::

      >>> pathspec = GitPathSpec(b'Documentation/*.jpg')
      >>> pathspec.match(b'Documentation/chapter_1/figure_1.jpg')
      True

    Before the last slash, wildcards do not match slashes::

      >>> pathspec = GitPathSpec(b'*/figure_1.jpg')
      >>> pathspec.match(b'Documentation/chapter_1/figure_1.jpg')
      False
      >>> pathspec.match(b'figure_1.jpg')
      False
      >>> pathspec.match(b'Documentation/figure_1.jpg')
      True

    Trailing slash subtleties::

      >>> pathspec = GitPathSpec(b'Documentation/')
      >>> pathspec.match(b'Documentation')
      False
      >>> pathspec.match(b'Documentation/foo')
      True

    Implicit directory prefix (not mentioned in gitglossary(7) but still
    true and checkable with all commands, including `git log` and `git add`)::

      >>> pathspec = GitPathSpec(b'Documentation/foo')
      >>> pathspec.match(b'Documentation/foo/bar')
      True

      >>> pathspec = GitPathSpec(b'Documentation')
      >>> pathspec.match(b'Documentation')
      True
      >>> pathspec.match(b'Documentation/foo')
      True
      >>> pathspec.match(b'Documentation/foo/bar')
      True

      >>> pathspec = GitPathSpec(b'Doc*')
      >>> pathspec.match(b'Documentation/foo')
      True
      >>> pathspec.match(b'Documentation/foo/bar')
      True
    """

    def __init__(self, pathspec: bytes):
        self.split_spec = pathspec.split(b'/')
        # Note that `fnmatch.translate()` (outputs regexp) chokes
        # on bytes strings.

    def match(self, file_path):
        split_input = file_path.split(b'/', len(self.split_spec) - 1)
        if len(split_input) < len(self.split_spec):
            return False

        split_spec_but_one = self.split_spec[:-1]
        # a split is never empty, even if done for the empty string
        last_spec = self.split_spec[-1]

        split_input_but_one = split_input[:-1]
        last_input = split_input[-1]

        # all elements of both lists except the last one are free of slashes,
        # hence fnmatch cannot create a deeper match for patterns before
        # the last slash in pathspec.
        return (all(not s or fnmatch.fnmatch(i, s)
                    for i, s in zip(split_input_but_one, split_spec_but_one))
                and
                (
                    # trailing slash in pathspec
                    not last_spec
                    # case of deep fnmatch accross remaining directories
                    or fnmatch.fnmatch(last_input, last_spec)
                    # case of pattern=foo and input=foo/bar
                    or fnmatch.fnmatch(last_input.split(b'/', 1)[0], last_spec)
                ))


class GitLiteralPathSpec:
    def __init__(self, pathspec):
        self.pathspec = pathspec
        if pathspec.endswith(b'/'):
            self.dir_prefix = pathspec
        else:
            self.dir_prefix = pathspec + b'/'

    def match(self, file_path):
        return (
            file_path == self.pathspec
            or file_path.startswith(self.dir_prefix)
        )
