"""Helpers shared by the report generators in this package.

Each generator produces a different report, but they all need the same view of
the seed corpus in order to express coverage as "scanned out of total".  That
helper was copy-pasted into five generators; it lives here instead so a change
to the seed layout is made once.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.lib.country_utils import country_filename_to_code, iter_seed_toon_files


def count_toon_seed_urls(toon_seeds_dir: Path) -> dict[str, int]:
    """Return a mapping of country_code to page_count from the seed files.

    Reads every country seed in *toon_seeds_dir* and takes its declared
    ``page_count``.  Scanner-generated ``.toon`` output is excluded; see
    :func:`src.lib.country_utils.iter_seed_toon_files`.

    Args:
        toon_seeds_dir: Directory holding the per-country seed files.

    Returns:
        Country code to page count.  Empty when the directory does not exist or
        holds no seeds.  A seed that cannot be read is skipped rather than
        failing the whole report.
    """
    counts: dict[str, int] = {}
    if not toon_seeds_dir.is_dir():
        return counts
    for toon_file in iter_seed_toon_files(toon_seeds_dir):
        try:
            data = json.loads(toon_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        country_code = country_filename_to_code(toon_file.stem)
        counts[country_code] = int(data.get("page_count") or 0)
    return counts
