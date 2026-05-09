# Comparative analysis: kpm-treatment versus other KPM converters

`kpm-treatment` is one of nine open-source tools
  that read [Kaspersky Password Manager][kpm]'s proprietary TXT export.
This document positions `kpm-treatment` against the other eight,
  defends the two advantages the author claims —
  locality of use and PyPI distribution —
  and identifies the cases where another tool is the right pick.

The survey is grounded in a catalogue of the field
  with one row per repository
  and the same columns for every entry:
  language, parsed sections, rendered sections,
  target format, delivery channel,
  and a last-activity signal.
Every claim below cites those columns,
  not author intent.

## Repositories surveyed

| Repository | Language    | Parsed → rendered | Target format | Delivery                |
|---|-------------|---|---|-------------------------|
| [CuberHuber/kpm-treatment][cuberhuber] | Python      | 4 → 1 strict / 3 soft | KPM import CSV (round-trip) | PyPI + source                 |
| [gokdenizozkan/kpm2csv][goz] | JavaScript  | 4 → 4 | Generic CSV (one file per type) | hosted web + source     |
| [Draggie306/kaspersky-to-csv][draggie] | Python + JS | 1 → 1 | Chromium-style CSV | hosted web + source     |
| [MrSuicideParrot/Kaspersky-Password-Manager-to-CSV][parrot] | Python      | 3 → 3 | Generic CSV (`;` delim) / NordPass | source                  |
| [NeaGogu/Kaspersky-to-csv][neagogu] | Go          | 1 → 1 | Generic CSV | binaries + source       |
| [Th3Shadowbroker/KPM2CSV][shadow] | Go          | 1 → 1 | KeePassXC TSV | Windows binary + source |
| [EetheridgeIV/kaspersky-to-csv][etheridge] | Python      | 1 → 1 | 1Password CSV | source                  |
| [Salazar34/norton-kaspersky-adapter][salazar] | Python      | 1 → 1 | Norton CSV | source                  |
| [lucaslgr/kaspersky-password-manager-export-to-csv][lucaslgr] | PHP         | 1 → 1 | Dashlane / Chrome CSV | source                  |

The `1` in the rendered column denotes the Websites section,
  which is the section every other tool has chosen to support.

## Section coverage

KPM's TXT export carries four sections:
  Websites, Applications, Other Accounts, and Notes.
Six of the eight competitor tools parse only Websites and discard the rest.
Only two tools — `gokdenizozkan/kpm2csv` and `kpm-treatment` —
  parse all four sections.
`MrSuicideParrot/Kaspersky-Password-Manager-to-CSV` parses three;
  it omits Other Accounts.

Parsing all four sections matters because credentials live across them.
Some users keep desktop logins under Applications,
  some use Other Accounts for non-web identifiers
  (Wi-Fi keys, SSH passphrases, server consoles),
  and some store free-form recovery codes under Notes.
A converter that parses Websites only
  silently drops a non-trivial fraction of the user's vault.

The rendering picture is different.
KPM's own import path accepts only the Websites schema;
  Applications, Other Accounts, and Notes
  have no representation in the import CSV.
`kpm-treatment` therefore renders Websites strictly
  and raises `FormatUnrepresentable`
  when the input carries other sections,
  rather than degrading the model without telling the caller.
An opt-in `--soft` flag (and the equivalent `KpmImportFormat(_soft=True)`
  in library code) drops the non-website entries
  and renders the rest.
`gokdenizozkan/kpm2csv` solves the same coverage problem differently:
  it emits one generic CSV file per section type,
  shifting the fan-out to the filesystem.

## Target format and the round-trip case

Every other tool in the catalogue targets a third-party schema —
  Chromium, KeePassXC, 1Password, Norton, NordPass, Dashlane,
  or a generic CSV the user reshapes for some downstream importer.
Only `kpm-treatment` targets KPM's own import CSV.

This solves a case the other tools do not address:
  moving credentials from one KPM vault to another.
A KPM-native round-trip is impossible with the off-the-shelf product
  because KPM exports as TXT, imports as CSV,
  and refuses to round-trip through its own file formats.
Users who want to migrate from a corporate KPM account to a personal one,
  reset a vault from a backup,
  or diff two exports as CSV
  have no other tool in this catalogue.
The catalogue itself flags `kpm-treatment` as
  "the only repo that solves the KPM → KPM round-trip case".

## Delivery and installation

Delivery splits the catalogue along three axes.

*Hosted web tool* — `gokdenizozkan/kpm2csv`
  and `Draggie306/kaspersky-to-csv`
  publish converters that run inside the browser.
Both authors describe their pages as fully client-side,
  so the credential file does not leave the device by design.
The trust footprint is still wider than a local script:
  the user trusts the hosting domain,
  the integrity of the JS bundle,
  the network path on first load,
  and the absence of malicious browser extensions
  or DevTools observers reading page state.

*Pre-built binary* — `NeaGogu/Kaspersky-to-csv` ships
  Windows, macOS, and Linux binaries;
  `Th3Shadowbroker/KPM2CSV` ships a Windows binary.
The binary path skips the toolchain
  but ships on the project's own release cadence
  with no automated update channel.

*Source clone and run* — `MrSuicideParrot`, `EetheridgeIV`,
  `Salazar34`, and `lucaslgr` deliver as source only.
The user clones, installs the language toolchain
  (Python or PHP), resolves dependencies,
  and runs from the checkout.
This is the lowest-effort path for the *author*
  and the highest-effort path for a non-developer end user.

`kpm-treatment` belongs to the source-and-package category.
The repository can be cloned and run with `uv run kpm-treatment`,
  but it is also published to [PyPI][pypi-pkg] under the same project name,
  installable in one command with `pipx`, `uv tool`, or plain `pip`.
PyPI delivery is unique in this catalogue:
  no other tool surveyed —
  Python or otherwise —
  has registered itself as a Python distribution.

## Code quality and engineering posture

The competitor tools are mostly single-author scripts
  with no CI, no published test suite, and no static-analysis gates.
This is honest for tools that are short, single-purpose,
  and rarely re-edited.

`kpm-treatment` makes a different bet.
A CI matrix on Python 3.11, 3.12, and 3.13 runs
  `pytest --cov` (with an 80 % coverage gate),
  `ruff check`, `ruff format --check`,
  `mypy --strict`, `bandit -r src`,
  `flake8` with the [`eo-styleguide`][eo-style] plugin set,
  and `pre-commit run --all-files` on every push.
The release workflow rebuilds, re-tests,
  publishes to PyPI via [Trusted Publishing][pypi-tp]
  (no stored token),
  and creates a GitHub Release on every `v*` tag push.
The architecture itself is constrained by the
  [Elegant Objects][eo] discipline:
  every class is `@final`,
  every dataclass is `frozen=True`,
  no implementation inheritance,
  small `Protocol`-based interfaces,
  fail-fast error reporting,
  and a registry that decouples format lookup from format definition.

Whether this matters depends on the user.
For a one-shot conversion, a 100-line script is enough.
For a tool that is maintained, evolved,
  or imported into a downstream pipeline,
  the test gate is the difference between a refactor that ships
  and a refactor that breaks the round-trip.

## Locality of use

The author's first claimed advantage is locality —
  the converter runs entirely on the user's machine,
  reads source the user can audit,
  and makes no network call.

Two competitor tools fail the locality test by design.
`gokdenizozkan/kpm2csv` and `Draggie306/kaspersky-to-csv`
  load JavaScript from a third-party domain
  and process the export file inside that page.
Both authors document the page as fully client-side,
  and the architectural claim is plausibly true,
  but the trust surface is wider than a Python module on disk.
A user who downloaded the page on a hostile network,
  whose browser is running an extension that reads page content,
  or whose ISP injects a payload into HTTP responses,
  has no way to detect a tampered converter
  short of reading the JS bundle line by line.

A local Python module avoids those vectors entirely.
The user reads `parser.py` and `formats/kpm_import.py`,
  diffs them against the PyPI release,
  and runs the tool offline.
Air-gapped environments —
  corporate workstations,
  forensic recovery hosts,
  hardened laptops —
  cannot use the hosted converters
  and can use `kpm-treatment` without modification.

The remaining six competitors are also local in the same sense
  (`MrSuicideParrot`, `NeaGogu`, `Th3Shadowbroker`,
  `EetheridgeIV`, `Salazar34`, `lucaslgr`),
  so locality alone does not separate `kpm-treatment` from them.
Locality matters mainly as the answer to the question
  "should I paste my password file into the website I just found".

## Distribution via PyPI

The author's second claimed advantage is PyPI distribution.
Among the four Python tools surveyed,
  `kpm-treatment` is the only one that publishes a wheel.
The other three (`MrSuicideParrot`, `EetheridgeIV`, `Salazar34`)
  expect the user to clone the repository,
  read the README,
  install dependencies into some environment,
  and invoke the script from the checkout.

PyPI compresses that sequence into one line:

```bash
pipx install kpm-treatment
kpm-treatment kpm-export.txt -o kpm-import.csv
```

or, for users on `uv`:

```bash
uv tool install kpm-treatment
kpm-treatment kpm-export.txt -o kpm-import.csv
```

The single-command install path matters for three reasons.

*Discoverability.*
PyPI is searchable;
  GitHub repositories are searchable on GitHub,
  but a user who already lives in `pip` / `pipx` / `uv`
  finds the tool without leaving their package manager.

*Reproducibility.*
A versioned wheel is the same file for every user.
A `git clone` of `main` is whatever the latest commit happens to be,
  which is fine for the author
  and a footgun for downstream callers who want a pinned dependency.
A consumer's `pyproject.toml` declares
  `kpm-treatment>=0.2,<0.3` and gets the same artefact every time.

*Library use.*
`kpm-treatment` exposes a typed public API
  (`__all__` in `src/kpm_treatment/__init__.py`)
  and ships a `py.typed` marker so type checkers honour the annotations.
A downstream Python project imports `KpmText`, `KpmExport`,
  `DEFAULT_REGISTRY`, and the `Parseable` / `Exportable` protocols
  directly,
  without vendoring source or pinning a git ref.
None of the other Python tools in the catalogue
  is designed for library reuse;
  they are scripts whose internals are not stable interfaces.

The pre-built binary tools (`NeaGogu`, `Th3Shadowbroker`)
  also offer a one-step install,
  but only for the CLI use case
  and only on the operating systems for which the author cut a binary.
PyPI delivers cross-platform wheels under a single package name
  and lets the user upgrade with one command.

## When to choose another tool

A comparative analysis should be honest about the cases
  where another tool is the right pick.

Choose `gokdenizozkan/kpm2csv`
  if you want a hosted page that handles all four sections
  and you accept the wider trust surface of a JS bundle on a public domain.

Choose `Draggie306/kaspersky-to-csv`
  if you want the lowest-friction zero-install path
  for a Websites-only export
  and your target is Dashlane or a Chromium-style importer.

Choose `NeaGogu/Kaspersky-to-csv`
  if you do not have a Python toolchain installed
  and your target is a generic CSV.

Choose `Th3Shadowbroker/KPM2CSV`
  if your target is KeePassXC and you are on Windows.

Choose `EetheridgeIV/kaspersky-to-csv`,
  `Salazar34/norton-kaspersky-adapter`,
  or `lucaslgr/kaspersky-password-manager-export-to-csv`
  if your target is 1Password, Norton, or Dashlane respectively
  and the Websites-only scope is enough.

Choose `MrSuicideParrot/Kaspersky-Password-Manager-to-CSV`
  if you want a Python script that emits NordPass CSV.

Choose `kpm-treatment`
  if you want a KPM → KPM round-trip,
  if you want all four sections parsed under a typed model,
  if you want a library you can import,
  if you want a single-command install via PyPI,
  or if you want a tool with a CI matrix and a release pipeline.

## Summary

`kpm-treatment` shares the locality property with six other tools
  and shares the all-four-sections parser with one other tool,
  but it is the only tool in the surveyed catalogue
  that targets KPM's own import CSV,
  the only Python tool published to PyPI,
  and the only repository that exposes a typed library API
  alongside the CLI.

The author's two stated advantages — locality and PyPI —
  are both real and both narrower than they sound.
Locality separates `kpm-treatment` from the two hosted converters
  but not from the other six local tools.
PyPI separates `kpm-treatment` from every other Python tool surveyed,
  and from every tool surveyed in any language,
  for the install-and-import use case.

The differentiator that does not appear in the author's stated list
  but that the catalogue makes most clearly visible
  is the round-trip case:
  `kpm-treatment` is the only tool
  that lets a KPM user move credentials from one KPM vault to another.

[cuberhuber]: https://github.com/CuberHuber/kpm-treatment
[draggie]: https://github.com/Draggie306/kaspersky-to-csv
[eo]: https://www.elegantobjects.org/
[eo-style]: https://github.com/yegor256/eo-styleguide
[etheridge]: https://github.com/EetheridgeIV/kaspersky-to-csv
[goz]: https://github.com/gokdenizozkan/kpm2csv
[kpm]: https://www.kaspersky.com/password-manager
[lucaslgr]: https://github.com/lucaslgr/kaspersky-password-manager-export-to-csv
[neagogu]: https://github.com/NeaGogu/Kaspersky-to-csv
[parrot]: https://github.com/MrSuicideParrot/Kaspersky-Password-Manager-to-CSV
[pypi-pkg]: https://pypi.org/project/kpm-treatment/
[pypi-tp]: https://docs.pypi.org/trusted-publishers/
[salazar]: https://github.com/Salazar34/norton-kaspersky-adapter
[shadow]: https://github.com/Th3Shadowbroker/KPM2CSV
