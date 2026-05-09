"""Rewrite the custom plugin path in ``.secrets.baseline`` to a portable form.

``detect-secrets scan`` stores the absolute ``file://`` URI of every
``--plugin`` argument in ``plugins_used``. The URI is whatever path was
on the developer's machine, so committing the baseline as written
poisons it for every other contributor and CI runner.

This normalizer rewrites the ``KpmPasswordDetector`` entry's ``path``
field to a stable, repository-relative URI. The KPM-aware audit wrapper
pre-imports the plugin module before any baseline-driven lookup, so the
URI is never resolved at runtime — only its textual stability matters.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Final, final

_PORTABLE_PLUGIN_PATH: Final[str] = (
    "file://tools/detect_secrets_plugins/kpm_password.py"
)
_PLUGIN_NAME: Final[str] = "KpmPasswordDetector"


@final
class PortableSecretsBaseline:
    """A ``.secrets.baseline`` whose plugin paths are repo-relative."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def normalize(self) -> None:
        with open(self._path, encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
        for plugin in data.get("plugins_used", []):
            if plugin.get("name") == _PLUGIN_NAME:
                plugin["path"] = _PORTABLE_PLUGIN_PATH
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: uv run python tools/normalize_secrets_baseline.py <baseline-path>"
        )
    PortableSecretsBaseline(Path(sys.argv[1])).normalize()
