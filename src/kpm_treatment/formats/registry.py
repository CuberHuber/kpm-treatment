from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, final, runtime_checkable

from kpm_treatment.formats.exceptions import FormatMismatch, FormatNotFound
from kpm_treatment.formats.kpm_import import KpmImportFormat
from kpm_treatment.formats.protocols import Describable, Exportable, Lintable
from kpm_treatment.models import KpmExport


@runtime_checkable
class _Format(Describable, Lintable, Protocol):
    """A format usable by the registry: described, lintable, materializable."""

    def of(self, export: KpmExport) -> Exportable: ...


@final
@dataclass(frozen=True)
class FormatRegistry:
    """A catalog of known formats, looked up by name or detected from input."""

    _formats: tuple[_Format, ...]

    def __iter__(self) -> Iterator[_Format]:
        return iter(self._formats)

    def find(self, name: str) -> _Format:
        for fmt in self._formats:
            if fmt.name() == name:
                return fmt
        raise FormatNotFound(f"no format registered under name '{name}'")

    def detect(self, source: str) -> _Format:
        for fmt in self._formats:
            try:
                fmt.lint(source)
            except FormatMismatch:
                continue
            return fmt
        raise FormatNotFound("no registered format matches the given source")


DEFAULT_REGISTRY: FormatRegistry = FormatRegistry((KpmImportFormat(),))
