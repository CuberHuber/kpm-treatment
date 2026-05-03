from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import TextIO, final

from kpm_treatment.formats import (
    DEFAULT_REGISTRY,
    FormatError,
    FormatRegistry,
    FormatUnrepresentable,
    KpmImportFormat,
)
from kpm_treatment.parser import KpmText


@final
@dataclass(frozen=True)
class Cli:
    """The kpm-treatment command-line interface."""

    _argv: tuple[str, ...]
    _registry: FormatRegistry
    _out: TextIO
    _err: TextIO

    def run(self) -> int:
        parser = argparse.ArgumentParser(
            prog="kpm-treatment",
            description=(
                "Convert a Kaspersky Password Manager export "
                "into a supported import/export format."
            ),
        )
        parser.add_argument(
            "input",
            help="path to a KPM export file, or '-' to read from stdin",
        )
        parser.add_argument(
            "-f",
            "--format",
            dest="format",
            default=None,
            help=(
                "name of the target format; "
                "if omitted, the format is detected from the input"
            ),
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="output",
            default=None,
            help="path to write rendered output to; defaults to stdout",
        )
        parser.add_argument(
            "--soft",
            dest="soft",
            action="store_true",
            help=(
                "soft mode: render only website credentials and silently "
                "drop applications, other accounts, and notes "
                "(supported by 'kpm-import' only)"
            ),
        )
        args = parser.parse_args(self._argv)
        try:
            source = self._read(args.input)
            fmt = (
                self._registry.find(args.format)
                if args.format is not None
                else self._registry.detect(source)
            )
            if args.soft:
                if fmt.name() != "kpm-import":
                    raise FormatUnrepresentable(
                        f"soft mode is not supported by format '{fmt.name()}'"
                    )
                fmt = KpmImportFormat(_soft=True)
            rendered = fmt.of(KpmText(source).export()).render()
            self._write(args.output, rendered)
            return 0
        except FormatError as exc:
            self._err.write(f"format error: {exc}\n")
            return 1
        except (ValueError, OSError) as exc:
            self._err.write(f"error: {exc}\n")
            return 1

    def _read(self, path: str) -> str:
        if path == "-":
            return sys.stdin.read()
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def _write(self, path: str | None, text: str) -> None:
        if path is None:
            self._out.write(text)
            if not text.endswith("\n"):
                self._out.write("\n")
            return
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


def main() -> int:
    return Cli(
        _argv=tuple(sys.argv[1:]),
        _registry=DEFAULT_REGISTRY,
        _out=sys.stdout,
        _err=sys.stderr,
    ).run()


if __name__ == "__main__":
    raise SystemExit(main())
