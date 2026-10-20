"""Tests for pinned dependency compatibility in requirements.txt."""

from __future__ import annotations

from pathlib import Path


def _parse_requirements() -> dict[str, str]:
    """Return pinned package versions from requirements.txt."""
    requirements_path = Path("requirements.txt")
    versions: dict[str, str] = {}

    for raw_line in requirements_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "==" not in line:
            continue
        name, version = line.split("==", 1)
        versions[name.strip()] = version.strip()

    return versions


def test_pytest_pin_is_compatible_with_pytest_asyncio() -> None:
    """Pinned pytest version should satisfy the pinned pytest-asyncio range.

    The pins read here are the validated pair: pytest-asyncio 1.3.0 declares
    ``pytest<10,>=8.2``, and pytest 9.0.3 satisfies it.  Update both
    assertions together whenever either pin is bumped -- this test reads
    ``requirements.txt``, not the installed environment, so a stale virtual
    environment cannot mask a mismatch.
    """
    versions = _parse_requirements()

    assert versions["pytest"] == "9.0.3"
    assert versions["pytest-asyncio"] == "1.3.0"
