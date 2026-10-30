# Caracolaracol Homebrew tap

Precompiled releases of [Tuxedo Task](https://github.com/Caracolaracol/tuxedo-task),
an independent community fork of [Tuxedo](https://github.com/webstonehq/tuxedo).

## Install

```sh
brew install caracolaracol/tap/tuxedotask
```

No Rust or Cargo is required. Homebrew downloads the correct archive and verifies
its SHA-256 checksum; the formula has no Rust build dependency.

Both command names run the same application:

```sh
tuxedo --version
tuxedotask --version
tuxedo /path/to/todo.txt
```

The executable is `tuxedo`, with `tuxedotask` as a relative symlink. Existing task
files and `~/.config/tuxedo` configuration are not moved or deleted. The formula
supports macOS 12+ on Apple Silicon/Intel and glibc-based Linux ARM64/x86-64
(glibc 2.35+).

**Upstream conflict:** `brew install tuxedo` installs the original project, not
this fork. The formulas conflict because both provide `tuxedo`. Choose which one
you want linked; do not force an overwrite. Existing Cargo/manual copies are not
removed; use `command -v tuxedo` to check PATH precedence.

## Update

```sh
brew update
brew upgrade caracolaracol/tap/tuxedotask
```

[Application documentation](https://caracolaracol.github.io/tuxedo-task/docs/) ·
[Binary releases](https://github.com/Caracolaracol/tuxedo-task/releases/latest)

## Formula maintenance

The `Update formula` workflow checks the latest stable application release every
hour. It validates the version tag, the four expected archive/checksum names,
the release host, and checksum syntax before generating the formula. Incomplete,
draft, or prerelease releases cannot replace the stable formula. It can also be
triggered after publishing:

```sh
gh workflow run update.yml --repo caracolaracol/homebrew-tap
```

Updates use this repository's own short-lived GitHub token, not a stored
cross-repository personal token. The formula generator uses Python's standard
library only. Its tests are run with:

```sh
python3 -m unittest discover -s tests -v
ruby -c Formula/tuxedotask.rb
```

Formula CI also installs and tests the actual binary on Apple Silicon and Intel
Mac runners. The application binary and its original copyright remain under MIT;
see the [application license](https://github.com/Caracolaracol/tuxedo-task/blob/main/LICENSE).
