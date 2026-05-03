# kpm-treatment
Kaspersky Password Manager (kpm) treatment

## Background

I’ve been using kpm for a very long time, but I’ve never transferred data from it to other tools. One day, when I needed to export data, I ran into a very unpleasant problem:
1. kpm only supports data export in TXT format
2. kpm only supports importing data in CSV format (you got it right—if I want to transfer saves from one vault to another, I won’t be able to do it)
3. kpm only supports importing `Passwords` with the `Websites` type (yes, other types aren’t supported)
4. kpm throws an error when importing _incorrect_ data (for example, if the CSV file contains empty rows or invalid data formats), but it never tells you what the problem is

After spending some time on the forums, I discovered that many users had encountered similar problems and couldn’t find a solution.
After a series of experiments, I found a solution suggested to me by a guy on the [official forum](https://forum.kaspersky.com/topic/kpm-import-csv-6262/).

## Quick start



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

[kpm]: https://www.kaspersky.com/password-manager
[frozen-dc]: https://docs.python.org/3/library/dataclasses.html#frozen-instances
[proto]: https://docs.python.org/3/library/typing.html#typing.Protocol
[final]: https://docs.python.org/3/library/typing.html#typing.final
[eo]: https://www.elegantobjects.org/
[bitwarden]: https://bitwarden.com
