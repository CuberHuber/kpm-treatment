from __future__ import annotations

from dataclasses import dataclass
from typing import final

from kpm_treatment.formats.csv_export import CsvExport
from kpm_treatment.formats.exceptions import (
    FormatMalformed,
    FormatMismatch,
    FormatUnrepresentable,
)
from kpm_treatment.formats.protocols import Exportable
from kpm_treatment.models import KpmExport

_KPM_SECTION_HEADERS = frozenset(
    {"Websites", "Applications", "Other Accounts", "Notes"}
)

_KPM_IMPORT_HEADER = (
    "Account",
    "Login Name",
    "Password",
    "Web Site",
    "Comments",
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
                w.login,
                w.password,
                w.website_url,
                w.comment or "",
            )
            for w in self._source.websites
        )
        return CsvExport(_KPM_IMPORT_HEADER, rows, _quote_all=True).render()


@final
@dataclass(frozen=True)
class KpmImportFormat:
    """The KPM-native CSV import format for website credentials."""

    def name(self) -> str:
        return "kpm-import"

    def description(self) -> str:
        return (
            "Kaspersky Password Manager import CSV. Five fully-quoted "
            "columns: Account, Login Name, Password, Web Site, Comments. "
            "Renders website credentials only; an export carrying any "
            "application, other-account, or note entry is rejected, "
            "since the KPM CSV import path accepts websites only."
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
        if export.applications or export.other_accounts or export.notes:
            raise FormatUnrepresentable(
                "kpm-import renders website credentials only; export "
                f"carries {len(export.applications)} application(s), "
                f"{len(export.other_accounts)} other-account(s), and "
                f"{len(export.notes)} note(s)"
            )
        return _KpmImportDoc(export)
