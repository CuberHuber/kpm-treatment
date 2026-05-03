from dataclasses import FrozenInstanceError

import pytest

from kpm_treatment.models import (
    ApplicationEntry,
    KpmExport,
    NoteEntry,
    OtherAccountEntry,
    WebsiteEntry,
)


@pytest.mark.unit
def test_website_entry_fields() -> None:
    e = WebsiteEntry(
        website_name="example.com",
        website_url="https://example.com",
        login="user@example.com",
        password="secret",
        login_name="Main",
        comment="test",
    )
    assert e.website_name == "example.com"
    assert e.login == "user@example.com"


@pytest.mark.unit
def test_website_entry_is_frozen() -> None:
    e = WebsiteEntry(
        website_name="example.com",
        website_url="https://example.com",
        login="user@example.com",
        password="secret",
        login_name=None,
        comment=None,
    )
    with pytest.raises(FrozenInstanceError):
        e.login = "other"  # type: ignore[misc]


@pytest.mark.unit
def test_website_display_name_uses_login_name() -> None:
    e = WebsiteEntry(
        website_name="x",
        website_url="https://x",
        login="user@x",
        password="p",
        login_name="Work",
        comment=None,
    )
    assert e.display_name() == "Work"


@pytest.mark.unit
def test_website_display_name_falls_back_to_login() -> None:
    e = WebsiteEntry(
        website_name="x",
        website_url="https://x",
        login="user@x",
        password="p",
        login_name=None,
        comment=None,
    )
    assert e.display_name() == "user@x"


@pytest.mark.unit
def test_application_display_name_falls_back_to_login() -> None:
    e = ApplicationEntry(
        application="MyApp",
        login="myuser",
        password="p",
        login_name=None,
        comment=None,
    )
    assert e.display_name() == "myuser"


@pytest.mark.unit
def test_other_account_display_name_falls_back_to_login() -> None:
    e = OtherAccountEntry(
        account_name="Win",
        login="user@host",
        password="p",
        login_name=None,
        comment=None,
    )
    assert e.display_name() == "user@host"


@pytest.mark.unit
def test_note_is_multiline_true() -> None:
    n = NoteEntry(name="n", text="line1\nline2")
    assert n.is_multiline() is True


@pytest.mark.unit
def test_note_is_multiline_false() -> None:
    n = NoteEntry(name="n", text="single line")
    assert n.is_multiline() is False


@pytest.mark.unit
def test_kpm_export_is_frozen() -> None:
    export = KpmExport(websites=(), applications=(), other_accounts=(), notes=())
    with pytest.raises(FrozenInstanceError):
        export.websites = ()  # type: ignore[misc]


@pytest.mark.unit
def test_kpm_export_all_credentials_includes_all_sections() -> None:
    w = WebsiteEntry("s", "u", "l", "p", None, None)
    a = ApplicationEntry("app", "l", "p", None, None)
    o = OtherAccountEntry("acc", "l", "p", None, None)
    export = KpmExport(
        websites=(w,),
        applications=(a,),
        other_accounts=(o,),
        notes=(),
    )
    creds = list(export.all_credentials())
    assert w in creds
    assert a in creds
    assert o in creds
    assert len(creds) == 3
