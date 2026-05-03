from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class WebsiteEntry:
    website_name: str
    website_url: str
    login: str
    password: str
    login_name: str | None
    comment: str | None

    def display_name(self) -> str:
        return self.login_name if self.login_name else self.login


@final
@dataclass(frozen=True)
class ApplicationEntry:
    application: str
    login: str
    password: str
    login_name: str | None
    comment: str | None

    def display_name(self) -> str:
        return self.login_name if self.login_name else self.login


@final
@dataclass(frozen=True)
class OtherAccountEntry:
    account_name: str
    login: str
    password: str
    login_name: str | None
    comment: str | None

    def display_name(self) -> str:
        return self.login_name if self.login_name else self.login


@final
@dataclass(frozen=True)
class NoteEntry:
    name: str
    text: str

    def is_multiline(self) -> bool:
        return "\n" in self.text


Credential = WebsiteEntry | ApplicationEntry | OtherAccountEntry


@final
@dataclass(frozen=True)
class KpmExport:
    websites: tuple[WebsiteEntry, ...]
    applications: tuple[ApplicationEntry, ...]
    other_accounts: tuple[OtherAccountEntry, ...]
    notes: tuple[NoteEntry, ...]

    def all_credentials(self) -> Sequence[Credential]:
        return (*self.websites, *self.applications, *self.other_accounts)
