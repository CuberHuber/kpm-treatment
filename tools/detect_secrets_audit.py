"""KPM-aware wrapper around ``detect-secrets``.

Upstream ``detect-secrets`` v1.5.0 builds its
secret-type → plugin-class mapping from the built-in plugin package
on the first lookup
and caches the result with ``functools.lru_cache``.
The ``audit``, ``audit --report``, and ``audit --stats`` subcommands
trigger that lookup at argparse time —
before the baseline is read —
so any custom plugin path stored in ``.secrets.baseline``
is never registered when auditing.
The result is ``KeyError: 'KPM Export Password'``
followed by ``TypeError`` from ``from_secret_type``.

This wrapper imports the project's ``KpmPasswordDetector``
into the cached mapping
before delegating to ``detect_secrets.main.main``,
so audit-mode commands can reverse-engineer the secret values
stored in the baseline.

The wrapper also pre-validates the baseline path arguments,
because ``detect_secrets.main.main`` unconditionally returns ``0``
and would otherwise swallow a missing or corrupt baseline silently.

Usage mirrors the upstream CLI:

    uv run python tools/detect_secrets_audit.py audit .secrets.baseline
    uv run python tools/detect_secrets_audit.py audit --report .secrets.baseline
    uv run python tools/detect_secrets_audit.py audit --stats .secrets.baseline
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final, final

from detect_secrets.core.plugins import initialize as plugins_initialize
from detect_secrets.main import main

_PLUGIN_PATH: Final[Path] = (
    Path(__file__).resolve().parent / "detect_secrets_plugins" / "kpm_password.py"
)


@final
class KpmAwareDetectSecrets:
    """A ``detect-secrets`` invocation that knows about the KPM plugin."""

    def __init__(self, argv: list[str]) -> None:
        self._argv = argv

    def run(self) -> int:
        if not _PLUGIN_PATH.is_file():
            raise FileNotFoundError(f"KPM detector module missing at {_PLUGIN_PATH}")
        for candidate in self._argv:
            if candidate.startswith("-"):
                continue
            path = Path(candidate)
            if path.suffix != ".baseline" and path.name != ".secrets.baseline":
                continue
            if not path.is_file():
                raise FileNotFoundError(f"Baseline file missing at {path}")
            with open(path, encoding="utf-8") as fh:
                try:
                    json.load(fh)
                except json.JSONDecodeError as err:
                    raise ValueError(
                        f"Baseline at {path} is not valid JSON: {err}"
                    ) from err
        plugins_initialize.from_file(str(_PLUGIN_PATH))
        return main(self._argv)


if __name__ == "__main__":
    sys.exit(KpmAwareDetectSecrets(sys.argv[1:]).run())
