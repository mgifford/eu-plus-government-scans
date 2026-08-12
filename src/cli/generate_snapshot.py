"""Record a dated snapshot of the scan corpus, so change becomes measurable.

The relationship dataset describes the corpus *now*.  It carries ``first_seen``
and ``last_seen`` per edge but no periodic record, so questions of the form
"what share of this country's agencies depended on this provider in March"
cannot be answered for any past date, however well the scanner runs.

This writes one compact snapshot per day.  Accumulated over months they are what
makes a trend line possible: movement away from a provider, or growth in a
country's domain inventory, shows up as a difference between two snapshots.

Snapshots are deliberately bounded.  A dense country-by-provider record over all
6,866 observed providers would cost ~645 KB per cycle -- 230 MB a year -- and
almost all of it would be a long tail nobody trends.  Keeping the top providers
by how many government domains depend on them covers roughly three quarters of
all domain-provider dependencies for about 18 KB a day, and everything outside
that set is still counted in an ``other`` bucket so per-country totals reconcile.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

from src.cli.generate_dependency_matrix import (
    DEPENDENCY_TYPES,
    build_country_index,
)
from src.lib.country_utils import iter_seed_toon_files
from src.lib.relationship_shards import iter_rows

DEFAULT_TOON_DIR = Path("data/toon-seeds/countries")
DEFAULT_SHARD_DIR = Path("docs/data/relationships")
DEFAULT_SNAPSHOT_DIR = Path("docs/data/snapshots")

INDEX_FILENAME = "index.json"

# Providers kept per snapshot, ranked by how many government domains depend on
# them.  200 covers ~75% of all domain-provider dependencies; the rest roll into
# the per-country "other" count.
DEFAULT_TOP_PROVIDERS = 200


def count_seed_domains(toon_dir: Path) -> dict[str, int]:
    """Return the seeded domain count per country.

    Tracks the inventory itself rather than what was observed, so a country
    adding domains shows up even before the scanner reaches them.

    Args:
        toon_dir: Directory holding the per-country seed files.

    Returns:
        Country code to number of seeded domains.
    """
    from src.lib.country_utils import country_filename_to_code

    counts: dict[str, int] = {}
    for path in iter_seed_toon_files(toon_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        counts[country_filename_to_code(path.stem)] = len(data.get("domains", []))
    return counts


def build_snapshot(
    rows: Iterable[dict],
    country_index: dict[str, str],
    seed_counts: dict[str, int],
    snapshot_date: str,
    top_providers: int = DEFAULT_TOP_PROVIDERS,
) -> dict:
    """Build one dated snapshot from the relationship rows.

    Args:
        rows: Relationship rows.
        country_index: Registrable domain to country code.
        seed_counts: Country code to seeded domain count.
        snapshot_date: ISO date this snapshot describes.
        top_providers: How many providers to record individually.

    Returns:
        The snapshot payload, in an index-based encoding that keeps the file
        small enough to write daily and keep forever.
    """
    scanned: dict[str, set[str]] = defaultdict(set)
    gov_links: dict[str, int] = defaultdict(int)
    pairs: dict[tuple[str, str], set[str]] = defaultdict(set)
    provider_domains: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        # Inactive edges describe the past, not the corpus this snapshot covers.
        if row.get("active") is False:
            continue

        source = row.get("source_domain", "")
        country = country_index.get(source.lower())
        if country is None:
            continue
        scanned[country].add(source)

        rel_type = row.get("relationship_type")
        category = row.get("target_category")
        target = row.get("target_domain", "")

        if rel_type == "editorial_link" and category == "known_government":
            if target != source:
                gov_links[country] += 1
            continue

        if rel_type in DEPENDENCY_TYPES and category != "known_government" and target:
            pairs[(country, target)].add(source)
            provider_domains[target].add(source)

    providers = sorted(
        provider_domains,
        key=lambda p: (-len(provider_domains[p]), p),
    )[:top_providers]
    provider_pos = {name: i for i, name in enumerate(providers)}

    countries = sorted(scanned | seed_counts.keys())
    country_pos = {name: i for i, name in enumerate(countries)}

    cells: list[list[int]] = []
    other: dict[str, set[str]] = defaultdict(set)
    for (country, provider), domains in pairs.items():
        if provider in provider_pos:
            cells.append([country_pos[country], provider_pos[provider], len(domains)])
        else:
            other[country] |= domains
    cells.sort()

    return {
        "date": snapshot_date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": 1,
        "notes": {
            "cells": "[country index, provider index, distinct government domains depending]",
            "provider_ranking": "distinct government domains depending on the provider",
            "other_domains": "domains depending on at least one provider outside the recorded set",
        },
        "countries": countries,
        "seed_domains": [seed_counts.get(c, 0) for c in countries],
        "scanned_domains": [len(scanned.get(c, ())) for c in countries],
        "gov_to_gov_links": [gov_links.get(c, 0) for c in countries],
        "providers": providers,
        "cells": cells,
        "other_domains": [len(other.get(c, ())) for c in countries],
    }


def write_snapshot(snapshot: dict, snapshot_dir: Path) -> Path:
    """Write *snapshot* and refresh the directory index.

    One file per day: a later run on the same day replaces it, so the four scan
    cycles a day collapse into a single daily point rather than four
    near-identical ones.

    Args:
        snapshot: Snapshot payload.
        snapshot_dir: Destination directory.

    Returns:
        Path of the written snapshot.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_dir / f"{snapshot['date']}.json"
    path.write_text(
        json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    dates = sorted(p.stem for p in snapshot_dir.glob("*.json") if p.name != INDEX_FILENAME)
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(dates),
        "first": dates[0] if dates else None,
        "latest": dates[-1] if dates else None,
        "dates": dates,
    }
    (snapshot_dir / INDEX_FILENAME).write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--toon-dir", type=Path, default=DEFAULT_TOON_DIR)
    parser.add_argument("--shard-dir", type=Path, default=DEFAULT_SHARD_DIR)
    parser.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT_DIR)
    parser.add_argument(
        "--date",
        default=None,
        help="Date this snapshot describes (default: today, UTC).",
    )
    parser.add_argument(
        "--top-providers",
        type=int,
        default=DEFAULT_TOP_PROVIDERS,
        help=f"Providers recorded individually (default: {DEFAULT_TOP_PROVIDERS}).",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Entry point."""
    parsed = parse_args(args)

    country_index = build_country_index(parsed.toon_dir)
    if not country_index:
        print(f"No seed files under {parsed.toon_dir}; nothing to snapshot.")
        return 1

    snapshot_date = parsed.date or date.today().isoformat()
    snapshot = build_snapshot(
        iter_rows(parsed.shard_dir),
        country_index,
        count_seed_domains(parsed.toon_dir),
        snapshot_date,
        top_providers=parsed.top_providers,
    )

    if not snapshot["cells"]:
        print("No dependency data found; refusing to write an empty snapshot.")
        return 1

    path = write_snapshot(snapshot, parsed.snapshot_dir)
    size_kb = path.stat().st_size / 1024
    print(f"Wrote {path} ({size_kb:.1f} KB)")
    print(
        f"  {len(snapshot['countries'])} countries, "
        f"{len(snapshot['providers'])} providers, {len(snapshot['cells'])} cells"
    )
    print(f"  {sum(snapshot['scanned_domains']):,} scanned domains, "
          f"{sum(snapshot['seed_domains']):,} seeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
