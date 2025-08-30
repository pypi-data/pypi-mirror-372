# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Multiprocess server

The main entry point is :func:`run_forever`
"""
import contextlib
import logging
from multiprocessing import cpu_count
import signal
import socket
import time
from urllib.parse import urlparse

from .address import (
    DEFAULT_TCP_PORT,
    InvalidUrl,
    UnsupportedUrlScheme,
    analyze_netloc,
)
from .mono import (
    BindError,
    server_process,
)
from .worker import WorkerProcess

logger = logging.getLogger(__name__)


class SocketReusePortError(RuntimeError):
    """If the socket could not be flagged with SO_REUSEPORT"""


def prefork_info_from_url(url):
    """Return needed information for prefork processing from URL."""
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise InvalidUrl(url, *exc.args)

    scheme = parsed.scheme
    if scheme in ('tcp', 'tls'):
        try:
            family, host, port = analyze_netloc(parsed.netloc)
        except ValueError:
            # can't really happen after urlparse (does already same checks)
            # still catching to be refactor-proof
            raise InvalidUrl(url)

        if port is None:
            port = DEFAULT_TCP_PORT
        return scheme, (family, host, port)
    else:
        return scheme, None


@contextlib.contextmanager
def prebind_sockets(listen_urls):
    """Pre-bind all sockets with the SO_REUSEPORT option."""
    # failing early if there's one invalid URL in the mix, so that
    # we don't have anything to clean up (this would raise ValueError)
    extracted_urls = ((url, prefork_info_from_url(url)) for url in listen_urls)
    prebound_urls = []

    sockets = []

    def close_sockets():
        for sock in sockets:
            sock.close()

    for url, (scheme, info) in extracted_urls:
        try:
            if scheme == 'tcp':
                family, host, port = info

                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                if sock.getsockopt(socket.SOL_SOCKET,
                                   socket.SO_REUSEPORT) == 0:
                    raise SocketReusePortError(url)
                try:
                    sock.bind((host, port))
                except Exception:
                    logger.exception("Could not bind on %r (bind info=%r)",
                                     url, info)
                    raise BindError(url)
                else:
                    sockets.append(sock)

                info = ("Pre-bound %r for %r", info[1:], url)
                prebound_urls.append(url)
            elif scheme == 'unix':
                info = ("Unix Domain Socket doesn't need port pre-binding", )
            else:
                raise UnsupportedUrlScheme(scheme)

            logger.info(*info)

        except Exception:
            logger.info("Closing previously bound sockets after exception")
            close_sockets()
            raise

    try:
        yield prebound_urls
    finally:
        close_sockets()


def terminate_workers(witness, workers, sig, *a):
    witness.set(True)
    logger.info("Catched signal %d, workers=%r", sig, workers)
    for worker in workers:
        logger.info("Terminating %s (alive is %r)", worker, worker.is_alive())
        # using is_alive() could be subject to a race, whereas
        # terminate() will send SIGTERM as soon as possible.
        try:
            worker.terminate()
        except Exception as exc:
            # only warning because it may not even be alive.
            logger.exception("Terminating worker %s failed: %r",
                             worker, exc)


class MutableBoolean:
    def __init__(self, v):
        self.set(v)

    def set(self, v):
        self.v = v

    def __bool__(self):
        return self.v


def termination_signals(workers, termination):
    """Signal handler for termination.

    :param workers: iterable of the :class:`Process` instances of the workers.
    :param termination: :class:`MutableBoolean` instance that will be set
       to ``True`` to indicate that worker termination is due to this handler.
       Main use-case would be to avoid restarting them.
    """
    for sig_name in ('SIGTERM', 'SIGINT'):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            signal.signal(sig, lambda *a: terminate_workers(
                termination, workers, *a))


def run_forever(listen_urls, storages,
                nb_workers=None,
                restart_done_workers=False,
                monitoring_interval=60,
                max_rss_mib=1024,
                mono_process=False,
                **process_kwargs):
    """Run the server, never stopping

    :param listen_urls: list of URLs, given as in the same form as in
       GitLab configuration files.
    :param storages: a :class:`dict`, mapping storage names to the
       corresponding root directories for repositories.
    :param float monitoring_interval: time, in seconds, between successive
       monitorings of workers.
    :param max_rss_mib: maximum Resident Set Size of workers, in MiB. If
       a worker goes over it, it will be gracefully restarted.
    """
    if mono_process:
        return server_process(0, listen_urls, storages,
                              mono_process=True,
                              **process_kwargs)

    if nb_workers is None:
        nb_workers = cpu_count() // 2 + 1

    worker_kwargs = dict(restart_done_workers=restart_done_workers,
                         max_rss=max_rss_mib << 20,
                         )
    worker_kwargs.update(process_kwargs)

    with prebind_sockets(listen_urls) as prebound_urls:
        workers = [WorkerProcess.run(process_callable=server_process,
                                     process_args=(0, listen_urls, storages),
                                     **worker_kwargs)]
        if prebound_urls:
            workers.extend(
                WorkerProcess.run(process_callable=server_process,
                                  process_args=(i, prebound_urls, storages),
                                  **worker_kwargs)
                for i in range(1, nb_workers))
        else:
            logger.info("No socket prebound for multiprocessing "
                        "(expected if listening only to Unix Domain socket) "
                        "Starting only one worker")

        general_shutdown = MutableBoolean(False)
        termination_signals(workers, general_shutdown)

        logger.info("All %d worker processes started", len(workers))

        keep_monitoring = True
        while keep_monitoring and not general_shutdown:
            for worker in workers:
                keep_monitoring &= worker.watch()
            time.sleep(monitoring_interval)

        logger.warning("General shutdown required, wrapping up")
        for worker in workers:
            worker.join()
        logger.info("All worker processes are finished. Closing down")
