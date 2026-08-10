"""Sharded storage for the published relationship dataset.

The dataset is served straight out of the repository to GitHub Pages, so it has
to stay in version control -- but GitHub refuses any single file larger than
100 MiB, and this dataset grows on every scan cycle.  Rows are therefore split
across several files, each capped well below that ceiling.

Rows are grouped by the top-level domain of their source domain, so one shard
maps roughly onto one country and a consumer can fetch just the slice it needs
rather than the whole dataset.  A group that outgrows the cap is split into
numbered parts, which keeps the scheme working no matter how large any single
country's slice becomes.

Ordering is fully deterministic.  That matters for more than tidiness: git
stores these files as deltas against the previous revision, so a scan that
changes a handful of rows produces a small delta instead of rewriting every
shard from scratch.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Cap each shard at 32 MiB.  GitHub's hard limit is 100 MiB; the margin absorbs
# several scan cycles of growth so a shard never lands close to the ceiling
# between the run that fills it and the run that splits it.
SHARD_MAX_BYTES = 32 * 1024 * 1024

# GitHub rejects a push containing any blob larger than this.
GITHUB_FILE_LIMIT_BYTES = 100 * 1024 * 1024

INDEX_FILENAME = "index.json"

_GROUP_SAFE = re.compile(r"[^a-z0-9-]")
_FALLBACK_GROUP = "other"

# Sort fields, in precedence order, used to give shard contents a stable layout.
_SORT_FIELDS = (
    "source_domain",
    "target_domain",
    "target_hostname",
    "relationship_type",
)


def shard_group_for_domain(domain: str) -> str:
    """Return the shard group a source domain belongs to.

    The group is the domain's last label -- its top-level domain -- which keeps
    each country's relationships together in one place.

    Args:
        domain: Source domain, e.g. ``"varna.bg"``.

    Returns:
        A filename-safe group name, e.g. ``"bg"``.  Domains with no usable TLD
        (empty values, bare hostnames, raw IP addresses) fall back to
        ``"other"`` so that no row is ever silently dropped.
    """
    if not domain or "." not in domain:
        return _FALLBACK_GROUP
    tld = _GROUP_SAFE.sub("", domain.rsplit(".", 1)[-1].lower())
    # An all-digit last label means this is an IP address, not a hostname, so
    # there is no country to group it under.
    if not tld or tld.isdigit():
        return _FALLBACK_GROUP
    return tld


def _sort_key(row: dict[str, Any]) -> tuple[str, ...]:
    """Return the deterministic ordering key for a relationship row."""
    return tuple(str(row.get(field, "")) for field in _SORT_FIELDS)


def shard_files(shard_dir: Path) -> list[Path]:
    """Return the dataset's shard files, in the order they should be read.

    Prefers the order recorded in ``index.json`` and falls back to a sorted
    glob when the index is missing or unreadable, so a partially written or
    hand-edited directory still yields all of its data.

    Args:
        shard_dir: Directory holding the shards.

    Returns:
        Existing shard paths.  Empty when *shard_dir* does not exist.
    """
    if not shard_dir.is_dir():
        return []

    index_path = shard_dir / INDEX_FILENAME
    if index_path.is_file():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            listed = [shard_dir / entry["file"] for entry in index["shards"]]
            if all(path.is_file() for path in listed):
                return listed
        except (OSError, ValueError, KeyError, TypeError):
            # Fall through to the glob below; a damaged index must not hide
            # shards that are present on disk.
            pass

    return sorted(shard_dir.glob("*.jsonl"))


def iter_rows(
    shard_dir: Path,
    legacy_path: Path | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield every relationship row in the dataset.

    Rows are streamed one at a time so a caller that only needs to accumulate a
    summary never has to hold the whole dataset in memory.

    Args:
        shard_dir: Directory holding the shards.
        legacy_path: Optional path to the pre-sharding single-file dataset.
            Read only when *shard_dir* holds no shards, which lets a checkout
            created before the split still find its data.

    Yields:
        Decoded relationship rows.  Blank and malformed lines are skipped.
    """
    paths = shard_files(shard_dir)
    if not paths and legacy_path is not None and legacy_path.is_file():
        paths = [legacy_path]

    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except ValueError:
                    continue


def write_rows(
    rows: Iterable[dict[str, Any]],
    shard_dir: Path,
    max_bytes: int = SHARD_MAX_BYTES,
) -> dict[str, Any]:
    """Write the dataset to *shard_dir*, replacing whatever was there.

    Each shard is written to a temporary file and moved into place, so a run
    interrupted mid-write leaves the previous shard readable rather than
    truncated.  Shards left over from a previous run that the new data no
    longer fills are deleted, so a group that shrinks does not strand stale
    rows on disk.

    Args:
        rows: Relationship rows to write.
        shard_dir: Destination directory, created when absent.
        max_bytes: Soft cap on the size of a single shard.  A group larger than
            this is split into numbered parts.  A single row that exceeds the
            cap on its own still gets its own shard rather than being dropped.

    Returns:
        The index that was written alongside the shards.
    """
    shard_dir.mkdir(parents=True, exist_ok=True)

    # Encode up front: the encoded length decides which shard a row lands in.
    encoded: list[tuple[tuple[str, ...], str, bytes]] = []
    for row in rows:
        line = json.dumps(row, ensure_ascii=False) + "\n"
        group = shard_group_for_domain(str(row.get("source_domain", "")))
        encoded.append((_sort_key(row), group, line.encode("utf-8")))

    # Group first, then order within the group, so a shard's contents change
    # only when that group's own rows change.
    encoded.sort(key=lambda item: (item[1], item[0]))

    written: list[dict[str, Any]] = []
    current_group: str | None = None
    part_number = 0
    buffer: list[bytes] = []
    buffered_bytes = 0

    def flush() -> None:
        """Write the buffered rows out as the next part of the current group."""
        nonlocal buffer, buffered_bytes, part_number
        if not buffer:
            return
        part_number += 1
        name = f"{current_group}.{part_number:03d}.jsonl"
        target = shard_dir / name
        tmp = target.with_suffix(".jsonl.tmp")
        payload = b"".join(buffer)
        tmp.write_bytes(payload)
        tmp.replace(target)
        written.append(
            {
                "file": name,
                "group": current_group,
                "rows": len(buffer),
                "bytes": len(payload),
            }
        )
        buffer = []
        buffered_bytes = 0

    for _key, group, line in encoded:
        if group != current_group:
            flush()
            current_group = group
            part_number = 0
        elif buffered_bytes + len(line) > max_bytes and buffer:
            flush()
        buffer.append(line)
        buffered_bytes += len(line)
    flush()

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shard_max_bytes": max_bytes,
        "total_rows": sum(entry["rows"] for entry in written),
        "total_bytes": sum(entry["bytes"] for entry in written),
        "shards": written,
    }

    index_path = shard_dir / INDEX_FILENAME
    index_tmp = index_path.with_suffix(".json.tmp")
    index_tmp.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    index_tmp.replace(index_path)

    # Drop shards this run did not produce.
    keep = {entry["file"] for entry in written}
    for stale in shard_dir.glob("*.jsonl"):
        if stale.name not in keep:
            stale.unlink()
    for leftover in shard_dir.glob("*.tmp"):
        leftover.unlink()

    return index
