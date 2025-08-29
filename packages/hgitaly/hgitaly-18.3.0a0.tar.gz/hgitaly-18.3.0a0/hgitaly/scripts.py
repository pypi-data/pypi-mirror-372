# Copyright 2022-2023 Georges Racinet <georges.racinet@octobus.net>
# Copyright 2024 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse
from collections import defaultdict
from datetime import datetime
import json
import re
import statistics
import sys

ISOFORMAT_WITH_TZ = sys.version_info >= (3, 11)

RHGITALY_SPAN_CLOSE_RX = re.compile(
    r'(\d+-\d+-\d+T\d+:\d+:\d+\.\d+Z).*?(?:\[1m)?(\w+)(.\[0m.\[1m)?'
    r'\{.*rhgitaly::service.*? '
    r'close .*?time.busy.*?=.*?([0-9.]*?)([mnµ]?)s ')

REQUEST_SUFFIX = 'Request'

unit_multipliers_to_millis = {
    '': 1000,
    'm': 1,
    'µ': 1e-3,
    'n': 1e-6,
}


def hgitaly_parse_logs(fobj, since=None):  # pragma no cover
    """Parse a log file in HGitaly format.

    :returns: (first timestamp, call counts per request, execution times)
       Call counts and execution times are per requests, execution times
       only for requests with normal termination (i.e, not cancelled or
       failed)
    """
    called = defaultdict(lambda: 0)
    succeeded = defaultdict(list)
    first_timestamp = None
    for line in fobj:
        try:
            log = json.loads(line)
        except json.JSONDecodeError:
            # ignoring log lines predating the transition to JSON
            continue

        if first_timestamp is None:
            log_dt = log['asctime']
            if since is not None:
                if ISOFORMAT_WITH_TZ and not log_dt.endswith('Z'):
                    # the whole HGitaly process timezone is UTC, but this
                    # may not be explicit in the logging format
                    log_dt += 'Z'
                if not ISOFORMAT_WITH_TZ and log_dt.endswith('Z'):
                    # this Python version does not support time zones in
                    # ISO format, let's go the naive way.
                    log_dt = log_dt[:-1]
                # some Python versions accept only dots for subsecond part
                dt = datetime.fromisoformat(log_dt.replace(',', '.'))
                if dt < since:
                    continue
            first_timestamp = log['asctime']

        req = log.get('request')
        if req is None:
            continue

        req = req.split(' ', 1)[0]
        if req.endswith(REQUEST_SUFFIX):
            req = req[:-len(REQUEST_SUFFIX)]
        msg = log.get('message')
        if msg.startswith("Starting"):
            called[req] += 1
        elif msg.startswith("Finished"):
            # milliseconds for readability of most frequent cases
            succeeded[req].append(log["elapsed_seconds"] * 1000)

    return first_timestamp, called, succeeded


def snake_case_to_camel(s):
    """Change case of key from snake_case to CamelCase.

    >>> snake_case_to_camel('find_commits')
    'FindCommits'
    """
    return ''.join(w.capitalize() for w in s.split('_'))


def dict_snake_case_to_camel(d):
    """Change in place the case of keys.

    >>> d = dict(hg_publish=3)
    >>> dict_snake_case_to_camel(d)
    >>> d
    {'HgPublish': 3}
    """
    keys = tuple(d.keys())
    for k in keys:
        v = d.pop(k)
        d[snake_case_to_camel(k)] = v


def rhgitaly_parse_logs(fobj, since=None):  # pragma no cover
    """Parse a log file in HGitaly format.

    Same as :func:`hgitaly_parse_logs`, for RHGitaly logs format, except that
    we return `None` as `first_timestamp` (analysis not done yet, TODO)
    """
    called = defaultdict(lambda: 0)
    succeeded = defaultdict(list)
    first_timestamp = None
    for line in fobj:
        m = RHGITALY_SPAN_CLOSE_RX.search(line)

        if m is None:
            continue
        if first_timestamp is None:
            log_dt = m.group(1)
            if since is not None:
                # RHGitaly log date/times are always in full ISO format
                # (with 'T' and 'Z'). Some Python versions don't understand
                # the use of commas, though
                dt = datetime.fromisoformat(log_dt.replace(',', '.'))
                if dt < since:
                    continue
            first_timestamp = log_dt
        req = m.group(2)
        called[req] += 1
        # TODO dectect request failures
        succeeded[req].append(
            float(m.group(4)) * unit_multipliers_to_millis[m.group(5)])
        continue

    dict_snake_case_to_camel(called)
    dict_snake_case_to_camel(succeeded)
    return first_timestamp, called, succeeded


def stats():  # pragma no cover
    parser = argparse.ArgumentParser(
        description="Analyse HGitaly logs and output statistics by method",
    )
    parser.add_argument('log_path',
                        help="Path to the log file to analyse. "
                        "Use `-` for `stdin`")
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--rhgitaly', action='store_true')
    parser.add_argument('--since',
                        help="Filter the logs from the given date, "
                        "that must be in UTC ISO-8601 format with time zone")
    parser.add_argument('--sort-by', choices=('calls',
                                              'incomplete',
                                              'timing:mean',
                                              'timing:median',
                                              'timing:worst_decile',
                                              'timing:worst_centile',
                                              'timing:total',
                                              ),
                        default='calls')

    cl_args = parser.parse_args()
    log_path = cl_args.log_path
    rhgitaly = cl_args.rhgitaly

    called = defaultdict(lambda: 0)
    succeeded = defaultdict(list)

    if rhgitaly:
        parse = rhgitaly_parse_logs
    else:
        parse = hgitaly_parse_logs

    if log_path == '-':
        logf = sys.stdin
    else:
        logf = open(log_path)

    if cl_args.since is None:
        since = None
    else:
        try:
            since = datetime.fromisoformat(cl_args.since)
        except ValueError:
            parser.error("--since must be given in ISO-8601 format")
        if since.tzinfo is None and ISOFORMAT_WITH_TZ:
            parser.error("--since must be given with timezone, "
                         "usually just 'Z' for UTC")
    with logf:
        first_timestamp, called, succeeded = parse(logf, since=since)

    total_requests = sum(called.values())
    incomplete = total_requests - sum(len(succ) for succ in succeeded.values())

    stats = []
    for req, count in called.items():
        percent = round(count * 100 / total_requests)
        succ = succeeded[req]
        nb_succ = len(succ)
        req_stats = dict(percent=percent,
                         calls=count,
                         complete=nb_succ,
                         incomplete=count - nb_succ,
                         )
        stats.append((req, req_stats))
        if nb_succ > 0:
            timing = req_stats['completion_stats_ms'] = dict(
                mean=statistics.mean(succ),
                median=statistics.median(succ),
                total=sum(s for s in succ),
            )
            if nb_succ > 1:
                timing['standard_deviation'] = statistics.pstdev(succ)
                deciles = statistics.quantiles(succ, method='inclusive', n=10)
                centiles = statistics.quantiles(succ, method='inclusive',
                                                n=100)
                timing['best_centile'] = centiles[0]
                timing['best_decile'] = deciles[0]
                timing['worst_decile'] = deciles[-1]
                timing['worst_centile'] = centiles[-1]

    sort_key = cl_args.sort_by
    if sort_key.startswith('timing:'):
        sort_key = ('completion_stats_ms', sort_key.split(':', 1)[-1])

    def sort_key_function(req_stats):
        stats = req_stats[1]
        if isinstance(sort_key, str):
            return -stats.get(sort_key, 0)

        stats = stats.get(sort_key[0])
        if stats is None:
            return 0
        return -stats.get(sort_key[1], 0)

    stats.sort(key=sort_key_function)
    stats = dict(stats)

    if cl_args.json:
        print(json.dumps(stats))
        return

    print(f"TOTAL Requests since {first_timestamp}: {total_requests} \n"
          f"      {incomplete} incomplete (cancelled or failed)")
    print("Breakdown:")
    for req, details in stats.items():
        percent = '%4.1f' % details['percent']
        time_stats = details.get('completion_stats_ms')
        if time_stats is None:
            print(f"  {percent}% {req} "
                  f"(called={details['calls']}, "
                  f"incomplete={details['incomplete']} (timing N/A)")
            continue
        time_stats = details['completion_stats_ms']
        mean = time_stats['mean']
        avg_ms_str = '%.1f' % mean
        worst_decile_str = '%.1f' % time_stats.get('worst_decile', mean)
        print(f"  {percent}% {req} "
              f"(called={details['calls']}, "
              f"incomplete={details['incomplete']}, "
              f"average_time={avg_ms_str}ms, "
              f"worst_decile={worst_decile_str}ms)")
