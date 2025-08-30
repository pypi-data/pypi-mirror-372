# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess

import grpc

from hgitaly.testing.grpc import wait_server_accepts_connection
from hgitaly.testing.storage import storage_path

HGITALY_SOURCE_ROOT = Path(__file__).parent.parent


@attr.s
class RHGitalyServer:
    home_dir = attr.ib()
    sidecar_address = attr.ib()
    env_overrides = attr.ib(default=None)
    """Optional environment variables overrides.

    If not ``None``, this :class:`dict` will be applied to the process
    environment, after the several settings normally performed :meth:`running`.
    To be used in special cases only.
    """

    termination_timeout = attr.ib(default=1)
    """Time allowed for RHGitaly to shutdown after termination request

    Useful to test that termination actually works. Normally it should be
    very fast, even with the `debug` build.
    """

    socket_name = attr.ib(default='rhgitaly.socket')

    @contextmanager
    def running(self):
        env = dict(os.environ)
        env['GITALY_TESTING_NO_GIT_HOOKS'] = "1"  # will be eventually useful
        timeout = int(env.pop('RHGITALY_STARTUP_TIMEOUT', '30').strip())

        env['RHGITALY_CONFIG_DIRECTORY'] = self.home_dir
        env['RHGITALY_REPOSITORIES_ROOT'] = str(storage_path(self.home_dir))
        socket_path = self.home_dir / self.socket_name
        url = 'unix:%s' % socket_path.resolve()
        env['RHGITALY_LISTEN_URL'] = url
        env['RHGITALY_SIDECAR_ADDRESS'] = self.sidecar_address

        if self.env_overrides is not None:
            env.update(self.env_overrides)
        rhgitaly_dir = HGITALY_SOURCE_ROOT / 'rust/rhgitaly'

        rhgitaly_exe = env.get('RHGITALY_EXECUTABLE')
        if rhgitaly_exe is None:  # pragma no cover
            subprocess.check_call(('cargo', 'build', '--locked'),
                                  cwd=rhgitaly_dir)
            run_cmd = ('cargo', 'run')
        else:  # pragma no cover
            # Popen would not run a relative binary so easily
            run_cmd = [Path(rhgitaly_exe).resolve()]

        with open(self.home_dir / 'rhgitaly.log', 'w') as logf:
            rhgitaly = subprocess.Popen(
                run_cmd,
                stdout=logf, stderr=logf,
                env=env,
                cwd=rhgitaly_dir,
            )

        self.pid = rhgitaly.pid
        # visible and useful only by putting a breakpoint right before it:
        print(f"Tests dir: {self.home_dir}")

        try:
            # tonic (actually H2) does not accept the default authority
            # set in the case of Unix Domain Sockets by gRPC 1.58.
            # See https://github.com/hyperium/tonic/issues/742 and for instance
            # this solution by k8s clients:
            # https://github.com/kubernetes/kubernetes/pull/112597
            with grpc.insecure_channel(
                    url,
                    options=[('grpc.default_authority', 'localhost')]
            ) as channel:
                wait_server_accepts_connection(channel, timeout=timeout)
                yield channel
        finally:
            rhgitaly.terminate()
            rhgitaly.wait(timeout=self.termination_timeout)
