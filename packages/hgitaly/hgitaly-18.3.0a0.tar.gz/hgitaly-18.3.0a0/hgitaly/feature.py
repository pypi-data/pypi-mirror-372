# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import grpc
import os

# for now, we can simply list all the feature flags that we support
# later on, we'll probably want an automatic extraction: it's not
# hard if we require an either from
# Golang definition or from the Rails app repository. The latter
# is easier, because of YaML format. We could even copy them over.
#
# Note: we see no problem within this Python code to use dash
# as separator. No need to go back and forth between dashes and underscores
# as the Golang implementation does. In Ruby case, the underscores have the
# advantage of being usable as symbols without any quotes.
FEATURE_FLAGS = {  # name -> default value
    'find-tag-structured-error': False,
    'simplify-find-local-branches-response': False,
}
GRPC_PREFIX = 'gitaly-feature-'
ALL_ENABLED = (
    os.environ.get('GITALY_TESTING_ENABLE_ALL_FEATURE_FLAGS') == 'true'
)


class UndefinedError(LookupError):
    """Exception used to qualify query of undefined feature flag.

    This is about HGitaly code querying the value of undefined flag, not
    about incoming requests bearing unknown feature flags.

    In most cases, that means the feature flag has to be defined.
    """


def is_enabled(context: grpc.ServicerContext, name: str) -> bool:
    """Return whether a given feature flag is enabled

    This is meant for HGitaly servicer code.

    :raises UndefinedError: if the feature flag is not defined. This strict
      policy is made possible by the fact that this method is not used to
      validate incoming feature flags (we expect to ignore many of them),
      rather as a HGitaly service method implementation expecting a
      feature flag to exist, given in litteral form. This will break the
      service tests if a feature flag has just been removed and the caller has
      not (yet). With our 100% coverage policy, this is not a hazard for
      production: all calls to `is_enabled` are covered.
    """
    if ALL_ENABLED:
        if name not in FEATURE_FLAGS:
            raise UndefinedError(name)
        return True

    md_key = GRPC_PREFIX + name
    md = dict(context.invocation_metadata())
    val = md.get(md_key)
    if val is None:
        try:
            return FEATURE_FLAGS[name]
        except KeyError:
            raise UndefinedError(name)

    return val == 'true'


def as_grpc_metadata(flag_values):
    if flag_values is None:
        return None

    return [((GRPC_PREFIX + k).encode('ascii'), b'true' if v else b'false')
            for k, v in flag_values]
