# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from io import BytesIO
import os
import subprocess

import pytest

from heptapod.testhelpers import (
    LocalRepoWrapper,
)

from .. import diff as hgitaly_diff
from ..diff import (
    git_patch_id,
    run_git_patch_id,
    write_diff_to_file,
)
from ..tests.common import (
    MINIMAL_HG_CONFIG,
)
from hgitaly.service.diff import (
    CurrDiff,
    Limits,
    Parser,
)


def test_parser_corner_cases():
    parser = Parser(Limits(), CurrDiff())
    parser.parse([b""])


def diff_lines(cs_from, cs_to, **kw):
    out = BytesIO()
    write_diff_to_file(out, cs_from, cs_to, **kw)
    return out.getvalue().splitlines()


def test_git_patch_id(tmpdir):
    wrapper = LocalRepoWrapper.init(tmpdir, config=MINIMAL_HG_CONFIG)

    wrapper.commit_file('regular', content='foo\n')
    regular = (tmpdir / 'regular')
    regular.write('bar\n')

    script = tmpdir / 'script'
    script.write('#!/usr/bin/env python2\n'
                 'print "Hello, world"\n')
    script.chmod(0o755)
    cs1 = wrapper.commit([], add_remove=True)
    cs2 = wrapper.commit_file(
        'foo.gz',
        content=b'\x1f\x8b\x08\x08\xd6Q\xc1e\x00\x03foo\x00K'
        b'\xcb\xcf\xe7\x02\x00\xa8e2~\x04\x00\x00\x00',
        message='gzipped file is easy binary')

    assert diff_lines(cs1, cs2, dump_binary=False) == [
        b'diff --git a/foo.gz b/foo.gz',
        b'new file mode 100644',
        (b'index 0000000000000000000000000000000000000000..'
         b'%s_Zm9vLmd6' % cs2.hex()),
        b'Binary file foo.gz has changed',
        b'--- a/foo.gz',
        b'+++ b/foo.gz',
        b'@@ -1 +1 @@',
        b'-0000000000000000000000000000000000000000',
        b'+' + cs2[b'foo.gz'].hex(),
    ]

    patch_id2 = git_patch_id('git', cs1, cs2)

    cs3 = wrapper.commit_file(
        'foo.gz',
        content=b"\x1f\x8b\x08\x088=\xc2e\x00"
        b"\x03foo\x00K\xcb7\xe2\x02\x00\xb1F'q\x04\x00\x00\x00",
        message='gzipped file is easy binary')
    patch_id3 = git_patch_id('git', cs2, cs3)
    assert patch_id3 != patch_id2

    cs4 = wrapper.commit_file(
        'foo.gz',
        content=b"\x1f\x8b\x08\x08\xf2=\xc2e\x00"
        b"\x03foo\x00K\xcb7\xe6\x02\x00\xf0w<h\x04\x00\x00\x00",
        message='gzipped file is easy binary')
    patch_id4 = git_patch_id('git', cs3, cs4)
    assert len(set((patch_id4, patch_id3, patch_id2))) == 3


def test_run_git_patch_id_errors(tmpdir, monkeypatch):
    fake_git = tmpdir / 'git'
    fake_git_path = os.fsencode(str(fake_git))
    fake_git.write_text('\n'.join(('#!/usr/bin/env python3',
                                   'import sys',
                                   'import time',
                                   'timeout = sys.stdin.read()',
                                   'if not timeout:'
                                   '  sys.exit(21)',
                                   'time.sleep(float(timeout))',
                                   )),
                        encoding='ascii')
    fake_git.chmod(0o755)
    with pytest.raises(RuntimeError) as exc_info:
        run_git_patch_id(fake_git_path, lambda stdin: None)
    assert 'code 2' in exc_info.value.args[0]

    monkeypatch.setattr(hgitaly_diff, 'GIT_PATCH_ID_TIMEOUT_SECONDS', 0.001)

    with pytest.raises(subprocess.TimeoutExpired) as exc_info:
        run_git_patch_id(fake_git_path, lambda stdin: stdin.write(b'0.01'))
