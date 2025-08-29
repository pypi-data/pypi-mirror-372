# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
from contextlib import contextmanager
import grpc
import os
import subprocess

from hgitaly.testing.grpc import wait_server_accepts_connection
from hgitaly.testing.storage import (
    storage_path,
    DEFAULT_STORAGE_NAME,
)

from . import (
    GITALY_BIN_DIR,
    GITALY_INSTALL_DIR,
)


@attr.s
class GitalyServer:
    home_dir = attr.ib()

    def configure(self):
        home_dir = self.home_dir
        self.gitaly_conf = home_dir / 'gitaly_config.toml'
        self.gitaly_socket = home_dir / 'gitaly.socket'

        # this is required even if we won't use it (we're not sending any
        # GitLab hooks)
        gitlab_shell_dir = home_dir / 'gitlab-shell'
        gitlab_shell_dir.mkdir()

        default_storage_path = storage_path(home_dir)
        default_storage_path.mkdir()
        conf_lines = [
            'socket_path = "%s"' % self.gitaly_socket,
            # Gitaly compilation outputs its binaries at the root
            # of the checkout
            'bin_dir = "%s"' % GITALY_BIN_DIR,
            '[gitlab-shell]',
            'dir = "%s"' % gitlab_shell_dir,
            '[gitaly-ruby]',
            'dir = "%s"' % (GITALY_INSTALL_DIR / 'ruby'),
            '[[storage]]',
            f'name = "{DEFAULT_STORAGE_NAME}"',
            f'path = "{default_storage_path}"',
            '[git]',
            'use_bundled_binaries = true',
            ''
        ]
        self.gitaly_conf.write_text("\n".join(conf_lines))

    @contextmanager
    def start(self):
        self.configure()

        env = dict(os.environ)
        env['GITALY_TESTING_NO_GIT_HOOKS'] = "1"
        timeout = int(env.pop('GITALY_STARTUP_TIMEOUT', '30').strip())

        # as of Gitaly 14.9, the `logging.dir` setting does not have
        # it write to a file, let's redirect ourselves.
        with open(self.home_dir / 'gitaly.log', 'w') as logf:
            gitaly = subprocess.Popen(
                [GITALY_BIN_DIR / 'gitaly', self.gitaly_conf],
                stdout=logf, stderr=logf,
                env=env)

        with grpc.insecure_channel('unix:' + str(self.gitaly_socket),
                                   ) as gitaly_channel:
            wait_server_accepts_connection(gitaly_channel, timeout=timeout)
            yield gitaly_channel

        gitaly.terminate()
        gitaly.wait()
