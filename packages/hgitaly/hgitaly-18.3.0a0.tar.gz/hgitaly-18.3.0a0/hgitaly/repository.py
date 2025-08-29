# Copyright 2021-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import re
import subprocess

from mercurial import (
    commands,
    pycompat,
    ui as uimod,
)

from .stub.mercurial_repository_pb2 import (
    HeptapodConfigSection,
)

AutoPublish = HeptapodConfigSection.AutoPublish
CloneBundles = HeptapodConfigSection.CloneBundles

GITLAB_PROJECT_FULL_PATH_FILENAME = b'gitlab.project_full_path'
MAIN_HGRC_FILE = b'hgrc'
MANAGED_HGRC_FILE = b'hgrc.managed'
INCLUDE_MANAGED_HGRC_LINE = b'%include ' + MANAGED_HGRC_FILE
HGRC_INCL_INHERIT_RX = re.compile(br'^%include (.*)/hgrc$', re.MULTILINE)
HEPTAPOD_CONFIG_SECTION = b'heptapod'
# TODO would be nice to import these from hgext3rd.heptapod
HEPTAPOD_CONFIG_AUTO_PUBLISH = b'auto-publish'
HEPTAPOD_CONFIG_CLONE_BUNDLES = b'clone-bundles'
HEPTAPOD_CONFIG_ALLOW_BOOKMARKS = b'allow-bookmarks'
HEPTAPOD_CONFIG_ALLOW_MULTIPLE_HEADS = b'allow-multiple-heads'
AUTO_PUBLISH_MAPPING = {
    b'without-topic': AutoPublish.WITHOUT_TOPIC,
    b'nothing': AutoPublish.NOTHING,
    b'all': AutoPublish.ALL,
}
AUTO_PUBLISH_REVERSE_MAPPING = {v: k for k, v in AUTO_PUBLISH_MAPPING.items()}
CLONE_BUNDLES_MAPPING = {
    b'disabled': CloneBundles.DISABLED,
    b'explicit': CloneBundles.EXPLICIT,
    b'on-change': CloneBundles.ON_CHANGE,
}
CLONE_BUNDLES_REVERSE_MAPPING = {
    v: k for k, v in CLONE_BUNDLES_MAPPING.items()
}


def unbundle(repo, bundle_path: str, rails_sync=False):
    """Call unbundle with proper options and conversions.

    :param bool rails_sync: if ``True``, let the synchronization with the
       Rails app proceed (conversion to Git if needed, pre/post-receive hooks,
       etc.)
    """
    # make sure obsmarker creation is allowed while unbundle
    overrides = {(b'experimental', b'evolution'): b'all',
                 }
    if not rails_sync:
        overrides[(b'hooks', b'pretxnclose.heptapod_sync')] = b''

    # TODO it would be nice to have UPSTREAM a method
    # to unbundle from an arbitrary file-like object rather than
    # paths forcing us to dump to disk
    with repo.ui.configoverride(overrides, b'hgitaly.unbundle'):
        commands.unbundle(repo.ui, repo, pycompat.sysbytes(bundle_path))


def config_inherits(repo) -> bool:
    """Tell whether repo inherits configuration from its group."""
    hgrc = repo.vfs.tryread(MAIN_HGRC_FILE)
    if not hgrc:  # can be None or empty string for missing files
        return False

    return HGRC_INCL_INHERIT_RX.search(hgrc) is not None


def config_message_bool_from_ui(fields, ui, protocol_key, config_key,
                                as_recorded=False):
    default_opts = {}
    if as_recorded:
        default_opts['default'] = None

    value = ui.configbool(HEPTAPOD_CONFIG_SECTION, config_key, **default_opts)
    if value is None:
        return

    fields[protocol_key] = value


def heptapod_ui_config(ui, as_recorded=False) -> HeptapodConfigSection:
    """Convert the config from `ui` instance to message.

    :param as_recorded: if ``True``, values that are not explicitly set in
      config are not returned.
    """
    fields = {}

    auto_pub = ui.config(HEPTAPOD_CONFIG_SECTION, HEPTAPOD_CONFIG_AUTO_PUBLISH)

    if auto_pub is not None or not as_recorded:
        fields['auto_publish'] = AUTO_PUBLISH_MAPPING.get(auto_pub)

    clone_bundles = ui.config(HEPTAPOD_CONFIG_SECTION,
                              HEPTAPOD_CONFIG_CLONE_BUNDLES)

    if clone_bundles is not None or not as_recorded:
        fields['clone_bundles'] = CLONE_BUNDLES_MAPPING.get(clone_bundles)

    for field, key in (
            ('allow_multiple_heads', HEPTAPOD_CONFIG_ALLOW_MULTIPLE_HEADS),
            ('allow_bookmarks', HEPTAPOD_CONFIG_ALLOW_BOOKMARKS),
    ):
        config_message_bool_from_ui(fields, ui, field, key,
                                    as_recorded=as_recorded)

    return HeptapodConfigSection(**fields)


def heptapod_config(repo) -> HeptapodConfigSection:
    """Return the `heptapod` configuration section, as seen by Mercurial.

    These are the fully resolved value, hence taking Group inheritance into
    account.
    """
    return heptapod_ui_config(repo.ui)


def heptapod_local_config(repo) -> HeptapodConfigSection:
    """Return the configuration spectific to this repository.

    It ignores global settings and those from the main HGRC, hence in
    particular what could be inherited from a Group.
    """
    ui = uimod.ui()
    ui.readconfig(repo.vfs.join(MANAGED_HGRC_FILE), trust=True)
    return heptapod_ui_config(ui, as_recorded=True)


def replace_heptapod_managed_config(repo, items, by_line):
    """Entirely replace the managed HGRC file with the given items.

    :param items: a dict, whose keys and values are as fields of the
      :class:`HeptapodConfigSection` message
    """
    with repo.wlock():
        with repo.vfs(MANAGED_HGRC_FILE,
                      mode=b'wb',
                      atomictemp=True,
                      checkambig=True) as fobj:
            fobj.write(b"# This file is entirely managed by Heptapod \n")
            fobj.write(b"# latest update ")
            fobj.write(by_line.encode('utf-8'))
            fobj.write(b"\n\n")

            if not items:
                return

            fobj.write(b"[heptapod]\n")
            auto_pub = items.get('auto_publish')
            if auto_pub is not None:
                fobj.write(b"auto-publish = ")
                fobj.write(AUTO_PUBLISH_REVERSE_MAPPING[auto_pub])
                fobj.write(b"\n")

            clone_bundles = items.get('clone_bundles')
            if clone_bundles is not None:
                fobj.write(b"clone-bundles = ")
                fobj.write(CLONE_BUNDLES_REVERSE_MAPPING[clone_bundles])
                fobj.write(b"\n")

            for field in ('allow_bookmarks', 'allow_multiple_heads'):
                val = items.get(field)
                if val is None:
                    continue

                hg_key = field.replace('_', '-')
                fobj.write(f'{hg_key} = {val}\n'.encode('ascii'))


def ensure_managed_config_inclusion(repo):
    with repo.wlock():
        for line in repo.vfs.tryread(MAIN_HGRC_FILE).splitlines():
            if line.strip() == INCLUDE_MANAGED_HGRC_LINE:
                return

        with repo.vfs(MAIN_HGRC_FILE,
                      mode=b'ab',
                      atomictemp=True,
                      checkambig=True) as fobj:
            fobj.write(INCLUDE_MANAGED_HGRC_LINE)
            fobj.write(b"\n")


def set_managed_config(repo, heptapod: HeptapodConfigSection,
                       remove_items, by_line):
    existing = heptapod_local_config(repo)
    items = {}
    for field in ('allow_bookmarks', 'allow_multiple_heads',
                  'auto_publish', 'clone_bundles'):
        if field in remove_items:
            continue

        if heptapod.HasField(field):
            items[field] = getattr(heptapod, field)
        elif existing.HasField(field):
            items[field] = getattr(existing, field)
    replace_heptapod_managed_config(repo, items, by_line)
    ensure_managed_config_inclusion(repo)


def set_config_inheritance(repo, hgrc_dir, by_line):
    """Set inheritance from an HGRC file in given hgrc_dir.

    :param hgrc_dir: if None, the inheritance is removed if present.
      Otherwise has to be a relative path from the repo's wdir and
      if inheritance is absent, it is set to the file named ``hgrc``
      in the given ``hgrc_dir``.

    Tis currrenl
    """
    by_line = by_line.encode('utf-8')
    changed = False
    with repo.wlock():
        lines = repo.vfs.tryread(MAIN_HGRC_FILE).splitlines()
        for i, line in enumerate(lines):
            if HGRC_INCL_INHERIT_RX.search(line) is not None:
                if hgrc_dir is None:
                    lines[i] = b'# inheritance removed ' + by_line
                    changed = True
                break
        else:
            if hgrc_dir is not None:
                lines.insert(0,
                             b'%%include %s/hgrc' % hgrc_dir.encode('utf-8'))
                lines.insert(0, b'# inheritance restored ' + by_line)
                changed = True

        if not changed:
            return

        with repo.vfs(MAIN_HGRC_FILE,
                      mode=b'wb',
                      atomictemp=True,
                      checkambig=True) as fobj:
            for line in lines:
                fobj.write(line)
                fobj.write(b'\n')


def repo_size(repo):
    """Return repository size in kilobytes"""
    out = subprocess.check_output(('du', '-ks', os.fsdecode(repo.path)))
    return int(out.split()[0].decode('ascii'))
