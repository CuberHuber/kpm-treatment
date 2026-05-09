"""Custom detect-secrets plugin for KPM export formats.

Matches passwords in the human-readable Kaspersky Password Manager exports
that the bundled detect-secrets plugins cannot recognise:

  * ``.txt`` blocks shaped like ``Password: <value>``
  * ``.csv`` rows where the password is the third quoted column

Loaded via ``detect-secrets scan --plugin``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from re import Pattern
from typing import Final, final

from detect_secrets.plugins.base import RegexBasedDetector


@final
class KpmPasswordDetector(RegexBasedDetector):
    secret_type: Final[str] = "KPM Export Password"

    denylist: Final[Iterable[Pattern[str]]] = (
        re.compile(r"^Password:\s*(\S+)\s*$"),
        re.compile(r'^(?!"Account",)"[^"]*","[^"]*","([^"]+)"'),
    )
