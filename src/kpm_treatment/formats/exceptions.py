from __future__ import annotations

from typing import final


class FormatError(Exception):  # noqa: FIN100
    """Base class for every error raised by the formats subsystem.

    Intentionally non-final: leaf exceptions below extend it so that
    callers can discriminate with ``except FormatMismatch`` while still
    being able to catch the family with ``except FormatError``.
    """


@final
class FormatMismatch(FormatError):
    """Raised when input does not look like the format being asked."""


@final
class FormatMalformed(FormatError):
    """Raised when input has the right shape but is structurally broken."""


@final
class FormatNotFound(FormatError):
    """Raised when a registry lookup cannot resolve a name or input."""


@final
class FormatUnrepresentable(FormatError):
    """Raised when a format cannot represent the given export.

    Distinct from ``FormatMismatch`` (which is about *input* shape) and
    from ``FormatMalformed`` (which is about *input* integrity): this
    one is raised when an otherwise-valid ``KpmExport`` carries content
    that the requested format does not cover, e.g. a KPM-import CSV
    asked to render application or note entries.
    """
