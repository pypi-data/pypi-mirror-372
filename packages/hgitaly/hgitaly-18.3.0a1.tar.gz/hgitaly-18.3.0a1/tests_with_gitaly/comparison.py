# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixture for Gitaly comparison tests based on Heptapod's Git mirroring."""
import attr
import contextlib
from copy import deepcopy
import functools
from itertools import (
    islice,
)
import logging
import pytest
import random
import warnings

import grpc

from mercurial_testhelpers.util import as_bytes

from hggit.git_handler import GitHandler
from heptapod.testhelpers.gitlab import GitLabMirrorFixture
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)
from hgext3rd.heptapod.special_ref import (
    write_gitlab_special_ref,
    special_refs,
)
from hgitaly.errors import (
    STATUS_DETAILS_KEY,
    parse_structured_error,
)
from hgitaly import feature
from hgitaly import message
from hgitaly.errors import HGITALY_ISSUES_URL
from hgitaly.gitlab_ref import (
    keep_around_ref_path,
    parse_keep_around_ref_path,
)
from hgitaly.servicer import SKIP_HOOKS_MD_KEY
from hgitaly.stub.shared_pb2 import Repository
from hgitaly.testing.storage import (
    DEFAULT_STORAGE_NAME,
    storage_path,
    stowed_away_git_repo_path,
    stowed_away_git_repo_relpath,
)

try:
    from itertools import batched
except ImportError:  # Python<3.12
    def batched(it, n):
        # not sure in which version `while batch :=` is possible
        while True:
            batch = tuple(islice(it, n))
            if not batch:
                return
            yield batch

logger = logging.getLogger(__name__)


@attr.s
class GitalyComparison:
    hgitaly_channel = attr.ib()
    gitaly_channel = attr.ib()
    gitaly_repo = attr.ib()
    hgitaly_repo = attr.ib()
    gitlab_mirror = attr.ib()
    rhgitaly_channel = attr.ib(default=None)

    @property
    def hg_repo_wrapper(self):
        return self.gitlab_mirror.hg_repo_wrapper

    @property
    def git_repo(self):
        return self.gitlab_mirror.git_repo

    def rpc_helper(self, **kw):
        return RpcHelper(self, **kw)

    @functools.cached_property
    def hg_git(self):
        """The hg-git GitHandler instance, with SHA mapping preloaded.

        To invalidate this cached property, use :meth:`invalidate`
        """
        hg_repo = self.hg_repo_wrapper.repo
        hg_git = GitHandler(hg_repo, hg_repo.ui)
        hg_git.load_map()
        return hg_git

    def invalidate(self):
        """Invalidate all caches.

        In particular, reload the Mercurial repo
        """
        try:
            del self.hg_git
        except AttributeError:
            # the cached property has not been used yet, nothing to do
            pass

        self.hg_repo_wrapper.reload()
        self.gitlab_mirror.activate_mirror()

    def write_special_ref(self, ref_name, hg_sha):
        """Write a special ref in both repos

        :param ref_name: the special ref name (without `refs/`)
        :param bytes hg_sha: hexadecimal Mercurial Node ID of the changeset
          to point to

        :return: a pair of :class:`bytes` instance: (full ref path, git_sha)
        """
        git_sha = self.hg_git.map_git_get(hg_sha)
        if git_sha is None:
            raise LookupError("Git commit not found for %r" % hg_sha)

        hg_wrapper = self.hg_repo_wrapper
        git_repo = self.git_repo

        ref_path = b'refs/' + ref_name
        self.git_repo.write_ref(ref_path.decode(), git_sha)
        write_gitlab_special_ref(hg_wrapper.repo, ref_name, hg_sha)
        hg_wrapper.reload()
        assert ref_path in git_repo.all_refs()
        assert ref_name in special_refs(hg_wrapper.repo)
        return ref_path, git_sha

    def create_keep_around(self, hg_sha):
        """Create a keep-around ref in both repos

        :param bytes hg_sha: hexadecimal Mercurial Node ID of the changeset
          to point to

        On the Git side, the keep-around is set for the Git commit
        corresponding to the Mercurial commit.

        :return: a pair of :class:`bytes` instances:
          (full Mercurial ref path, full Git ref path)
        """
        git_sha = self.hg_git.map_git_get(hg_sha)
        hg_wrapper = self.hg_repo_wrapper
        git_repo = self.git_repo

        hg_ref_path = keep_around_ref_path(hg_sha)
        git_ref_path = keep_around_ref_path(git_sha)

        create_keep_around(hg_wrapper.repo, hg_sha)
        git_repo.write_ref(git_ref_path, git_sha)
        hg_wrapper.reload()
        return hg_ref_path, git_ref_path


@contextlib.contextmanager
def gitaly_comparison_fixture(server_repos_root,
                              gitaly_channel,
                              grpc_channel,
                              monkeypatch,
                              rhgitaly_channel=None,
                              native=False,
                              ):
    common_relative_path = 'repo-' + hex(random.getrandbits(64))[2:]
    storage = DEFAULT_STORAGE_NAME

    if native:
        git_repo_rpath = stowed_away_git_repo_relpath(common_relative_path)
    else:
        git_repo_rpath = common_relative_path + '.git'

    gitaly_repo = Repository(relative_path=str(git_repo_rpath),
                             gl_repository='project-1234',
                             storage_name=storage)
    hgitaly_repo = Repository(relative_path=common_relative_path + '.hg',
                              storage_name=storage)

    hg_config = dict(phases=dict(publish=False),
                     ui=dict(username='Hgitaly Tests <hgitaly@heptapod.test>'),
                     heptapod={
                         'native': 'yes' if native else 'no',
                         'repositories-root': str(server_repos_root / storage),
                     },
                     extensions={name: '' for name in ('evolve',
                                                       'hggit',
                                                       'topic',
                                                       'hgitaly',
                                                       'heptapod')})
    with GitLabMirrorFixture.init(
            storage_path(server_repos_root),
            monkeypatch,
            common_repo_name=common_relative_path,
            hg_config=hg_config,
    ) as mirror:
        # configuration must be written in HGRC file, because
        # HGitaly server will load the repository independently.
        mirror.hg_repo_wrapper.write_hgrc(hg_config)
        mirror.activate_mirror()
        if native:
            mirror.git_repo.path = stowed_away_git_repo_path(
                server_repos_root,
                common_relative_path,
            )
        yield GitalyComparison(
            hgitaly_channel=grpc_channel,
            hgitaly_repo=hgitaly_repo,
            gitaly_channel=gitaly_channel,
            rhgitaly_channel=rhgitaly_channel,
            gitaly_repo=gitaly_repo,
            gitlab_mirror=mirror,
        )


class BaseRpcHelper:
    """Common helper for all comparisons.

    Will handle comparison between Gitaly and (HGitaly or RHGitaly) as well
    as comparison beween HGitaly and RHGitaly, or whatever comes next.

    :param streaming requests_with_header: yield a first request
      controlled by `first_request_sub_message`, and then as iterable of
      `dicts`
    :param streaming_request_field: produce a stream of requests by
       cutting a single incoming field into chunks.
    """

    def __init__(self, comparison, stub_cls, method_name, request_cls,
                 repository_arg=True,
                 request_defaults=None,
                 feature_flags=(),
                 streaming_requests_raw=False,
                 streaming_requests_with_header=None,
                 streaming_request_field=None,
                 streaming_request_chunk_size=1,
                 streaming=False):
        self.comparison = comparison
        self.stub_cls = stub_cls
        self.method_name = method_name
        self.request_cls = request_cls
        self.streaming = streaming
        self.streaming_request_field = streaming_request_field
        self.streaming_requests_raw = streaming_requests_raw
        self.streaming_requests_with_header = streaming_requests_with_header
        self.streaming_request_chunk_size = streaming_request_chunk_size
        self.repository_arg = repository_arg

        self.request_defaults = request_defaults
        self.streaming = streaming
        self.feature_flags = list(feature_flags)

        self.init_stubs()

    def init_stubs(self):
        """To be provided by subclasses."""
        raise NotImplementedError  # pragma no cover

    def grpc_metadata(self):
        mds = feature.as_grpc_metadata(self.feature_flags)
        mds.append((SKIP_HOOKS_MD_KEY, 'true'))
        return mds

    def stream_requests(self, **kwargs):
        to_stream = kwargs.pop(self.streaming_request_field, [])

        req = kwargs  # only for first request
        has_chunk = False
        for chunk in batched(iter(to_stream),
                             self.streaming_request_chunk_size):
            has_chunk = True
            req[self.streaming_request_field] = chunk
            yield self.request_cls(**req)
            req.clear()

        if not has_chunk:
            # If to_stream was empty, we need to yield at least one request
            # This can happen if the streaming field is optional, which is the
            # case with `UpdateRemoteMirror`
            yield self.request_cls(**req)

    def stream_requests_with_header(self, tail_requests=(), **kwargs):
        """Tailored for UserCommtiFiles. Could be useful elsewhere."""
        header_attr, header_cls = self.streaming_requests_with_header
        yield self.request_cls(**{header_attr: header_cls(**kwargs)})

        for req in tail_requests:
            yield self.request_cls(**req)

    def rpc(self, backend, **kwargs):
        if self.repository_arg:
            if backend == 'hg':
                kwargs.setdefault('repository', self.comparison.hgitaly_repo)
            else:
                kwargs.setdefault('repository', self.comparison.gitaly_repo)

        if self.streaming_request_field is not None:
            request = self.stream_requests(**kwargs)
        elif self.streaming_requests_raw:
            request = iter(kwargs['requests'])
        elif self.streaming_requests_with_header is not None:
            request = self.stream_requests_with_header(**kwargs)
        else:
            request = self.request_cls(**kwargs)

        meth = getattr(self.stubs[backend], self.method_name)
        metadata = self.grpc_metadata()
        if self.streaming:
            return [resp for resp in meth(request, metadata=metadata)]

        return meth(request, metadata=metadata)

    def apply_request_defaults(self, kwargs):
        defaults = self.request_defaults
        if defaults is not None:
            for k, v in defaults.items():
                kwargs.setdefault(k, v)

    def structured_errors_git_converter(self, fields, error_git_cls=None):
        """Return a function that is suitable for `to_git` in handler.

        This matches the common pattern of the structured error being
        an enum with subobject variants
        Only full hash string or bytes values are supported and lists of
        these are supported at this point

        :param fields: a list of :class:`dict`with keys:

          - `hg_field`: name of the variant for HGitaly
          - `git_field`: name of the variant for Gitaly,
                        defaults to `hg_field`
          - `git_cls`: variant class to use for Gitaly, defaults to the
                       received HGitaly variant class
          - `subfields`: list of names of fields in the varian to convert.
                         Use the `[]` suffix to specify that a field is
                         repeated.
        """
        def to_git(error):
            if error_git_cls is None:
                error_git_class = error.__class__  # pragma no cover
            else:
                error_git_class = error_git_cls
            for descr in fields:
                name = descr['hg_field']
                new_name = descr.get('git_field', name)
                if error.HasField(name):
                    subobj = getattr(error, name)
                    git_cls = descr.get('git_cls', subobj.__class__)
                    # direct assignment to repeated values is not possible
                    # so we copy in a dict and reinstantiate
                    subitems = message.as_dict(subobj)
                    for field in descr['subfields']:
                        repeated = field.endswith('[]')
                        if repeated:
                            field = field[:-2]
                        hg_val = subitems.get(field)
                        if hg_val is None:
                            continue  # pragma no cover

                        if repeated:
                            git_val = [self.hg2git(sha) for sha in hg_val]
                        else:
                            git_val = self.hg2git(hg_val)
                        subitems[field] = git_val
                    subobj = git_cls(**subitems)
                    return error_git_class(**{new_name: subobj})

            raise AssertionError("Unexpected error variant")  # pragma no cover

        return to_git

    def assert_compare_grpc_exceptions(self, exc0, exc1,
                                       same_details=True,
                                       vcses=('hg', 'git'),
                                       skip_structured_errors_issue=None,
                                       structured_errors_handler=None):
        """Comparison of exceptions once they are available.

        Singled out so that we can compare the errors provided by different
        gRPC methods, useful when we had to make a specific Mercurial method
        instead of just implementing some Gitaly method and still want to
        compare outcomes.
        """
        excs = [exc0, exc1]
        assert exc0.code() == exc1.code()
        if same_details:
            norm = self.error_details_normalizer
            details = [exc0.details(), exc1.details()]
            if norm is not None:  # pragma no cover
                for i, det in enumerate(details):
                    details[i] = norm(details[i], vcs=vcses[i])
            assert details[0] == details[1]

        # trailing metadata can bear a typed error gRPC message, which
        # is more important to compare than "details" (in the sense of
        # human-readable message), so let's insist on at least
        # having a tracking issue
        if skip_structured_errors_issue is None:
            # TODO check how to unskew that: RHGitaly currently adds
            # `content-length` and `date`, which Gitaly does not
            mds = [dict(exc.trailing_metadata()) for exc in (exc0, exc1)]
            for md in mds:
                md.pop('content-length', None)
                md.pop('date', None)
            if structured_errors_handler is not None:
                handler = structured_errors_handler
                # ignoring human-readable details, as they are much less
                # interesting and more volatile than the structured error
                # (and usually just repeat `exc.details()`)
                cls1 = handler[vcses[1] + '_cls']  # by default, git
                cls0 = handler.get(vcses[0] + '_cls', cls1)  # by default, hg
                handler_classes = [cls0, cls1]
                extracted = {}
                for i in range(2):
                    try:
                        code, _, error = parse_structured_error(
                            excs[i], handler_classes[i])
                        extracted[i] = dict(code=code, error=error)
                    except LookupError:  # pragma no cover
                        # unlikely case: caller is expecting structured errors
                        pass

                assert len(extracted) in (0, 2)  # None of them or both
                if extracted:
                    assert extracted[0]['code'] == extracted[1]['code']
                    if vcses[1] == 'git':
                        extracted[0]['error'] = handler['to_git'](
                            extracted[0]['error'])

                    norm = handler.get('normalizer')
                    if norm is not None:
                        norm(extracted[0]['error'])
                        norm(extracted[1]['error'])
                    assert extracted[0]['error'] == extracted[1]['error']

                # already done and a priori not directly comparable
                for md in mds:
                    md.pop(STATUS_DETAILS_KEY, None)
            assert mds[0] == mds[1]
        else:  # pragma no cover
            msg = ("Skipped comparison of structured errors, "
                   "until tracking issue %s/%d is done.") % (
                           HGITALY_ISSUES_URL, skip_structured_errors_issue)
            logger.warning(msg)
            warnings.warn(msg, RuntimeWarning)  # more visible in pytest output

        return exc0, exc1


class RpcHelper(BaseRpcHelper):
    """Encapsulates a comparison fixture with call and compare helpers.

    As Mercurial and Git responses are expected to differ (commit hashes and
    the like), this class provides a uniform mechanism to account for
    the expected difference, before finally asserting equality of
    the responses.

    # TODO much more to document.

    :attr:`feature_flags`: a mutable list of pairs such as
      ``(`my-flag`, True)``. The flags are sent to both servers.
    :attr:`response_sha_attrs`: Used to specify response attributes to
      convert to Git for comparison. See :meth:`attr_path_to_git` for
      specification.
    """

    def __init__(self, comparison, stub_cls, method_name, request_cls,
                 hg_server='hgitaly',
                 request_sha_attrs=(),
                 response_sha_attrs=(),
                 normalizer=None,
                 error_details_normalizer=None,
                 chunked_fields_remover=None,
                 chunks_concatenator=None,
                 **kwargs,
                 ):
        self.hg_server = hg_server
        super(RpcHelper, self).__init__(
            comparison, stub_cls, method_name, request_cls,
            **kwargs
        )
        self.request_sha_attrs = request_sha_attrs
        self.response_sha_attrs = response_sha_attrs
        self.normalizer = normalizer
        self.error_details_normalizer = error_details_normalizer
        self.chunked_fields_remover = chunked_fields_remover
        self.chunks_concatenator = chunks_concatenator

    def init_stubs(self):
        comparison, stub_cls = self.comparison, self.stub_cls

        if self.hg_server == 'rhgitaly':
            hg_channel = comparison.rhgitaly_channel
        else:
            hg_channel = comparison.hgitaly_channel
        self.stubs = dict(git=stub_cls(comparison.gitaly_channel),
                          hg=stub_cls(hg_channel))

    def hg2git(self, hg_sha):
        """Convert a Mercurial hex SHA to its counterpart SHA in Git repo.

        If not found in the Git Repo, the original SHA is returned, which
        is useful for tests about non existent commits.
        """
        # if hg_sha is None or not 40 bytes long it certainly won't
        # be found in the hg-git mapping, we don't need a special case
        # for that
        git_sha = self.comparison.hg_git.map_git_get(as_bytes(hg_sha))
        return hg_sha if git_sha is None else git_sha

    def normalize_keep_around(self, ref, vcs):
        if vcs != 'hg':
            return ref

        hg_sha = parse_keep_around_ref_path(ref)
        if hg_sha is None:
            # not a keep-around
            return ref
        return keep_around_ref_path(self.hg2git(hg_sha))

    def request_kwargs_to_git(self, hg_kwargs):
        # attr_path_to_git updates lists in place, because it needs
        # to do so in the case of scalar lists for Messages. Hence in the
        # case of dicts, we need to perform the deep copy.
        git_kwargs = deepcopy(hg_kwargs)
        sha_attr_paths = [path.split('.') for path in self.request_sha_attrs]
        for attr_path in sha_attr_paths:
            self.attr_path_to_git(git_kwargs, attr_path,
                                  accessor=lambda d, k: d.get(k),
                                  setter=lambda d, k, v: d.__setitem__(k, v),
                                  has_field=lambda d, f: f in d,
                                  )
        return git_kwargs

    def revspec_to_git(self, revspec):
        """Convert revision specifications, including ranges to Git.

        This is to be improved as new cases arise.
        """
        is_bytes = isinstance(revspec, bytes)
        symdiff_sep = b'...' if is_bytes else '...'
        only_sep = b'..' if is_bytes else '..'

        for sep in (symdiff_sep, only_sep):
            if sep in revspec:
                # hg2git() defaulting rule will let symbolic revisions, such
                # as refs go through untouched
                return sep.join(self.hg2git(rev)
                                for rev in revspec.split(sep))
        # TODO implement caret, tilda etc.
        return self.hg2git(revspec)

    def response_to_git(self, resp):
        sha_attr_paths = [path.split('.') for path in self.response_sha_attrs]
        if self.streaming:
            for msg in resp:
                self.message_to_git(msg, sha_attr_paths)
        else:
            self.message_to_git(resp, sha_attr_paths)

    def message_to_git(self, message, attr_paths, **kw):
        for attr_path in attr_paths:
            self.attr_path_to_git(message, attr_path, **kw)

    def attr_path_to_git(self, message, attr_path,
                         accessor=getattr,
                         setter=setattr,
                         has_field=lambda o, f: o.HasField(f),
                         ):
        """Convert to Git part of message specified by an attr_path.

        :param attr_path: symbolic representation, as a succession of dotted
          attribute names. In case an attribute name ends with ``[]``, it
          is expected to be a simple list on which to iterate.
          Examples:
          - ``id``: convert ``message.id``
          - ``commits[].id``: for each element ``c`` of ``message.commits``,
            convert  ``c.id``
          - ``commits[].parent_ids[]`: for each element ``c`` of
            ``message.commits``, convert  all values in ``c.parent_ids``
        """
        obj = message
        trav = list(attr_path)
        while len(trav) > 1:
            attr_name, trav = trav[0], trav[1:]
            recurse = attr_name.endswith('[]')
            if recurse:
                attr_name = attr_name[:-2]
            # HasField cannot be used on repeated attributes, hence the elif
            elif not has_field(obj, attr_name):
                return
            obj = accessor(obj, attr_name)
            if obj is None:  # can happen with an accessor for dicts
                continue  # pragma no cover TODO make unit tests for RpcHelper
            if recurse:
                for msg in obj:
                    # after traversal, we are sure to be on a Message instance
                    self.message_to_git(msg, [trav])
                return

        obj_attr = trav[0]
        scalar_list = obj_attr.endswith('[]')
        if scalar_list:
            obj_attr = obj_attr[:-2]
        value = accessor(obj, obj_attr)
        if value is None:
            return

        if scalar_list:
            for i, sha in enumerate(value):
                value[i] = self.revspec_to_git(sha)
        else:
            setter(obj, obj_attr, self.revspec_to_git(value))

    def call_backends(self, **hg_kwargs):
        """Call Gitaly and HGitaly with uniform request kwargs.

        To be used only if no error is expected.

        :param hg_kwargs: used as-is to construct the request for HGitaly,
          converted to Git and then to a request for Gitaly.
        """
        self.apply_request_defaults(hg_kwargs)

        git_kwargs = self.request_kwargs_to_git(hg_kwargs)

        git_response = self.rpc('git', **git_kwargs)
        hg_response = self.rpc('hg', **hg_kwargs)

        return hg_response, git_response

    def call_git_only(self, **hg_kwargs):
        """Call only Git, yet with Mercurial arguments.

        In some cases, comparison between Git and Mercurial is not directly
        possible (happens with mutations), but it is worthwile to check the
        assumptions on Gitaly behaviour that drive the HGitaly implementation.

        In that case, it is more convenient to take arguments as
        :meth:`assert_compare` does, hence providing conversion of arguments
        from Mercurial to Git.
        """
        self.apply_request_defaults(hg_kwargs)
        git_kwargs = self.request_kwargs_to_git(hg_kwargs)
        if self.repository_arg:
            git_kwargs.setdefault('repository', self.comparison.gitaly_repo)
        return self.rpc('git', **git_kwargs)

    def normalize_responses(self, hg_response, git_response):
        self.response_to_git(hg_response)
        norm = self.normalizer
        if norm is not None:
            norm(self, hg_response, vcs='hg')
            norm(self, git_response, vcs='git')

    def assert_compare(self, **hg_kwargs):
        hg_response, git_response = self.call_backends(**hg_kwargs)
        self.normalize_responses(hg_response, git_response)
        assert hg_response == git_response

    def assert_compare_aggregated(self,
                                  compare_first_chunks=True,
                                  check_both_chunked=True,
                                  **hg_kwargs):
        """Compare streaming responses with appropriate concatenation.

        Sometimes, it's unreasonable to expect HGitaly chunking to
        exactly match Gitaly's. This method allows to compare after
        regrouping the chunks, with the provided :attr:`chunks_concatenator`.

        Usually Gitaly returns small values within the first response only,
        to avoid the bandwidth waste of repetiting them. This helper
        checks that HGitaly does the same by comparing after applying
        :attr: `chunked_fields_remover` to as many responses as possible
        (typically the number of responses would differ).

        :param bool compare_first_chunk: if ``True``, the first chunks of
          both responses are directly compared (including main content). If
          ``False``, they are still compared, just ignoring main content.
        :param bool check_both_chunked: if ``True` checks that we get
          more than one response for both HGitaly and Gitaly
        :return: a pair: the first chunk of responses for Gitaly and HGitaly
          respectively, taken before normalization. This can be useful, e.g.,
          for pagination parameters.
        """
        assert self.streaming  # for consistency

        hg_resps, git_resps = self.call_backends(**hg_kwargs)
        original_first_chunks = deepcopy((git_resps[0], hg_resps[0]))

        self.normalize_responses(hg_resps, git_resps)
        if compare_first_chunks:
            assert hg_resps[0] == git_resps[0]

        if check_both_chunked:
            assert len(hg_resps) > 1
            assert len(git_resps) > 1

        concatenator = getattr(self, 'chunks_concatenator')
        fields_remover = getattr(self, 'chunked_fields_remover')
        assert concatenator(hg_resps) == concatenator(git_resps)

        for hg_resp, git_resp in zip(hg_resps, git_resps):
            if fields_remover is not None:
                fields_remover(hg_resp)
                fields_remover(git_resp)
            assert hg_resp == git_resp

        return original_first_chunks

    def assert_compare_errors(self, same_details=True,
                              skip_structured_errors_issue=None,
                              structured_errors_handler=None,
                              **hg_kwargs):
        """Compare errors returned by (R)HGitaly and Gitaly.

        :param:`structured_errors_handler`: if supplied, it is expected to be
          a :class:`dict` with the following keys:

          - `git_cls`: expected error class (gRPC message) from Gitaly
          - `hg_cls`: expected error class (gRPC message) from HGitaly
                      defaults to the value of `git_cls`
          - `to_git`: conversion callable from HGitaly's gRPC error message
            to Gitaly's
          - `git_normalizer`: additional normalizer to apply to Git error
            (some of them involve objects that cannot exist on the Mercurial
             side)
        """
        self.apply_request_defaults(hg_kwargs)

        git_kwargs = self.request_kwargs_to_git(hg_kwargs)
        with pytest.raises(grpc.RpcError) as exc_info_git:
            self.rpc('git', **git_kwargs)
        with pytest.raises(grpc.RpcError) as exc_info_hg:
            self.rpc('hg', **hg_kwargs)
        self.assert_compare_grpc_exceptions(
            exc_info_hg.value,
            exc_info_git.value,
            same_details=same_details,
            skip_structured_errors_issue=skip_structured_errors_issue,
            structured_errors_handler=structured_errors_handler,
        )


def normalize_commit_message(commit):
    """Remove expected differences between commits in Gitaly and HGitaly.

    Some are really testing artifacts, some have eventually to be removed.
    """
    # TODO tree_id should be replaced by HGitaly standard value
    # once HGitaly2 is the norm
    commit.tree_id = ''

    # hg-git may add a branch marker (this is just a test artifact)
    hg_marker = b'\n--HG--\n'
    split = commit.body.split(hg_marker, 1)
    if len(split) > 1:
        commit.body = split[0]
        commit.body_size = commit.body_size - len(split[1]) - len(hg_marker)

    # Either hg-git or Git itself adds a newline if there isn't one.
    # TODO investigate and if it is Git, add the newline in Mercurial
    # response.
    if not commit.body.endswith(b'\n'):
        commit.body = commit.body + b'\n'
        commit.body_size = commit.body_size + 1
