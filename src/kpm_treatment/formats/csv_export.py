from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class CsvExport:
    """A CSV document built from a header row and data rows."""

    _header: tuple[str, ...]
    _rows: tuple[tuple[str, ...], ...]
    _quote_all: bool = False

    def render(self) -> str:
        buffer = io.StringIO()
        if self._quote_all:
            writer = csv.writer(buffer, quoting=csv.QUOTE_ALL, lineterminator="\n")
        else:
            writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerow(self._header)
        for row in self._rows:
            writer.writerow(row)
        return buffer.getvalue()
