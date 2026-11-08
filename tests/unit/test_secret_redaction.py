"""Tests for credential masking in scan output."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cli.redact_secrets import main as redact_main
from src.lib.secret_redaction import REDACTED, redact_known_formats, redact_url

# Credential-shaped test values are assembled at runtime so that this source
# file contains no key-shaped literal for secret scanning to flag.
GOOGLE_KEY = "AI" + "za" + "Sy" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q"
GITHUB_TOKEN = "gh" + "p_" + "a" * 36
AWS_KEY_ID = "AK" + "IA" + "ABCDEFGHIJKLMNOP"


def test_google_key_fixture_has_the_real_shape() -> None:
    """Guard the fixture itself: a Google API key is AIza plus 35 characters."""
    assert len(GOOGLE_KEY) == 39


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://maps.googleapis.com/maps/api/js?libraries=places,geometry&key=abc123&callback=init",
            "https://maps.googleapis.com/maps/api/js?libraries=places,geometry&key=REDACTED&callback=init",
        ),
        ("https://api.example.com/x.js?apiKey=abc", "https://api.example.com/x.js?apiKey=REDACTED"),
        ("https://api.example.com/x.js?api-key=abc", "https://api.example.com/x.js?api-key=REDACTED"),
        (
            "https://api.mapbox.com/v1.js?access_token=abc.def",
            "https://api.mapbox.com/v1.js?access_token=REDACTED",
        ),
        ("https://idp.example.com/cb#access_token=abc", "https://idp.example.com/cb#access_token=REDACTED"),
        (
            "https://bucket.example.com/f.js?X-Amz-Signature=abc&X-Amz-Expires=60",
            "https://bucket.example.com/f.js?X-Amz-Signature=REDACTED&X-Amz-Expires=60",
        ),
    ],
)
def test_redact_url_masks_credential_parameters(url: str, expected: str) -> None:
    """Credential values are masked; everything else is left byte-for-byte."""
    assert redact_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://www.googletagmanager.com/gtm.js?id=GTM-AAA",
        "https://cdn.example.com/lib.js?monkey=banana&keys=1",
        "https://kit.fontawesome.com/f6f4ea8fb9.js",
        "",
    ],
)
def test_redact_url_leaves_other_urls_alone(url: str) -> None:
    """Parameter names must match whole, so ``monkey`` and ``keys`` survive."""
    assert redact_url(url) == url


def test_redact_url_masks_known_format_under_any_parameter_name() -> None:
    """A Google key is caught by its shape even when the parameter is unusual."""
    url = f"https://maps.example.com/js?client_ref={GOOGLE_KEY}&v=3"
    assert redact_url(url) == "https://maps.example.com/js?client_ref=REDACTED&v=3"


def test_redact_url_is_idempotent() -> None:
    """Masking twice gives the same result as masking once."""
    once = redact_url(f"https://maps.googleapis.com/maps/api/js?key={GOOGLE_KEY}")
    assert redact_url(once) == once


def test_redact_known_formats_counts_each_credential() -> None:
    """Every supported shape is masked and counted."""
    text = f'{{"a": "{GOOGLE_KEY}", "b": "{GITHUB_TOKEN}", "c": "{AWS_KEY_ID}"}}'
    masked, count = redact_known_formats(text)
    assert count == 3
    assert masked == f'{{"a": "{REDACTED}", "b": "{REDACTED}", "c": "{REDACTED}"}}'


def test_redact_known_formats_ignores_parameter_names() -> None:
    """Seed page URLs addressed by ``?key=`` must survive the published-file pass."""
    url = "https://www.example.gov/page?key=SiteNotices_CookiesPolicy"
    assert redact_known_formats(url) == (url, 0)


def test_redact_known_formats_needs_a_token_boundary() -> None:
    """A key shape embedded inside a longer token is not a match."""
    text = "x" + GOOGLE_KEY + "y"
    assert redact_known_formats(text) == (text, 0)


def test_cli_masks_files_and_reports_counts_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The CLI rewrites affected files, keeps a BOM, and never prints a value."""
    nested = tmp_path / "docs" / "domains"
    nested.mkdir(parents=True)
    leaky = tmp_path / "docs" / "data.csv"
    leaky.write_text(f"﻿url\nhttps://maps.example.com/js?key={GOOGLE_KEY}\n", encoding="utf-8")
    clean = nested / "iceland.md"
    clean_text = "https://www.example.gov/page?key=SiteNotices_CookiesPolicy\n"
    clean.write_text(clean_text, encoding="utf-8")
    ignored = tmp_path / "docs" / "image.png"
    ignored.write_bytes(GOOGLE_KEY.encode())

    exit_code = redact_main([str(tmp_path / "docs"), str(tmp_path / "missing.json")])

    assert exit_code == 0
    assert leaky.read_text(encoding="utf-8") == "﻿url\nhttps://maps.example.com/js?key=REDACTED\n"
    assert clean.read_text(encoding="utf-8") == clean_text
    assert ignored.read_bytes() == GOOGLE_KEY.encode()
    out = capsys.readouterr().out
    assert GOOGLE_KEY not in out
    assert "1 value(s) masked" in out
