# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import multiprocessing
import os
import psutil
import pytest
import random
import signal
import socket
import sys
from socket import (
    AF_INET,
)
import time

from hgitaly.procutil import is_current_service_process
from hgitaly.testing.multiprocessing import assert_recv

from .. import prefork as server
from ..worker import WorkerProcess


def raiser(exc, *exc_args):
    def f(*a, **kw):
        raise exc(*(exc_args or ('something', )))

    return f


def test_catch_netloc_value_error(monkeypatch):
    # errors parsing the netloc
    monkeypatch.setattr(server, 'analyze_netloc', raiser(ValueError))
    url = "tcp://localhost"
    with pytest.raises(Exception) as exc_info:
        server.prebind_sockets([url]).__enter__()

    assert exc_info.value.args == (url, )


def test_so_portreuse_error(monkeypatch):
    monkeypatch.setattr(socket.socket, 'getsockopt', lambda *a: 0)
    url = "tcp://whatever"
    with pytest.raises(server.SocketReusePortError) as exc_info:
        server.prebind_sockets([url]).__enter__()
    assert exc_info.value.args == (url, )


def test_prebind_sockets(monkeypatch):
    bind_records = []

    def fake_bind(sock, port_info):
        bind_records.append(port_info)

    monkeypatch.setattr(socket.socket, 'bind', fake_bind)

    with server.prebind_sockets(['tcp://127.0.0.1:0',
                                 'tcp://[::1]:0',
                                 'tcp://localhost:0',
                                 'unix:/rel/path',
                                 ]):
        assert bind_records == [('127.0.0.1', 0),
                                ('::1', 0),
                                ('localhost', 0),
                                ]

    # a getsockopt that gives expected success values only for IPv4
    def getsockopt(sock, *a, **kw):
        if a[1] != socket.SO_REUSEPORT:  # pragma no cover (for compat)
            return socket.getsockopt(*a, **kw)
        return 0 if sock.family == AF_INET else 1

    monkeypatch.setattr(socket.socket, 'getsockopt', getsockopt)

    del bind_records[:]

    # will fail on the second, hence call the close() for the first
    # that doesn't fail and coverage tells us it's really called
    with pytest.raises(server.SocketReusePortError):
        server.prebind_sockets(['tcp://127.0.0.1:0',
                                'tcp://[::1]:0',
                                ]).__enter__()


def test_run_forever(monkeypatch, tmpdir):

    # server processes are subprocesses. We're only interested into
    # proper start/stop and correct arguments dispatching. Let's have
    # them write that to a file.
    workers_log = tmpdir.join('worker-start.log')

    def fake_server(wid, urls, storages, **kw):
        with open(workers_log, 'a') as logf:
            logf.write("%d %s\n" % (wid, ' '.join(urls)))

    def read_workers():
        res = {}
        for line in workers_log.readlines():
            split = line.split()
            wid = int(split[0])
            for url in split[1:]:
                res.setdefault(url, []).append(wid)
        workers_log.remove()
        return res

    monkeypatch.setattr(server, 'server_process', fake_server)

    tcp_url = 'tcp://localhost:1234'
    unix_url = 'unix:/hgitaly.socket'

    server.run_forever([tcp_url], {}, nb_workers=3, mono_process=True)
    workers = read_workers()
    assert sum(len(wids) for wids in workers.values()) == 1

    server.run_forever([tcp_url], {},
                       nb_workers=3,
                       monitoring_interval=0.01)
    workers = read_workers()
    assert len(workers[tcp_url]) == 3

    # we don't want more than one worker per unix URL because it's not
    # implemented yet
    server.run_forever([unix_url], {},
                       nb_workers=5,
                       monitoring_interval=0.01)

    workers = read_workers()
    assert len(workers[unix_url]) == 1

    # mixed scenario
    server.run_forever([unix_url, tcp_url], {},
                       nb_workers=5,
                       monitoring_interval=0.01)
    workers = read_workers()
    assert workers[unix_url] == [0]
    assert set(workers[tcp_url]) == {0, 1, 2, 3, 4}

    # defaulting based on CPU count
    server.run_forever([tcp_url], {}, None,
                       monitoring_interval=0.01)
    assert tcp_url in workers  # not so obvious if there's only one CPU

    # at least 2 unless we are on a single CPU system
    monkeypatch.setattr(multiprocessing, 'cpu_count', lambda: 2)
    assert len(workers[tcp_url]) >= 2


def test_siblings_recognition():

    def worker_callable(wid, pipe, **kw):  # pragma no cover
        from hgitaly import procutil
        procutil.IS_CHILD_PROCESS = wid != 2
        pipe.send("started")

        while True:
            pipe.poll(timeout=1)
            requested_pid = pipe.recv()
            print(f"Worker {wid} got {requested_pid}")
            res = is_current_service_process(requested_pid)
            print(f"Worker {wid} says {res}")
            pipe.send(is_current_service_process(requested_pid))

    pipes = [multiprocessing.Pipe() for _ in range(3)]
    parent_pipes = [p[0] for p in pipes]
    child_pipes = [p[1] for p in pipes]

    workers = [WorkerProcess(process_args=(wid, child_pipes[wid]),
                             process_callable=worker_callable)
               for wid in range(3)]

    try:
        for wp in workers:
            wp.init_process()

        for wid, worker in enumerate(workers):
            worker.start()
            assert_recv(parent_pipes[wid], "started")

        # sanity check: boolean change in child does not leak to parent
        from hgitaly import procutil
        assert not procutil.IS_CHILD_PROCESS

        # workers are siblings of themselves
        parent_pipes[0].send(workers[0].pid)
        assert_recv(parent_pipes[0], True)

        # other sibling is recognized
        parent_pipes[0].send(workers[1].pid)
        assert_recv(parent_pipes[0], True)

        parent_pipes[1].send(workers[0].pid)
        assert_recv(parent_pipes[1], True)

        # the manager is not a sibling
        parent_pipes[0].send(os.getpid())
        assert_recv(parent_pipes[0], False)

        # PID 1 is never a sibling
        parent_pipes[0].send(1)
        assert_recv(parent_pipes[0], False)

        # non-existing process cannot be a sibling
        while True:
            unknown_pid = random.randint(10000, 1 << 31)
            if not psutil.pid_exists(unknown_pid):
                parent_pipes[1].send(unknown_pid)
                assert_recv(parent_pipes[1], False)
                break

        # worker 3 considers itself to be standalone
        parent_pipes[2].send(workers[0].pid)
        assert_recv(parent_pipes[2], False)
        parent_pipes[2].send(workers[2].pid)
        assert_recv(parent_pipes[2], True)
    finally:
        for worker in workers:
            if worker.process.is_alive():
                # kill() would prevent coverage collection
                worker.process.terminate()
            worker.join()


def test_terminate_workers(monkeypatch, tmpdir):

    def worker_callable(wid, queue, **kw):  # pragma no cover
        def bye(*a):
            queue.put((wid, 'bye'))
            sys.exit(0)

        signal.signal(signal.SIGTERM, bye)
        queue.put((wid, 'ready'))
        time.sleep(10)  # should be 100x times enough
        queue.put((wid, 'timeout'))  # pragma no cover

    queue = multiprocessing.Queue()

    def read_messages():
        msgs = {}
        for _ in range(2):
            msg = queue.get()
            msgs[msg[0]] = msg[1]
        return msgs

    workers = [WorkerProcess(process_args=(wid, queue),
                             process_callable=worker_callable)
               for wid in range(3)]

    for wp in workers:
        wp.init_process()

    # omitting to start a worker to trigger exception in its
    # termination, hence testing that we aren't impaired by that.
    for worker in workers[1:]:
        worker.start()

    # wait for all running workers to be ready to handle signal
    assert read_messages() == {wid: 'ready' for wid in range(1, 3)}

    shutdown_required = server.MutableBoolean(False)
    server.terminate_workers(shutdown_required, workers, signal.SIGTERM)
    for worker in workers[1:]:
        worker.join()

    assert shutdown_required  # flipped by terminate_workers()
    assert read_messages() == {wid: 'bye' for wid in range(1, 3)}


def test_mutable_boolean():
    mut_bool = server.MutableBoolean(False)
    assert bool(mut_bool) is False
    assert not mut_bool

    # demonstrate the main use-case: passing down to any callable
    # and getting back the changed value.
    def mutator(mutable, v):
        mutable.set(v)

    mutator(mut_bool, True)
    assert bool(mut_bool) is True
    assert mut_bool

    # getting back
    mutator(mut_bool, False)
    assert bool(mut_bool) is False
    assert not mut_bool
