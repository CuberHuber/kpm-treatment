from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from kpm_treatment.formats import (
    DEFAULT_REGISTRY,
    CsvExport,
    Describable,
    Exportable,
    FormatError,
    FormatMalformed,
    FormatMismatch,
    FormatNotFound,
    FormatRegistry,
    KpmImportFormat,
    Lintable,
)
from kpm_treatment.models import (
    ApplicationEntry,
    KpmExport,
    NoteEntry,
    OtherAccountEntry,
    WebsiteEntry,
)
from kpm_treatment.parser import KpmText

_HEADER_LINE = "Website name,Website URL,Login name,Login,Password,Comment"


def _empty_export() -> KpmExport:
    return KpmExport(
        websites=(),
        applications=(),
        other_accounts=(),
        notes=(),
    )


# ---------------------------------------------------------------------------
# CsvExport
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_csv_export_renders_header_and_rows() -> None:
    csv = CsvExport(
        _header=("a", "b"),
        _rows=(("1", "2"), ("3", "4")),
    )
    assert csv.render() == "a,b\n1,2\n3,4\n"


@pytest.mark.unit
def test_csv_export_renders_header_only_when_no_rows() -> None:
    csv = CsvExport(_header=("a", "b"), _rows=())
    assert csv.render() == "a,b\n"


@pytest.mark.unit
def test_csv_export_quotes_field_with_comma() -> None:
    csv = CsvExport(_header=("a",), _rows=(("x,y",),))
    assert csv.render() == 'a\n"x,y"\n'


@pytest.mark.unit
def test_csv_export_quotes_field_with_double_quote() -> None:
    csv = CsvExport(_header=("a",), _rows=(('he said "hi"',),))
    assert csv.render() == 'a\n"he said ""hi"""\n'


@pytest.mark.unit
def test_csv_export_quotes_field_with_newline() -> None:
    csv = CsvExport(_header=("a",), _rows=(("line1\nline2",),))
    assert csv.render() == 'a\n"line1\nline2"\n'


@pytest.mark.unit
def test_csv_export_satisfies_exportable() -> None:
    exportable: Exportable = CsvExport(_header=("a",), _rows=(("1",),))
    assert exportable.render() == "a\n1\n"


@pytest.mark.unit
def test_csv_export_is_frozen() -> None:
    csv = CsvExport(_header=("a",), _rows=(("1",),))
    with pytest.raises(FrozenInstanceError):
        csv._header = ("z",)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# KpmImportFormat — describable surface
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_kpm_import_format_name_is_kpm_import() -> None:
    assert KpmImportFormat().name() == "kpm-import"


@pytest.mark.unit
def test_kpm_import_format_description_is_non_empty() -> None:
    assert KpmImportFormat().description().strip() != ""


@pytest.mark.unit
def test_kpm_import_format_link_is_https_url() -> None:
    link = KpmImportFormat().link()
    assert link.startswith("https://")


@pytest.mark.unit
def test_kpm_import_format_satisfies_describable() -> None:
    desc: Describable = KpmImportFormat()
    assert desc.name() == "kpm-import"


@pytest.mark.unit
def test_kpm_import_format_satisfies_lintable() -> None:
    lintable: Lintable = KpmImportFormat()
    lintable.lint("Websites\n\nWebsite name: x\n")


@pytest.mark.unit
def test_kpm_import_format_descriptor_is_frozen() -> None:
    fmt = KpmImportFormat()
    with pytest.raises(FrozenInstanceError):
        fmt._marker = "x"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# KpmImportFormat — lint
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_lint_empty_source_raises_format_mismatch() -> None:
    with pytest.raises(FormatMismatch):
        KpmImportFormat().lint("")


@pytest.mark.unit
def test_lint_whitespace_only_raises_format_mismatch() -> None:
    with pytest.raises(FormatMismatch):
        KpmImportFormat().lint("   \n\t\n")


@pytest.mark.unit
def test_lint_no_section_header_raises_format_mismatch() -> None:
    with pytest.raises(FormatMismatch):
        KpmImportFormat().lint("Hello: world\nFoo: bar\n")


@pytest.mark.unit
def test_lint_header_without_fields_raises_format_malformed() -> None:
    with pytest.raises(FormatMalformed):
        KpmImportFormat().lint("Websites\n\n   \n")


@pytest.mark.unit
def test_lint_accepts_minimal_valid_source() -> None:
    KpmImportFormat().lint("Websites\n\nWebsite name: example.com\n")


@pytest.mark.unit
def test_lint_accepts_any_known_section_header() -> None:
    for header in ("Websites", "Applications", "Other Accounts", "Notes"):
        KpmImportFormat().lint(f"{header}\nName: x\n")


@pytest.mark.unit
def test_format_exceptions_share_base() -> None:
    assert issubclass(FormatMismatch, FormatError)
    assert issubclass(FormatMalformed, FormatError)
    assert issubclass(FormatNotFound, FormatError)


# ---------------------------------------------------------------------------
# KpmImportFormat — render via of()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_kpm_import_format_emits_header_only_for_empty_export() -> None:
    rendered = KpmImportFormat().of(_empty_export()).render()
    assert rendered == f"{_HEADER_LINE}\n"


@pytest.mark.unit
def test_kpm_import_format_renders_website_row() -> None:
    export = KpmExport(
        websites=(
            WebsiteEntry(
                website_name="example.com",
                website_url="https://example.com",
                login="user@example.com",
                password="secret",
                login_name="Main",
                comment="a note",
            ),
        ),
        applications=(),
        other_accounts=(),
        notes=(),
    )
    lines = KpmImportFormat().of(export).render().splitlines()
    assert lines[0] == _HEADER_LINE
    assert lines[1] == (
        "example.com,https://example.com,Main,user@example.com,secret,a note"
    )


@pytest.mark.unit
def test_kpm_import_format_blank_optional_fields_become_empty_strings() -> None:
    export = KpmExport(
        websites=(
            WebsiteEntry(
                website_name="t.com",
                website_url="https://t.com",
                login="t@t.com",
                password="tp",
                login_name=None,
                comment=None,
            ),
        ),
        applications=(),
        other_accounts=(),
        notes=(),
    )
    lines = KpmImportFormat().of(export).render().splitlines()
    assert lines[1] == "t.com,https://t.com,,t@t.com,tp,"


@pytest.mark.unit
def test_kpm_import_format_skips_applications() -> None:
    export = KpmExport(
        websites=(),
        applications=(
            ApplicationEntry(
                application="MyApp",
                login="myuser",
                password="pass123",
                login_name="work",
                comment=None,
            ),
        ),
        other_accounts=(),
        notes=(),
    )
    assert KpmImportFormat().of(export).render() == f"{_HEADER_LINE}\n"


@pytest.mark.unit
def test_kpm_import_format_skips_other_accounts() -> None:
    export = KpmExport(
        websites=(),
        applications=(),
        other_accounts=(
            OtherAccountEntry(
                account_name="Win",
                login="user@host",
                password="1234",
                login_name=None,
                comment=None,
            ),
        ),
        notes=(),
    )
    assert KpmImportFormat().of(export).render() == f"{_HEADER_LINE}\n"


@pytest.mark.unit
def test_kpm_import_format_skips_notes() -> None:
    export = KpmExport(
        websites=(),
        applications=(),
        other_accounts=(),
        notes=(NoteEntry(name="My Note", text="anything"),),
    )
    assert KpmImportFormat().of(export).render() == f"{_HEADER_LINE}\n"


@pytest.mark.unit
def test_kpm_import_format_renders_only_websites_when_mixed() -> None:
    export = KpmExport(
        websites=(WebsiteEntry("w.com", "https://w.com", "w@w.com", "wp", None, None),),
        applications=(ApplicationEntry("App", "appuser", "ap", None, None),),
        other_accounts=(OtherAccountEntry("Acc", "acc@host", "99", None, None),),
        notes=(NoteEntry(name="n", text="t"),),
    )
    lines = KpmImportFormat().of(export).render().splitlines()
    assert lines == [
        _HEADER_LINE,
        "w.com,https://w.com,,w@w.com,wp,",
    ]


@pytest.mark.unit
def test_kpm_import_doc_satisfies_exportable() -> None:
    exportable: Exportable = KpmImportFormat().of(_empty_export())
    assert exportable.render().startswith("Website name,")


@pytest.mark.unit
def test_kpm_import_doc_is_frozen() -> None:
    doc = KpmImportFormat().of(_empty_export())
    with pytest.raises(FrozenInstanceError):
        doc._source = _empty_export()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# FormatRegistry
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_default_registry_lists_kpm_import() -> None:
    names = tuple(fmt.name() for fmt in DEFAULT_REGISTRY)
    assert "kpm-import" in names


@pytest.mark.unit
def test_registry_find_returns_known_format() -> None:
    fmt = DEFAULT_REGISTRY.find("kpm-import")
    assert fmt.name() == "kpm-import"


@pytest.mark.unit
def test_registry_find_raises_for_unknown_name() -> None:
    with pytest.raises(FormatNotFound):
        DEFAULT_REGISTRY.find("does-not-exist")


@pytest.mark.unit
def test_registry_detect_returns_matching_format() -> None:
    fmt = DEFAULT_REGISTRY.detect("Websites\n\nWebsite name: x\n")
    assert fmt.name() == "kpm-import"


@pytest.mark.unit
def test_registry_detect_raises_when_no_format_matches() -> None:
    with pytest.raises(FormatNotFound):
        DEFAULT_REGISTRY.detect("totally unrelated text\nno headers here\n")


@pytest.mark.unit
def test_registry_detect_propagates_format_malformed() -> None:
    with pytest.raises(FormatMalformed):
        DEFAULT_REGISTRY.detect("Websites\n\n")


@pytest.mark.unit
def test_registry_is_frozen() -> None:
    registry = FormatRegistry((KpmImportFormat(),))
    with pytest.raises(FrozenInstanceError):
        registry._formats = ()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Integration — real sample file
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_kpm_import_format_renders_real_sample(samples_dir: Path) -> None:
    text = (samples_dir / "kpm-export.txt").read_text(encoding="utf-8")
    rendered = KpmImportFormat().of(KpmText(text).export()).render()
    lines = rendered.splitlines()
    assert lines[0] == _HEADER_LINE
    # Sample contains 3 websites; the other 9 entries (apps/accounts/notes)
    # must be skipped, so the output is exactly header + 3 rows.
    assert len(lines) == 4
    assert lines[1].startswith("google.com,https://google.com/registration/,")


@pytest.mark.integration
def test_registry_detect_recognises_real_sample(samples_dir: Path) -> None:
    text = (samples_dir / "kpm-export.txt").read_text(encoding="utf-8")
    fmt = DEFAULT_REGISTRY.detect(text)
    assert fmt.name() == "kpm-import"
