# Security policy

## Scope

`kpm-treatment` is a local command-line tool and library
  that converts Kaspersky Password Manager TXT exports
  into other formats.
The project never connects to a network,
  never uploads data,
  and never persists credentials beyond the input file
  and the output file the user names on the command line.

A vulnerability in `kpm-treatment` therefore looks like one of these:

- A parser flaw that silently drops or corrupts a credential
  during conversion.
- A code path that writes a credential to a destination
  the user did not name
  (a log file,
  a temporary file outside the named output,
  or standard error).
- A format renderer that emits CSV
  the target tool interprets unsafely
  (for example,
  a value treated as a CSV injection payload by Excel).
- A dependency advisory that affects the published wheel.

Bugs that do not match the list above belong in the
  [public issue tracker][issues].

## Local secret hygiene

The repository runs `detect-secrets` as a pre-commit hook
  that blocks any commit introducing a credential pattern
  the tool recognises,
  including the KPM export shapes
  produced by the project's own conversion code.
The hook is configured in `.pre-commit-config.yaml`,
  the persistent state lives in `.secrets.baseline`,
  and the operating procedure
  (init, update, scan, audit)
  is documented in the [secrets runbook][runbook].

## Reporting a vulnerability

Do not open a public GitHub issue for a vulnerability.

Email the maintainer at <lupashcko.rom@yandex.ru>
  with the subject line `kpm-treatment security`,
  or use [GitHub's private vulnerability reporting][gh-private]
  on the repository's Security tab.

A useful report contains:

- The version of `kpm-treatment` (or the commit SHA).
- The Python version and operating system.
- A minimal input that triggers the issue.
  Strip every real credential before sending;
  use synthetic data such as `https://example.com`,
  `user@example.com`,
  and `password123`.
- The observed and expected behaviour.

The maintainer acknowledges every report within seven days
  and aims to publish a fix or mitigation within thirty days
  for confirmed issues.

## What you must never include in a report

Do not paste a real KPM export.
Do not paste a real CSV that contains live passwords,
  recovery codes,
  or one-time-password seeds.
A report that arrives with live secrets is deleted unread,
  and the reporter is asked to resend with synthetic data.

## Supported versions

The project is pre-1.0
  (see `Development Status :: 3 - Alpha` in `pyproject.toml`).
Only the latest released version on [PyPI]
  receives security fixes.
Older versions are not back-patched;
  upgrade to the latest release to consume a fix.

## Disclosure timeline

The maintainer follows coordinated disclosure.
After a fix lands on `main`,
  the maintainer publishes a GitHub Security Advisory
  describing the issue,
  the fixed version,
  and the reporter's credit
  (or anonymous credit on request).

[gh-private]: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
[issues]: https://github.com/CuberHuber/kpm-treatment/issues
[PyPI]: https://pypi.org/project/kpm-treatment/
[runbook]: docs/runbooks/secrets.md
