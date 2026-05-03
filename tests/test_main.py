from __future__ import annotations

import io
from pathlib import Path

import pytest

from kpm_treatment.formats import DEFAULT_REGISTRY
from kpm_treatment.main import Cli

_WEBSITES_ONLY = (
    "Websites\n"
    "\n"
    "Website name: example.com\n"
    "Website URL: https://example.com/\n"
    "Login name: Synthetic Account\n"
    "Login: synthetic-user@example.com\n"
    "Password: synthetic-pass\n"
    "Comment: synthetic sample\n"
)

_EXPECTED_CSV = (
    '"Account","Login Name","Password","Web Site","Comments"\n'
    '"example.com","synthetic-user@example.com",'
    '"synthetic-pass","https://example.com/","synthetic sample"\n'
)


def _cli(argv: tuple[str, ...]) -> tuple[Cli, io.StringIO, io.StringIO]:
    out = io.StringIO()
    err = io.StringIO()
    return (
        Cli(_argv=argv, _registry=DEFAULT_REGISTRY, _out=out, _err=err),
        out,
        err,
    )


@pytest.mark.unit
def test_run_with_explicit_format_writes_csv_to_stdout(
    tmp_path: Path,
) -> None:
    src = tmp_path / "in.txt"
    src.write_text(_WEBSITES_ONLY, encoding="utf-8")
    cli, out, err = _cli((str(src), "-f", "kpm-import"))
    assert cli.run() == 0
    assert out.getvalue() == _EXPECTED_CSV
    assert err.getvalue() == ""


@pytest.mark.unit
def test_run_detects_format_when_flag_omitted(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text(_WEBSITES_ONLY, encoding="utf-8")
    cli, out, err = _cli((str(src),))
    assert cli.run() == 0
    assert out.getvalue() == _EXPECTED_CSV
    assert err.getvalue() == ""


@pytest.mark.unit
def test_run_writes_to_output_file_when_flag_given(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text(_WEBSITES_ONLY, encoding="utf-8")
    dst = tmp_path / "out.csv"
    cli, out, err = _cli((str(src), "-o", str(dst)))
    assert cli.run() == 0
    assert out.getvalue() == ""
    assert err.getvalue() == ""
    assert dst.read_text(encoding="utf-8") == _EXPECTED_CSV


@pytest.mark.unit
def test_run_returns_one_for_unknown_format(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text(_WEBSITES_ONLY, encoding="utf-8")
    cli, out, err = _cli((str(src), "-f", "no-such-format"))
    assert cli.run() == 1
    assert out.getvalue() == ""
    assert "format error" in err.getvalue()


@pytest.mark.unit
def test_run_returns_one_for_missing_input_file(tmp_path: Path) -> None:
    cli, out, err = _cli((str(tmp_path / "does-not-exist.txt"),))
    assert cli.run() == 1
    assert out.getvalue() == ""
    assert "error" in err.getvalue()


@pytest.mark.unit
def test_run_rejects_export_with_non_website_entries(
    samples_dir: Path,
) -> None:
    cli, out, err = _cli((str(samples_dir / "kpm-export.txt"), "-f", "kpm-import"))
    assert cli.run() == 1
    assert out.getvalue() == ""
    assert "format error" in err.getvalue()


@pytest.mark.unit
def test_run_soft_mode_renders_websites_only_from_mixed_export(
    samples_dir: Path,
) -> None:
    cli, out, err = _cli((str(samples_dir / "kpm-export.txt"), "--soft"))
    assert cli.run() == 0
    assert err.getvalue() == ""
    expected = (samples_dir / "kpm-import.csv").read_text(encoding="utf-8")
    assert out.getvalue().splitlines() == expected.splitlines()


@pytest.mark.unit
def test_run_soft_mode_with_explicit_format_renders_websites_only(
    samples_dir: Path,
) -> None:
    cli, out, err = _cli(
        (str(samples_dir / "kpm-export.txt"), "-f", "kpm-import", "--soft")
    )
    assert cli.run() == 0
    assert err.getvalue() == ""
    assert out.getvalue().splitlines()[0] == (
        '"Account","Login Name","Password","Web Site","Comments"'
    )


@pytest.mark.unit
def test_run_with_unparseable_input_emits_error(tmp_path: Path) -> None:
    src = tmp_path / "garbage.txt"
    src.write_text("not a kpm export at all\n", encoding="utf-8")
    cli, out, err = _cli((str(src),))
    assert cli.run() == 1
    assert out.getvalue() == ""
    assert err.getvalue() != ""
