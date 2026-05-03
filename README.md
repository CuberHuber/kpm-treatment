# kpm-treatment

Kaspersky Password Manager (KPM) treatment.

## Why this exists

I have been using KPM for years,
  but I have never transferred data from it to other tools.
One day, when I needed to export data, I ran into an unpleasant problem:

1. KPM only supports data export in TXT format
2. KPM only supports importing data in CSV format
   (you got it right —
   if I want to transfer saves from one vault to another, I cannot do it)
3. KPM only supports importing `Passwords` with the `Websites` type
   (yes, other types are not supported)
4. KPM throws an error when importing _incorrect_ data
   (for example, if the CSV file contains empty rows
   or invalid data formats),
   but it never tells you what the problem is

After spending some time on the forums,
  I discovered that many users had encountered similar problems
  and could not find a solution.
After a series of experiments,
  I found a solution suggested to me by a guy on the [official forum].

## Quick start

### Install

The project uses [uv] for environment management.
After cloning, sync the dependencies and install the [pre-commit] hooks:

```bash
uv sync
uv run pre-commit install
```

### Convert a KPM export from the command line

Export your vault from KPM as a TXT file,
  then hand it to the `kpm-treatment` console script:

```bash
# Detect the target format from the input
uv run kpm-treatment kpm-export.txt -o kpm-import.csv

# Select the format explicitly
uv run kpm-treatment kpm-export.txt -f kpm-import > kpm-import.csv

# Soft mode: render only the website rows and drop every
# application, other-account, and note entry from the export
uv run kpm-treatment kpm-export.txt --soft -o kpm-import.csv

# Read the export from stdin
cat kpm-export.txt | uv run kpm-treatment -
```

The CLI exits `0` on success,
  `1` on a parse or format error (a message is written to stderr),
  and `2` on a usage error (the standard [argparse] exit code).

### Use as a library

```python
from pathlib import Path

from kpm_treatment import DEFAULT_REGISTRY, KpmImportFormat, KpmText

source = Path("kpm-export.txt").read_text(encoding="utf-8")
export = KpmText(source).export()

# Strict: rejects exports that carry applications,
# other accounts, or notes
print(DEFAULT_REGISTRY.find("kpm-import").of(export).render())

# Soft: renders only the website rows and silently drops
# every non-website entry
print(KpmImportFormat(_soft=True).of(export).render())
```

The full public API is `kpm_treatment.__all__`;
  see `src/kpm_treatment/__init__.py` for the complete export list.

## Release

Releases are cut by pushing a `v*` tag.
The [`Release` workflow][release-yml] runs on tag push,
  rebuilds and tests the package,
  publishes the wheel and sdist to [PyPI],
  and creates a GitHub Release with the artifacts attached.

### Cut a release

```bash
# Bump the version in pyproject.toml, commit, then tag
# (use the version you just wrote, e.g. v0.2.0)
git tag vX.Y.Z
git push origin vX.Y.Z
```

The workflow refuses to publish if the tag does not match
  the `project.version` in `pyproject.toml`.

### One-time PyPI setup

The workflow uses [PyPI Trusted Publishing] (OIDC) —
  no API tokens are stored as repository secrets.
Before the first release a maintainer must:

1. Register the project on PyPI as `kpm-treatment`.
2. Add a [Trusted Publisher] entry on PyPI with:
   - Owner: `CuberHuber`
   - Repository: `kpm-treatment`
   - Workflow: `release.yml`
   - Environment: `pypi`
3. Create a GitHub Environment named `pypi` in the repository
   so the publish job's deployment can be reviewed and protected.

## Architecture

The tool reads
  [Kaspersky Password Manager][kpm]'s proprietary TXT export,
  which has no schema specification and no standard library support.
Rather than write a general-purpose tokeniser,
  the parser splits the raw string on `\n---\n` —
  the literal separator KPM writes between entries —
  and recognises four section headers
  (`Websites`, `Applications`, `Other Accounts`, `Notes`)
  by their position as the first line of a block.
Any change to KPM's export format requires changing `KpmText.export()`
  in `src/kpm_treatment/parser.py`.

KPM's TXT format exposes four sections with incompatible field sets:
  `Websites` carries a URL,
  `Applications` carry an application name,
  `Other Accounts` carry an account name,
  and `Notes` carry free-form multi-line text.
Representing these as a single generic record type
  would either discard static type information
  or force every caller to guard against absent fields at runtime.
Instead, each section maps to its own
  [`@dataclass(frozen=True)`][frozen-dc] —
  `WebsiteEntry`, `ApplicationEntry`, `OtherAccountEntry`, `NoteEntry` —
  so the type-checker rejects access to absent fields at analysis time,
  not at runtime.

KPM's import restriction (only `Websites`-type credentials can be
  re-imported) means consumers frequently need to iterate all
  credential records regardless of section of origin.
The `Credential` union type
  (`WebsiteEntry | ApplicationEntry | OtherAccountEntry`)
  and `KpmExport.all_credentials()` serve this use case
  without conflating credentials with `NoteEntry`,
  which has no login or password field and cannot be imported.
A programmer adding a conversion target
  (for example, a [Bitwarden][bitwarden] CSV converter)
  should iterate `KpmExport.all_credentials()`,
  not the individual section tuples on `KpmExport`.

The public API exposes a [`typing.Protocol`][proto] named `Parseable`
  — one method, `export() -> KpmExport` —
  rather than coupling callers to `KpmText` directly.
This follows the [Elegant Objects][eo] constraint
  that interfaces should be small structural contracts, not concrete classes.
Any test double or alternative parser
  (for example, one that accepts a `pathlib.Path` instead of a raw string)
  can satisfy the protocol without inheritance;
  test fixtures and callers should declare the type `Parseable`,
  not `KpmText`.

The output side mirrors `Parseable` with three small protocols in
  `src/kpm_treatment/formats/protocols.py`:
  `Exportable` exposes `render() -> str`,
  `Lintable` exposes `lint(source: str) -> None`,
  and `Describable` exposes `name()`, `description()`, and `link()`.
Each contract carries one or three methods,
  honouring the [Elegant Objects][eo] rule
  that an interface holds three or four methods at most.
A concrete format such as `KpmImportFormat` implements
  the union of protocols it needs and nothing more,
  so a format that cannot be auto-detected from raw input
  may omit `Lintable` without inheriting empty stubs.
A programmer adding a new format declares the protocols it satisfies,
  not a base class.

`FormatRegistry` in `src/kpm_treatment/formats/registry.py`
  exposes two lookup verbs:
  `find(name)` returns the format whose `name()` matches a string,
  and `detect(source)` walks the catalogue,
  asking each `Lintable` format whether the raw input belongs to it.
The two paths address two different callers:
  the CLI's `--format` flag resolves through `find`,
  while a script that hands over a file of unknown origin uses `detect`.
Adding a format requires one entry in `DEFAULT_REGISTRY`
  at the bottom of the same module;
  no caller of the registry changes,
  because the registry returns the structural protocol union,
  not the concrete class.

KPM's CSV import path accepts website credentials only;
  applications, other accounts, and notes have no representation.
`KpmImportFormat.of()` raises `FormatUnrepresentable`
  when the parsed `KpmExport` carries any non-website entry,
  rather than silently dropping the records the format cannot carry.
This is a third axis of failure,
  distinct from `FormatMismatch` (input shape does not look like the format)
  and `FormatMalformed` (input has the right shape but is structurally broken):
  `FormatUnrepresentable` describes a valid model
  that the requested format refuses to render.
A programmer adding a partial-coverage format
  raises `FormatUnrepresentable` from `of()`
  instead of returning a degraded `Exportable`.

The strict `FormatUnrepresentable` rule fits a programmer
  building a converter pipeline,
  but it forces the everyday user
  whose KPM export carries applications, other accounts, or
  notes to hand-strip those sections before each conversion.
`KpmImportFormat` therefore accepts an opt-in `_soft` flag,
  exposed as `--soft` on the CLI and as
  `KpmImportFormat(_soft=True)` in library code,
  which renders the website rows
  and drops every non-website entry without raising.
Soft mode changes only `of()`;
  parsing, detection, and lint behaviour stay identical,
  so a programmer toggling the flag never reasons
  about input recognition and rendering at the same time.

All model types and internal block types are decorated with
  [`@final`][final], prohibiting subclassing.
Combined with `frozen=True` dataclasses,
  this enforces the [Elegant Objects][eo] principle
  that objects must not change state after construction.
A `WebsiteEntry` is therefore safe to share across threads
  or to cache without defensive copying;
  the type-checker rejects any attempt to assign to its fields.

Field extraction is delegated to private `_EntryBlock`,
  `_WebsiteBlock`, `_ApplicationBlock`, `_OtherAccountBlock`,
  and `_NoteBlock` types in `src/kpm_treatment/parser.py`,
  none of which are re-exported from `__init__.py`.
This keeps `KpmText.export()` free of per-field string manipulation
  and makes each section's field list the responsibility of one class.
A programmer adding a new field to `ApplicationEntry`
  touches `_ApplicationBlock.entry()` and the model,
  not the top-level dispatcher.

`_EntryBlock.field()` raises `ValueError` immediately
  when a required field is absent or blank;
  it never returns `None` and never substitutes a default.
This reflects KPM's own failure mode:
  KPM silently rejects malformed imports
  without identifying the offending record.
The tool surfaces every structural problem loudly at parse time,
  so downstream conversion code never receives a partially-populated model.

The `Cli` class in `src/kpm_treatment/main.py`
  takes its argv tuple, registry, and stdout/stderr streams
  as constructor arguments,
  not from `sys` module globals.
The shim function `main()` is the only place that reads
  `sys.argv`, `sys.stdout`, and `sys.stderr`;
  every test instantiates `Cli` with a chosen argv tuple,
  the `DEFAULT_REGISTRY` (or a fake), and [`io.StringIO`][stringio] buffers,
  and asserts the integer exit code without monkey-patching.
A programmer adding a new flag edits `Cli.run()`'s
  [argparse] setup and the dispatch in the same method;
  `main()` itself stays a four-line constructor call.

## License

`kpm-treatment` is released under the [MIT License](LICENSE).

[argparse]: https://docs.python.org/3/library/argparse.html
[bitwarden]: https://bitwarden.com
[eo]: https://www.elegantobjects.org/
[final]: https://docs.python.org/3/library/typing.html#typing.final
[frozen-dc]: https://docs.python.org/3/library/dataclasses.html#frozen-instances
[kpm]: https://www.kaspersky.com/password-manager
[official forum]: https://forum.kaspersky.com/topic/kpm-import-csv-6262/
[pre-commit]: https://pre-commit.com/
[proto]: https://docs.python.org/3/library/typing.html#typing.Protocol
[PyPI]: https://pypi.org/project/kpm-treatment/
[PyPI Trusted Publishing]: https://docs.pypi.org/trusted-publishers/
[release-yml]: .github/workflows/release.yml
[stringio]: https://docs.python.org/3/library/io.html#io.StringIO
[Trusted Publisher]: https://docs.pypi.org/trusted-publishers/adding-a-publisher/
[uv]: https://docs.astral.sh/uv/
