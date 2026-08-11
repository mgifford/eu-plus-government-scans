"""Unit tests for country utility functions."""

from pathlib import Path

from src.lib.country_utils import (
    country_code_to_display_name,
    country_code_to_filename,
    country_filename_to_code,
    is_seed_toon_file,
    iter_seed_toon_files,
)


def test_country_filename_to_code():
    """Test converting filename to country code."""
    assert country_filename_to_code("iceland") == "ICELAND"
    assert country_filename_to_code("united-kingdom-uk") == "UNITED_KINGDOM_UK"
    assert country_filename_to_code("republic-of-cyprus") == "REPUBLIC_OF_CYPRUS"


def test_country_code_to_filename():
    """Test converting country code to filename."""
    assert country_code_to_filename("ICELAND") == "iceland"
    assert country_code_to_filename("UNITED_KINGDOM_UK") == "united-kingdom-uk"
    assert country_code_to_filename("REPUBLIC_OF_CYPRUS") == "republic-of-cyprus"


def test_roundtrip_conversion():
    """Test that conversions are reversible."""
    filenames = ["iceland", "france", "united-kingdom-uk", "republic-of-cyprus"]

    for filename in filenames:
        code = country_filename_to_code(filename)
        result = country_code_to_filename(code)
        assert result == filename


def test_roundtrip_conversion_from_code():
    """Test that conversions are reversible from code."""
    codes = ["ICELAND", "FRANCE", "UNITED_KINGDOM_UK", "REPUBLIC_OF_CYPRUS"]

    for code in codes:
        filename = country_code_to_filename(code)
        result = country_filename_to_code(filename)
        assert result == code


def test_country_code_to_display_name():
    """Test converting country codes to human-friendly display names."""
    assert country_code_to_display_name("ICELAND") == "Iceland"
    assert country_code_to_display_name("REPUBLIC_OF_CYPRUS") == "Cyprus"
    assert country_code_to_display_name("UNITED_KINGDOM_UK") == "United Kingdom"


# ---------------------------------------------------------------------------
# Seed file discovery
# ---------------------------------------------------------------------------

# Every suffix a scanner currently writes beside the seeds.
DERIVED_SUFFIXES = (
    "_validated", "_tech", "_social", "_lighthouse",
    "_3pjs", "_overlays", "_accessibility",
)


def test_seed_files_are_recognised():
    """Original country seeds are lowercase-hyphenated, never underscored."""
    for name in ("iceland", "france", "united-kingdom-uk", "republic-of-cyprus"):
        assert is_seed_toon_file(Path(f"{name}.toon")) is True


def test_scanner_output_is_rejected():
    """Generated files must not be mistaken for extra countries."""
    for suffix in DERIVED_SUFFIXES:
        assert is_seed_toon_file(Path(f"iceland{suffix}.toon")) is False


def test_unknown_future_suffix_is_rejected():
    """A scanner added later cannot reintroduce the bug by inventing a suffix."""
    assert is_seed_toon_file(Path("iceland_somethingnew.toon")) is False


def test_iter_skips_derived_files(tmp_path):
    """Only seeds are returned when generated output sits alongside them."""
    for name in ("iceland.toon", "france.toon"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    for suffix in DERIVED_SUFFIXES:
        (tmp_path / f"iceland{suffix}.toon").write_text("{}", encoding="utf-8")

    found = iter_seed_toon_files(tmp_path)

    assert [p.name for p in found] == ["france.toon", "iceland.toon"]


def test_iter_returns_sorted_paths(tmp_path):
    """Ordering is deterministic so scan order does not depend on the filesystem."""
    for name in ("zeta.toon", "alpha.toon", "mu.toon"):
        (tmp_path / name).write_text("{}", encoding="utf-8")

    assert [p.name for p in iter_seed_toon_files(tmp_path)] == [
        "alpha.toon", "mu.toon", "zeta.toon",
    ]


def test_iter_handles_missing_directory(tmp_path):
    """A missing seed directory yields nothing rather than raising."""
    assert iter_seed_toon_files(tmp_path / "absent") == []


def test_derived_names_roundtrip_would_be_bogus_country_codes():
    """Documents the failure this guards against.

    Passing a generated filename through the country-code conversion produces a
    country that does not exist, which is exactly what leaked into scan state
    when globs picked these files up.
    """
    assert country_filename_to_code("iceland_validated") == "ICELAND_VALIDATED"
    assert is_seed_toon_file(Path("iceland_validated.toon")) is False


def test_no_source_file_globs_toon_directly():
    """Regression guard: seed discovery must go through the shared helper.

    A raw ``glob("*.toon")`` silently picks up scanner output; this keeps new
    call sites from reintroducing that.
    """
    src_root = Path(__file__).resolve().parents[2] / "src"
    if not src_root.is_dir():
        return

    offenders = [
        path.relative_to(src_root.parent)
        for path in src_root.rglob("*.py")
        if path.name != "country_utils.py"
        and '.glob("*.toon")' in path.read_text(encoding="utf-8")
    ]
    assert not offenders, f"use iter_seed_toon_files() instead: {offenders}"
