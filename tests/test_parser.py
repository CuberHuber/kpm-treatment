from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from kpm_treatment.parser import KpmText, Parseable

# ---------------------------------------------------------------------------
# Unit tests — inline fixtures
# ---------------------------------------------------------------------------

_SINGLE_WEBSITE = """\
Websites

Website name: example.com
Website URL: https://example.com
Login name: Main
Login: user@example.com
Password: secret
Comment: a note\
"""

_WEBSITE_BLANK_LOGIN_NAME = """\
Websites

Website name: example.com
Website URL: https://example.com
Login name:
Login: user@example.com
Password: secret
Comment:\
"""

_SINGLE_APPLICATION = """\
Applications

Application: MyApp
Login name: work
Login: myuser
Password: pass123
Comment:\
"""

_SINGLE_OTHER_ACCOUNT = """\
Other Accounts

Account name: MyAccount
Login name:
Login: user@host
Password: 1234
Comment:\
"""

_NOTE_SINGLE_LINE = """\
Notes

Name: My Note
Text: just one line\
"""

_NOTE_MULTILINE = """\
Notes

Name: multiliner
Text: first line
second line

third line after blank\
"""

_TWO_WEBSITES = """\
Websites

Website name: site1.com
Website URL: https://site1.com
Login name:
Login: a@a.com
Password: p1
Comment:

---

Website name: site2.com
Website URL: https://site2.com
Login name: Alt
Login: b@b.com
Password: p2
Comment: c2\
"""

_ALL_FOUR_SECTIONS = """\
Websites

Website name: w.com
Website URL: https://w.com
Login name:
Login: w@w.com
Password: wp
Comment:

---

Applications

Application: App
Login name:
Login: appuser
Password: ap
Comment:

---

Other Accounts

Account name: Acc
Login name:
Login: acc@host
Password: 99
Comment:

---

Notes

Name: n
Text: t\
"""

_TRAILING_SEPARATOR = """\
Websites

Website name: t.com
Website URL: https://t.com
Login name:
Login: t@t.com
Password: tp
Comment:

---
\
"""

_MISSING_PASSWORD = """\
Websites

Website name: t.com
Website URL: https://t.com
Login name:
Login: t@t.com
Comment:\
"""

_ENTRY_BEFORE_HEADER = """\
Website name: t.com
Website URL: https://t.com
Login name:
Login: t@t.com
Password: p
Comment:\
"""


@pytest.mark.unit
def test_export_single_website() -> None:
    result = KpmText(_SINGLE_WEBSITE).export()
    assert len(result.websites) == 1
    w = result.websites[0]
    assert w.website_name == "example.com"
    assert w.website_url == "https://example.com"
    assert w.login_name == "Main"
    assert w.login == "user@example.com"
    assert w.password == "secret"
    assert w.comment == "a note"


@pytest.mark.unit
def test_export_website_blank_login_name_is_none() -> None:
    result = KpmText(_WEBSITE_BLANK_LOGIN_NAME).export()
    assert result.websites[0].login_name is None


@pytest.mark.unit
def test_export_website_blank_comment_is_none() -> None:
    result = KpmText(_WEBSITE_BLANK_LOGIN_NAME).export()
    assert result.websites[0].comment is None


@pytest.mark.unit
def test_export_single_application() -> None:
    result = KpmText(_SINGLE_APPLICATION).export()
    assert len(result.applications) == 1
    a = result.applications[0]
    assert a.application == "MyApp"
    assert a.login_name == "work"
    assert a.login == "myuser"


@pytest.mark.unit
def test_export_single_other_account() -> None:
    result = KpmText(_SINGLE_OTHER_ACCOUNT).export()
    assert len(result.other_accounts) == 1
    o = result.other_accounts[0]
    assert o.account_name == "MyAccount"
    assert o.login_name is None
    assert o.login == "user@host"


@pytest.mark.unit
def test_export_note_single_line_text() -> None:
    result = KpmText(_NOTE_SINGLE_LINE).export()
    assert len(result.notes) == 1
    n = result.notes[0]
    assert n.name == "My Note"
    assert n.text == "just one line"
    assert not n.is_multiline()


@pytest.mark.unit
def test_export_note_multiline_text() -> None:
    result = KpmText(_NOTE_MULTILINE).export()
    n = result.notes[0]
    assert n.name == "multiliner"
    assert n.is_multiline()
    assert "second line" in n.text
    assert "third line after blank" in n.text


@pytest.mark.unit
def test_export_multiple_entries_in_section() -> None:
    result = KpmText(_TWO_WEBSITES).export()
    assert len(result.websites) == 2
    assert result.websites[0].website_name == "site1.com"
    assert result.websites[1].website_name == "site2.com"
    assert result.websites[1].login_name == "Alt"


@pytest.mark.unit
def test_export_all_four_sections() -> None:
    result = KpmText(_ALL_FOUR_SECTIONS).export()
    assert len(result.websites) == 1
    assert len(result.applications) == 1
    assert len(result.other_accounts) == 1
    assert len(result.notes) == 1


@pytest.mark.unit
def test_export_trailing_separator_ignored() -> None:
    result = KpmText(_TRAILING_SEPARATOR).export()
    assert len(result.websites) == 1


@pytest.mark.unit
def test_export_missing_required_field_raises() -> None:
    with pytest.raises(ValueError, match="Password"):
        KpmText(_MISSING_PASSWORD).export()


@pytest.mark.unit
def test_export_entry_before_section_header_raises() -> None:
    with pytest.raises(ValueError, match="section header"):
        KpmText(_ENTRY_BEFORE_HEADER).export()


@pytest.mark.unit
def test_kpm_text_is_frozen() -> None:
    kpm = KpmText("x")
    with pytest.raises(FrozenInstanceError):
        kpm._raw = "y"  # type: ignore[misc]


@pytest.mark.unit
def test_kpm_text_satisfies_parseable() -> None:
    p: Parseable = KpmText(_NOTE_SINGLE_LINE)
    result = p.export()
    assert len(result.notes) == 1


# ---------------------------------------------------------------------------
# Integration test — real sample file
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_export_real_kpm_file(samples_dir: Path) -> None:
    text = (samples_dir / "kpm-export.txt").read_text(encoding="utf-8")
    result = KpmText(text).export()
    assert len(result.websites) == 3
    assert len(result.applications) == 3
    assert len(result.other_accounts) == 2
    assert len(result.notes) == 4
    assert result.websites[0].website_name == "google.com"
    assert result.websites[2].login_name is None
    assert result.notes[2].name == "mylord"
    assert result.notes[2].is_multiline()
