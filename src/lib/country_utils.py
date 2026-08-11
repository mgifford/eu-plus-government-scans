"""Utility functions for URL validation scanner."""

from __future__ import annotations

from pathlib import Path


_COUNTRY_DISPLAY_NAMES = {
    "REPUBLIC_OF_CYPRUS": "Cyprus",
    "UNITED_KINGDOM_UK": "United Kingdom",
}


def country_filename_to_code(filename: str) -> str:
    """
    Convert a country filename to a country code.

    Transforms lowercase hyphenated filenames to uppercase underscored codes.
    Example: "united-kingdom-uk" -> "UNITED_KINGDOM_UK"

    Args:
        filename: Lowercase hyphenated country name (without .toon extension)

    Returns:
        Uppercase underscored country code
    """
    return filename.upper().replace("-", "_")


def country_code_to_filename(country_code: str) -> str:
    """
    Convert a country code to a filename-safe format.

    Transforms uppercase underscored codes to lowercase hyphenated names.
    Example: "UNITED_KINGDOM_UK" -> "united-kingdom-uk"

    Args:
        country_code: Uppercase underscored country code

    Returns:
        Lowercase hyphenated filename (without extension)
    """
    return country_code.lower().replace("_", "-")


def country_code_to_display_name(country_code: str) -> str:
    """Return a human-friendly display label for a country code."""
    if country_code in _COUNTRY_DISPLAY_NAMES:
        return _COUNTRY_DISPLAY_NAMES[country_code]
    return country_code.replace("_", " ").title()


def is_seed_toon_file(path: Path) -> bool:
    """Return whether *path* is a country seed file rather than scanner output.

    Scanners write their per-country results beside the seeds as
    ``<country>_<scanner>.toon`` -- ``iceland_validated.toon``,
    ``iceland_tech.toon`` and so on.  Globbing ``*.toon`` therefore picks up
    generated files as though they were extra countries, inventing bogus codes
    like ``ICELAND_VALIDATED``.

    Seed filenames are lowercase-hyphenated (see
    :func:`country_code_to_filename`) and never contain an underscore, so the
    underscore is what separates the two.  Testing for it rather than listing
    known suffixes means a scanner added later cannot reintroduce the problem
    by inventing a suffix nobody remembered to exclude here.

    Args:
        path: Path to a ``.toon`` file.

    Returns:
        True when the file is an original seed.
    """
    return "_" not in path.stem


def iter_seed_toon_files(toon_dir: Path) -> list[Path]:
    """Return the country seed files in *toon_dir*, sorted by path.

    Excludes scanner-generated ``.toon`` output; see :func:`is_seed_toon_file`.

    Args:
        toon_dir: Directory holding the per-country seed files.

    Returns:
        Sorted seed file paths.  Empty when the directory does not exist.
    """
    if not toon_dir.is_dir():
        return []
    return sorted(path for path in toon_dir.glob("*.toon") if is_seed_toon_file(path))
