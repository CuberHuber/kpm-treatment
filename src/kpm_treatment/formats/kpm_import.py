from __future__ import annotations

from dataclasses import dataclass
from typing import final

from kpm_treatment.formats.csv_export import CsvExport
from kpm_treatment.formats.exceptions import FormatMalformed, FormatMismatch
from kpm_treatment.formats.protocols import Exportable
from kpm_treatment.models import KpmExport

_KPM_SECTION_HEADERS = frozenset(
    {"Websites", "Applications", "Other Accounts", "Notes"}
)

_KPM_IMPORT_HEADER = (
    "Website name",
    "Website URL",
    "Login name",
    "Login",
    "Password",
    "Comment",
)


@final
@dataclass(frozen=True)
class _KpmImportDoc:
    """A KPM-import CSV document bound to a parsed export."""

    _source: KpmExport

    def render(self) -> str:
        rows = tuple(
            (
                w.website_name,
                w.website_url,
                w.login_name or "",
                w.login,
                w.password,
                w.comment or "",
            )
            for w in self._source.websites
        )
        return CsvExport(_KPM_IMPORT_HEADER, rows).render()


@final
@dataclass(frozen=True)
class KpmImportFormat:
    """The KPM-native CSV import format for website credentials."""

    def name(self) -> str:
        return "kpm-import"

    def description(self) -> str:
        return (
            "Kaspersky Password Manager import CSV. Six columns: "
            "Website name, Website URL, Login name, Login, Password, Comment. "
            "Only website credentials are emitted; applications, other "
            "accounts, and notes are skipped because the KPM CSV import "
            "path accepts website credentials only."
        )

    def link(self) -> str:
        return "https://forum.kaspersky.com/topic/kpm-import-csv-6262/"

    def lint(self, source: str) -> None:
        if not source.strip():
            raise FormatMismatch("source is empty")
        lines = source.splitlines()
        if not any(line.strip() in _KPM_SECTION_HEADERS for line in lines):
            raise FormatMismatch(
                "no KPM section header "
                "(Websites/Applications/Other Accounts/Notes) found"
            )
        if not any(":" in line for line in lines):
            raise FormatMalformed(
                "KPM section header found but no 'Key: value' fields present"
            )

    def of(self, export: KpmExport) -> Exportable:
        return _KpmImportDoc(export)
