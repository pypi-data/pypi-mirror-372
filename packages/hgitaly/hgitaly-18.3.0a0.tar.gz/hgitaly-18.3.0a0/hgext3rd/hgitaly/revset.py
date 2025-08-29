import re

from mercurial import (
    error,
    registrar,
    revsetlang,
)
from mercurial.i18n import _
from mercurial.utils import (
    stringutil,
)

getstring = revsetlang.getstring

revsetpredicate = registrar.revsetpredicate()


@revsetpredicate(b'hpd_dsc_rx', weight=10)
def hpd_dsc_rx(repo, subset, x, re_flags=0):
    """Variant of the core `grep` revset suitable for `commit_message_patterns`

    It matches changeset descriptions only. The same function can be used
    for variants, thanks to :param re_flags:

    The name is short for: "HePtapoD DeSCription Regular eXpression", with
    the ``hpd_`` prefix to indicate that it is Heptapod specific.

    Notes:
    - as of Mercurial 6.3, dashes wouldn't work in predicate names,
      leading to the obscure "unknown revision 'hpd'" error message.
    - the ``re.NOFLAG`` constant was introduced in Python 3.11, which is not
      yet supported by HGitaly.
    """
    try:
        rx = re.compile(getstring(x, _(b"hpd_dsc_rx requires a string")),
                        flags=re_flags)
    except re.error as e:
        raise error.ParseError(
            _(b'invalid regexp pattern: %s') % stringutil.forcebytestr(e)
        )

    def matches(x):
        return rx.search(repo[x].description()) is not None

    return subset.filter(matches, condrepr=(b'<hpd_dsc_rx %r>', rx.pattern))


@revsetpredicate(b'hpd_dsc_irx', weight=10)
def hpd_dsc_irx(repo, subset, x):
    """Case-insensitive variant of hpd_dsc_rx"""
    return hpd_dsc_rx(repo, subset, x, re_flags=re.IGNORECASE)
