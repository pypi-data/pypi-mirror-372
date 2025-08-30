# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

# flake8: noqa E402
import os
import time
from mercurial.i18n import _
from mercurial import (
    demandimport,
    error,
    pycompat,
    registrar,
    util,
)

demandimport.disable()

from hgitaly.identification import ensure_client_id
from hgitaly.server import (
    run_forever,
    UnsupportedUrlScheme,
    InvalidUrl,
    BindError,
)
from . import revset

if util.safehasattr(registrar, 'configitem'):

    configtable = {}
    configitem = registrar.configitem(configtable)
    configitem(b'hgitaly', b'tokei-executable', b'tokei')
    configitem(b'hgitaly', b'license-detector-executable', b'license-detector')
    configitem(b'hgitaly', b'git-executable', b'git')


cmdtable = {}
command = registrar.command(cmdtable)


revsetpredicate = revset.revsetpredicate


DEFAULT_LISTEN_URL = b'tcp://127.0.0.1:9237'


def reraise_abort(msg, exc):
    """Raise error.abort from inner exception.

    :param msg: a bytes string containing as many `%s` as needed.
    """
    fmt_args = tuple(pycompat.sysbytes(str(a)) for a in exc.args)
    raise error.Abort(_(b"hgitaly-serve: " + msg) % fmt_args)


@command(b'hgitaly-serve',
         [(b'', b'repositories-root',
           b'',
           _(b'Path to the root directory for repositories storage. '
             b'Defaults to the `heptapod.repositories-root` '
             b'configuration item '),
           _(b'REPOS_ROOT')),
          (b'', b'listen',
           [],
           _(b'URL to listen on, default is %s, can be '
             b'repeated to listen on several addresses' % DEFAULT_LISTEN_URL),
           _(b'ADDRESS')),
          (b'', b'mono-process',
           False,
           _(b'Mono process mode (useful for debugging, notably with pdb).'
             b'No forking occurs, the main process is the single worker. '
             b'In particular the hgitaly.workers configuration item is '
             b'ignored.')),
          ],
         _(b'[OPTIONS]...'),
         norepo=True
         )
def serve(ui, **opts):
    """Start a HGitaly server with only one storage, named 'default'

    By default the root of repositories is read from the
    `heptapod.repositories-root` configuration item if present.
    """
    # local time does not make sense for a server-oriented process,
    # so let's switch to UTC. Mercurial itself is transparent about that
    # server-side commits will be recorded as been done UTC, which is fine
    # (it does not change the recorded time, which is always UTC, just some
    # ways of displaying it).
    os.environ['TZ'] = 'UTC'
    time.tzset()
    listen_urls = [pycompat.sysstr(u) for u in opts['listen']]
    if not listen_urls:
        # Any default in the option declaration would be added to
        # explicely passed values. This is not what we want, hence the late
        # defaulting done here.

        # Although gRPC defaults to IPv6, existing Gitaly setups
        # (GDK and monolithic Docker container) bind explicitely on IPv4
        listen_urls = [DEFAULT_LISTEN_URL.decode()]
    repos_root = opts.get('repositories_root')
    if not repos_root:
        repos_root = ui.config(b'heptapod', b'repositories-root')
        if repos_root is None:
            raise error.Abort(_(
                b"No value found in configuration for "
                b"'heptapod.repositories-root'. Please define it or run "
                b"the command with the --repositories-root option."
                ))
    config_root = os.fsdecode(ui.config(b'hgitaly', b'configuration-root',
                                        default=repos_root))
    ensure_client_id(config_root)
    nb_workers = ui.configint(b'hgitaly', b'workers')
    run_opts = dict(nb_workers=nb_workers,
                    restart_done_workers=True,
                    mono_process=opts.get('mono_process'))
    max_rss_mib = ui.configint(b'hgitaly', b'worker.max-rss-mib')
    if max_rss_mib is not None:
        run_opts['max_rss_mib'] = max_rss_mib
    monitoring_interval = ui.configint(b'hgitaly',
                                       b'worker.monitoring-interval-seconds')
    if monitoring_interval is not None:
        run_opts['monitoring_interval'] = monitoring_interval

    shutdown_timeout = ui.configint(
        b'hgitaly',
        b'worker.graceful-shutdown-timeout-seconds')
    if shutdown_timeout is not None:
        run_opts['graceful_shutdown_timeout_seconds'] = shutdown_timeout

    storages = dict(default=repos_root)
    try:
        run_forever(listen_urls, storages, **run_opts)
    except UnsupportedUrlScheme as exc:
        reraise_abort(b"unsupported URL scheme: '%s'", exc)
    except InvalidUrl as exc:
        reraise_abort(b"invalid URL: '%s' (%s)", exc)
    except BindError as exc:
        reraise_abort(b"could not listen (bind) to URL '%s'", exc)
