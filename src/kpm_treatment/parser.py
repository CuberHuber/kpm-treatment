from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, final, runtime_checkable

from kpm_treatment.models import (
    ApplicationEntry,
    KpmExport,
    NoteEntry,
    OtherAccountEntry,
    WebsiteEntry,
)


@runtime_checkable
class Parseable(Protocol):
    def export(self) -> KpmExport: ...


@final
@dataclass(frozen=True)
class _Field:
    """A single-line named field inside an entry block."""

    _raw: str
    _name: str

    def value(self) -> str:
        read = self._read()
        if read is None:
            raise ValueError(
                f"Required field '{self._name}' missing in block:\n{self._raw}"
            )
        if not read:
            raise ValueError(
                f"Required field '{self._name}' is blank in block:\n{self._raw}"
            )
        return read

    def optional(self) -> str | None:
        read = self._read()
        return read if read else None

    def _read(self) -> str | None:
        prefix = f"{self._name}:"
        for line in self._raw.splitlines():
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
        return None


@final
@dataclass(frozen=True)
class _MultilineField:
    """A field whose value spans from its label line to end of block."""

    _raw: str
    _name: str

    def value(self) -> str:
        prefix = f"{self._name}:"
        lines = self._raw.splitlines()
        for index, line in enumerate(lines):
            if line.startswith(prefix):
                first = line[len(prefix) :].lstrip(" ")
                rest = lines[index + 1 :]
                return "\n".join([first, *rest]).strip()
        raise ValueError(
            f"Required field '{self._name}' missing in block:\n{self._raw}"
        )


@final
@dataclass(frozen=True)
class _WebsiteBlock:
    _raw: str

    def entry(self) -> WebsiteEntry:
        return WebsiteEntry(
            website_name=_Field(self._raw, "Website name").value(),
            website_url=_Field(self._raw, "Website URL").value(),
            login=_Field(self._raw, "Login").value(),
            password=_Field(self._raw, "Password").value(),
            login_name=_Field(self._raw, "Login name").optional(),
            comment=_Field(self._raw, "Comment").optional(),
        )


@final
@dataclass(frozen=True)
class _ApplicationBlock:
    _raw: str

    def entry(self) -> ApplicationEntry:
        return ApplicationEntry(
            application=_Field(self._raw, "Application").value(),
            login=_Field(self._raw, "Login").value(),
            password=_Field(self._raw, "Password").value(),
            login_name=_Field(self._raw, "Login name").optional(),
            comment=_Field(self._raw, "Comment").optional(),
        )


@final
@dataclass(frozen=True)
class _OtherAccountBlock:
    _raw: str

    def entry(self) -> OtherAccountEntry:
        return OtherAccountEntry(
            account_name=_Field(self._raw, "Account name").value(),
            login=_Field(self._raw, "Login").value(),
            password=_Field(self._raw, "Password").value(),
            login_name=_Field(self._raw, "Login name").optional(),
            comment=_Field(self._raw, "Comment").optional(),
        )


@final
@dataclass(frozen=True)
class _NoteBlock:
    _raw: str

    def entry(self) -> NoteEntry:
        return NoteEntry(
            name=_Field(self._raw, "Name").value(),
            text=_MultilineField(self._raw, "Text").value(),
        )


@final
@dataclass(frozen=True)
class _GroupedBlocks:
    """Raw entry blocks bucketed under their section header."""

    websites: tuple[str, ...]
    applications: tuple[str, ...]
    other_accounts: tuple[str, ...]
    notes: tuple[str, ...]


@final
@dataclass(frozen=True)
class _SectionedText:
    """KPM raw text walked once and grouped by section header."""

    _raw: str

    def grouped(self) -> _GroupedBlocks:
        buckets: dict[str, list[str]] = {
            "Websites": [],
            "Applications": [],
            "Other Accounts": [],
            "Notes": [],
        }
        current = ""
        for raw_block in self._raw.split("\n---\n"):
            block = raw_block.strip()
            if not block:
                continue
            head = block.splitlines()[0].strip()
            if head in buckets:
                current = head
                rest = block[len(head) :].strip()
                if not rest:
                    continue
                block = rest
            if not current:
                raise ValueError(
                    f"Entry block found before any section header:\n{block}"
                )
            buckets[current].append(block)
        return _GroupedBlocks(
            websites=tuple(buckets["Websites"]),
            applications=tuple(buckets["Applications"]),
            other_accounts=tuple(buckets["Other Accounts"]),
            notes=tuple(buckets["Notes"]),
        )


@final
@dataclass(frozen=True)
class KpmText:
    """KPM export content as raw text. Pass UTF-8 decoded file content."""

    _raw: str

    def export(self) -> KpmExport:
        groups = _SectionedText(self._raw).grouped()
        return KpmExport(
            websites=tuple(_WebsiteBlock(b).entry() for b in groups.websites),
            applications=tuple(
                _ApplicationBlock(b).entry() for b in groups.applications
            ),
            other_accounts=tuple(
                _OtherAccountBlock(b).entry() for b in groups.other_accounts
            ),
            notes=tuple(_NoteBlock(b).entry() for b in groups.notes),
        )
