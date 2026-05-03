from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Exportable(Protocol):
    """A document that can render itself as text."""

    def render(self) -> str: ...


@runtime_checkable
class Lintable(Protocol):
    """A format that can decide whether raw input belongs to it."""

    def lint(self, source: str) -> None: ...


@runtime_checkable
class Describable(Protocol):
    """A named, documented entity with a public reference."""

    def name(self) -> str: ...

    def description(self) -> str: ...

    def link(self) -> str: ...
