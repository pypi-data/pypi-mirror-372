# HGitaly

HGitaly is Gitaly server for Mercurial.

It implements the subset of the Gitaly gRPC protocol that is relevant for
Mercurial repositories, as well as its own HGitaly protocol, with methods
that are specific to Mercurial.

It comes in two overlapping variants:

- HGitaly proper is written in Python, using the `grpcio` official library.
- RHGitaly is a high-performance partial implementation written in Rust, and
  based on the [`tonic`](https://crates.io/crates/tonic) gRPC framework.

  As of Heptapod 18.0, RHGitaly is able to treat all requests, sometimes by
  deferring to HGitaly. All clients should be configured to target RHGitaly,
  but a HGitaly service must still exist, and RHGitaly must be configured
  with the address of the HGitaly server. We have [plans](hgitaly#235)
  to make HGitaly become a sidecar of RHGitaly.

## Installation

### HGitaly (Python)

In what follows, `$PYTHON` is often the Python interpreter in a virtualenv,
but it can be a system-wide one (typical case in containers, strongly
discouraged on user systemes).

1. Install Mercurial with Rust parts (for the exact version, refer to the
   requirements file in the Heptapod main repository sources)

   ```
   $PYTHON -m pip install --no-use-pep517 --global-option --rust Mercurial==6.6.2
   ```

2. Install HGitaly itself (check that it does not reinstall Mercurial)

   ```
   $PYTHON -m pip install hgitaly
   ```

### RHGitaly

We distribute a self-contained source tarball. It includes the appropriate
`hg-core` Rust sources.

1. Fetch the tarball

   ```
   wget https://download.heptapod.net/rhgitaly/rhgitaly-x.y.z.tgz
   ```

2. Fetch and verify the GPG signature

   ```
   wget https://download.heptapod.net/rhgitaly/rhgitaly-x.y.z.tgz.asc
   gpg --verify rhgitaly-x.y.z.tgz.asc
   ```

3. Build

   ```
   tar xzf rhgitaly-x.y.z.tgz
   cd rhgitaly-x.y.z/rust
   cargo build --locked --release
   ```

4. Install wherever you want. Example given for a system-wide installation

   ```
   sudo install -o root -g root target/release/rhgitaly /usr/local/bin
   ```

5. Define a service. Example given for systemd, to be adjusted for your needs.
   Make sure in particular that user and all directories exist, with
   appropriate permissions.

   ```
   [Unit]
   Description=Heptapod RHGitaly Server

   [Service]
   User=hgitaly
   Environment=HGRCPATH=/etc/heptapod/heptapod.hgrc
   Environment=RHGITALY_LISTEN_URL=unix:/run/heptapod/rhgitaly.socket
   Environment=RHGITALY_REPOSITORIES_ROOT=/home/hg/repositories
   Environment=RHGITALY_HG_EXECUTABLE=/usr/local/bin/hg
   Environment=RHGITALY_SIDECAR_ADDRESS=http://127.0.0.1:9237
   Environment=RHGITALY_CONFIG_DIRECTORY=/home/hg/repositories/+hgitaly
   ExecStartPre=rm -f /run/heptapod/rhgitaly.socket
   ExecStart=/user/local/bin/rhgitaly
   Restart=on-failure

   [Install]
   WantedBy=default.target
   ```

### External executables

HGitaly needs several other programs to be installed and will run them
as separate processes.

By default, it expects to find them on `$PATH`, but the actual path to
each executable can be configured.

#### Tokei

As of Heptapod 18.0, the `tokei` executable is no longer necessary, as
RHGitaly provides a direct implementation, using `tokei` as a library (hence
an internal dependency, resolved at compilation).

[Tokei](https://crates.io/crates/tokei) is a programming languages analysis
tool written in Rust. It is used by the [CommitLanguages](protos/commit.proto)
method of HGitaly (python), which should now be in use only in Comparison
Tests.

Tokei is available in several Linux distributions.

As of this writing, HGitaly supports versions 12.0 and 12.1

#### Go license-detector

Usually installed as `license-detector`, this standalone executable is
part of the `go-enry` suite. Its library version is also used by Gitaly.

It is used in the [FindLicense](protos/repository.proto) method.

#### Git

HGitaly can make use of some Git commands that do not involve repositories!
This is for example the case of [GetPatchID](protos/diff.proto): the
`git patch-id` command does not access any repository. Instead it computes any
patch into an identifier.

RHGitaly spawns Git subprocesses for operations on the auxiliary Git repository
used for mirroring to Git. For instance, this is how the `git push` part of
the mirroring is implemented.

The path to the `git` executable can be configured with the
`RHGITALY_GIT_EXECUTABLE` enviroment variable (defaulting to just `git`).

#### Mercurial

RHGitaly can invoke Mercurial subprocesses for various operations that
are better accomodated this way.

The Mercurial executable is configured by the mandatory
`RHGITALY_HG_EXECUTABLE` environment variable.

### Configuration

HGitaly's configuration is done the standard way in the Mercurial world:
through HGRC files.

In a typical Heptapod installation, these are split into a managed file, for
consistency with other components and another one for edit by the systems
administrator (`/etc/gitlab/heptapod.hgrc` in Omnibus/Docker instances).

Many Mercurial tweaks are interpreted simply because HGitaly internally
calls into Mercurial, but HGitaly also gets its own section. Here are the
settings available as of HGitaly 1.1

```
[hgitaly]
# paths to external executables
tokei-executable = tokei
license-detector-executable = license-detector
git-executable = git

# The number of workers process default value is one plus half the CPU count.
# It can be explicitly set this way:
#workers = 4

# Time to let a worker finish treating its current request, if any, when
# gracefully restarted. Default is high because of backup requests.
worker.graceful-shutdown-timeout-seconds = 300
# Maximum allowed resident size for worker processes (MiB).
# They get gracefully restarted if they cross that threshold
worker.max_rss_mib = 1024
# Interval between memory monitoring of workers (results dumped in logs)
worker.monitoring-interval-seconds = 60
```

Also `heptapod.repositories-root` is used if `--repositories-root` is
not passed on the command line.

## Operation

### Logging

HGitaly is using the standard `logging` Python module, and the
`loggingmod` Mercurial extension to emit logs from the Mercurial core
and other extensions. Therefore, the logging configuration is done
from the Mercurial configuration, typically from one of the Heptapod
HGRC files.

The general convention is that all logs emitted by `hgitaly.service`
provide GitLab's `correlation_id` in the `extra` dict, making it
available in the format string. Here is a minimal example:

```
[correlation_id=%(correlation_id)s] [%(levelname)s] [%(name)s] %(message)s"
```

Conversely, the format strings for logs emitted outside of
`hgitaly.service` must not use `correlation_id`, as subpackages such as
`hgitaly.branch`, `hgitaly.message`, etc. cannnot provide a
value: it is a hard error to use a format that relies on some
extra if the emitter does not provide it.

To summarize the resulting policy:

- in `hgitaly.service`, all logging must be done through
  `hgitaly.logging.LoggerAdapter`. Using `correlation_id` in the
  format is strongly encouraged.
- outside of `hgitaly.service`, logging should be self-contained
  useful without an obvious link to the calling gRPC method. For
  instance a repository inconsistency should be logged at `WARNING`
  level, with a message including the path.

## Development

### Automated tests and Continuous Integration

#### How to run the tests

Usually, that would be in a virtualenv, but it's not necessary.

```
  python3 -m pip install -r test-requirements.txt
  ./run-all-tests
```

Hint: Check the contents of `run-all-tests`, it's just `pytest` with
a standard set of options (mostly for coverage, see below).

#### Unit and Mercurial integration tests

These are the main tests. They lie inside the `hgitaly`
and `hgext3rd.hgitaly` Python packages. The layout follows the style where
each subpackage has its own tests package, to facilitate future refactorings.

The Mercurial integration tests are written with the [mercurial-testhelpers]
library. Their duty is to assert that HGitaly works as expected and maintains
compatibility with several versions of Mercurial and possibly other
dependencies, such as [grpcio].

The implicit assumption with these tests is that the test authors actually
knew what was expected. HGitaly being meant to be a direct replacement, or
rather a translation of Gitaly in Mercurial terms, those expectation are
actually a mix of:

- Design choices, such as mapping rules between branch/topic combinations
  and GitLab branches.
- Gitaly documentation and source code.
- sampling of Gitaly responses.

#### Gitaly comparison tests

If an appropriate Gitaly installation is found, `run-all-tests` will also
run the tests from the `tests_with_gitaly` package. This happens automatically
from within a [HDK] workspace.

These are precisely meant for what the Mercurial integration tests can't do:
check that HGitaly responses take the form expected by the various Gitaly
clients, by comparing directly with the reference Gitaly implementation.

The comparisons work by using the conversions to Git provided by
`py-heptapod`, which are precisely what HGitaly aims to replace as a mean
to expose Mercurial content to GitLab.

Once there is no ambiguity with what Gitaly clients expect, the correctness
of the implementation, with its various corner cases,
should be left to the Mercurial integration tests.

#### Test coverage

This project is being developed with a strong test coverage policy, enforced by
CI: without the Gitaly comparison tests, the coverage has to stay at 100%.

This does not mean that a contribution has to meet this goal to be worthwile,
or even considered. Contributors can expect Maintainers to help them
achieving the required 100% coverage mark, especially if they are newcomers.
Of course, Contributors cannot expect Maintainers to go
as far as write missing tests for them, even if that can still happen
for critical urgent issues.

Selected statements can of course be excluded for good reasons, using
`# pragma no cover`.

Coverage exclusions depending on the Mercurial version are
provided by the coverage plugin of [mercurial-testhelpers].

Unexpected drop of coverage in different Mercurial versions is a powerful
warning system that something not obvious is getting wrong, but the
Gitaly comparison tests are run in CI against a fixed set of
dependencies, hence 100% coverage must be achieved without the Gitaly
comparison tests.

On the other hand, Gitaly comparison tests will warn us when we bump upstream
GitLab if some critical behaviour has changed.

#### Tests Q&A and development hints

##### Doesn't the 100% coverage rule without the Gitaly comparison tests mean writing the same tests twice?

In some cases, yes, but it's limited.

For example, the comparison tests
can tell us that the `FindAllBranchNames` is actually expected to return
GitLab refs (`refs/heads/some-branch`), not GitLab branch names. That can
be settled with a few, very basic, test cases. There is no need to test all
the mapping rules for topics, and even less the various related corner cases
in the comparison tests. These, on the other hand depend strongly on Mercurial
internals, and absolutely have to be fully tested continuously against various
Mercurial versions.

Also, it is possible to deduplicate scenarios that are almost identical in
Mercurial integration tests and Gitaly comparison tests: factorize out the
common code in a helper function made available for both. The question is if
it is worth the effort.

Finally, comparison tests should focus on the fact that Gitaly and HGitaly
results agree, not on what they contain. In the above example,
a comparison for `FindAllBranchNames` could simply assert equality of the
returned sets of branch names. This is a bit less cumbersome, and easier
to maintain.

#### How to reproduce a drop in coverage found by the `compat` CI stage?

These are often due to statements being covered by the Gitaly comparison
tests only, leading to 100% coverage in the `main` stage, but not in the
`compat` stage.

The first thing to do is to run without the Gitaly comparison tests:

```
SKIP_GITALY_COMPARISON_TESTS=yes ./run-all-tests
```

(any non empty value in that environment variable, even `no` or `false` will
trigger the skipping)

In some rare cases, the drop in coverage could be due to an actual change
between Mercurial versions. If that happens, there are good chances that an
actual bug is lurking around.

#### How to run the tests with coverage of the Gitaly comparison tests

```
./run-all-tests --cov tests_with_gitaly --cov-report html
```

The HTML report will be nice if you don't have 100% coverage. To display it,
just do

```
firefox htmlcov/index.html
```

By default, the Gitaly comparison tests themselves are not covered, indeed.
This is because `run-all-tests` does not know whether they will be skipped for
lack of a Gitaly installation – which would be legitimate.

But they *are* covered in the CI jobs that launch them, because Gitaly is
assumed to be available. For these, the coverage would tell us that something
was broken, preventing the tests to run.

#### How to poke into Gitaly protocol?

The Gitaly comparison tests provide exactly a harness for that: take a test,
modify it as needed, insert a `pdb` breakpoint, and get going.

The big advantage here is that startup of the Gitaly comparison tests is
almost instantaneous, especially compared with RSpec, wich takes about a minute
to start even a completely trivial test.

Of course that will raise the question whether it'll be useful to make true
tests of these experiments.

#### When is a Gitaly comparison test required?

Each time there's a need to be sure of what's expected and it can help answer
that question. It doesn't have to do more than that.

#### When to prefer writing RSpec tests in Heptapod Rails over Gitaly comparison tests in HGitaly?

If you need to make sure that Heptapod Rails, as a Gitaly client, sends
the proper requests, because that can depend on specific dispatch code.

For instance, we are currently still converting to Git on the Rails side.
A source of bugs would be to send Git commit ids to HGitaly.

Apart from that, it is expected to be vastly more efficient to use
Gitaly comparison tests.

The more Heptapod progresses, the less complicated all of this should be.

## Updating the Gitaly gRPC protocol

The virtualenv has to be activated

1. `pip install -r dev-requirements.txt`

2. Copy the new `proto` files from a Gitaly checkout with
   version matching the wanted GitLab upstream version.
   Example in a HDK context:

   ```
   cp ../gitaly/proto/*.proto protos/  # we dont want the `go` subdir
   ```

3. run `./generate-stubs`

4. run the tests: `./run-all-tests`

5. perform necessary `hg add` after close inspection of `hg status`

### Feature flags

GitLab uses special feature flags to control Gitaly. They are transmitted
to the Gitaly server by means of invocation metadata (part of the gRPC
protocol, actually implemented as HTTP/2 headers).
This is documented in Gitaly's `doc/` subdirectory.

Gitaly feature flags have become important in HGitaly development since
every request now goes to RHGitaly first. We used before that to introduce
ordinary feature flags in GitLab Rails to control which requests would go
to HGitaly (Python) and which would go to RHGitaly. This was instrumental
in the progressive reimplementation in Rust of many gRPC methods, and has
obviously to be replaced by the use of Gitaly feature flags.

GitLab's development workflow is heavily centered around "chatops", they make
it a rule that feature flags should start as being disabled by default, then
gradually rolled out by percentage chatops commands. On the other hand,
Heptapod often feature flag to provide an opt-out option, with many starting
as enabled by default.

An important property of Gitaly feature flags is that nothing is passed at
all if the feature flag has not been set in the Rails application. In other
words, the default value is implemented by the Gitaly server and meaningless
in the Rails app.

As a consequence, creating a Gitaly feature flag defaulting to `true` does
nothing unless (R)HGitaly itself interprets the absence of the value as `true`.

TL;DR: for opt-out by a feature flag seen as `gitaly_my_feature` by Rails,
just use `rhgitaly::metadata::is_feature_enabled?("my-feature", true)` in the RHGitaly
code.

### Updating the HGitaly specific gRPC protocol

This package defines and implements an additional gRPC protocol, with
gRPC services and methods that are specific to Mercurial, or more generally
Heptapod.

#### Protocol specification

The sources are `proto` files in the `protos/` directory, same as for the
Gitaly protocol.

They distinguish themselves by this declaration:

```
package hgitaly;
```

Each time a change is made to the protocol, the libraries for all
provided programming languages have to be regenerated and committed, ideally
together with the protocol change.

#### Python library

It has a special status, being versioned together with the protocol and the
server implementation. It is provided as the [hgitaly.stub](hgitaly/stub)
package.

The Python stubs are produced by the same script that takes care of Gitaly
`proto` files:

```
./generate-stubs
```

#### Ruby library

See [the separate documentation](ruby/README.md)

#### Other languages

A Go library will probably be necessary quite soon for Workhorse or perhaps
Heptapod Shell.

A Rust library would be nice to have

[mercurial-testhelpers]: https://pypi.org/project/mercurial-testhelpers/
[grpcio]: https://pypi.org/project/grpcio/
[HDK]: https://foss.heptapod.net/heptapod/heptapod-development-kit


