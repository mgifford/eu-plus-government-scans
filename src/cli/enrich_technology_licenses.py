"""CLI for enriching detected technologies with license metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.services.technology_license_enrichment import (
    EnrichedTechnology,
    build_output,
    enrich_all,
    load_overrides,
)


def _parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Enrich docs/technology-index.json with curated upstream "
            "license metadata and generate a markdown summary."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("docs/technology-index.json"),
        help="Path to the technology-index.json input file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/technology-license-index.json"),
        help="Path to write the enriched JSON output.",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path("data/technology-license-overrides.json"),
        help="Path to the curated license override JSON file.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("docs/technology-license-summary.md"),
        help="Path to write the markdown summary report.",
    )
    parser.add_argument(
        "--outlier-threshold",
        type=int,
        default=5,
        help="Maximum items shown in each summary list section.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    """Load and validate a top-level JSON object from disk.

    Args:
        path: JSON file path.

    Returns:
        Parsed JSON object.

    Raises:
        ValueError: If the file does not contain a JSON object.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return payload


def _write_json(path: Path, payload: dict) -> None:
    """Write a deterministic JSON document to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _build_stats_table(stats: dict[str, int]) -> list[str]:
    """Return markdown lines for the summary stats table."""
    return [
        "| Metric | Value |",
        "|---|---:|",
        f"| Total technologies | {stats['total_technologies']:,} |",
        f"| OSI-approved count | {stats['osi_approved_count']:,} |",
        (
            "| Proprietary + service count | "
            f"{stats['proprietary_or_service_count']:,} |"
        ),
        f"| Unknown count | {stats['unknown_count']:,} |",
        (
            "| Manual review queue count | "
            f"{stats['manual_review_queue_count']:,} |"
        ),
    ]


def _limit_entries(
    items: list[EnrichedTechnology],
    threshold: int,
) -> tuple[list[EnrichedTechnology], int]:
    """Return the first N items and the number omitted."""
    limit = max(threshold, 0)
    shown = items[:limit]
    return shown, max(len(items) - len(shown), 0)


def _append_empty_section(lines: list[str], message: str) -> None:
    """Append a one-line fallback message for an empty report section."""
    lines.extend([message, ""])


def _append_osi_section(
    lines: list[str],
    technologies: list[EnrichedTechnology],
    threshold: int,
) -> None:
    """Append the top OSI-approved technologies section."""
    lines.append("## Top OSI-approved technologies")
    lines.append("")
    shown, omitted = _limit_entries(technologies, threshold)
    if not shown:
        _append_empty_section(
            lines,
            "No OSI-approved technologies in the current dataset.",
        )
        return

    lines.extend(
        [
            "| Technology | Detected pages | SPDX | Confidence |",
            "|---|---:|---|---|",
        ]
    )
    for tech in shown:
        lines.append(
            "| "
            f"{tech.name} | {tech.detected_count:,} | "
            f"{tech.spdx_license_expression or '—'} | {tech.confidence} |"
        )
    lines.append("")
    if omitted:
        lines.extend([f"... and {omitted:,} more.", ""])


def _append_service_section(
    lines: list[str],
    technologies: list[EnrichedTechnology],
    threshold: int,
) -> None:
    """Append the proprietary and service technologies section."""
    lines.append("## Top proprietary/service technologies")
    lines.append("")
    shown, omitted = _limit_entries(technologies, threshold)
    if not shown:
        _append_empty_section(
            lines,
            "No proprietary or service-oriented technologies in the current "
            "dataset.",
        )
        return

    lines.extend(
        [
            "| Technology | Detected pages | Status | Confidence |",
            "|---|---:|---|---|",
        ]
    )
    for tech in shown:
        lines.append(
            "| "
            f"{tech.name} | {tech.detected_count:,} | "
            f"{tech.license_status} | {tech.confidence} |"
        )
    lines.append("")
    if omitted:
        lines.extend([f"... and {omitted:,} more.", ""])


def _append_manual_review_section(
    lines: list[str],
    technologies: list[EnrichedTechnology],
    threshold: int,
) -> None:
    """Append the manual review queue section."""
    lines.append("## Manual review queue")
    lines.append("")
    shown, omitted = _limit_entries(technologies, threshold)
    if not shown:
        _append_empty_section(
            lines,
            "No technologies are currently flagged for manual review.",
        )
        return

    lines.extend(
        [
            "| Technology | Detected pages | Status | Confidence |",
            "|---|---:|---|---|",
        ]
    )
    for tech in shown:
        lines.append(
            "| "
            f"{tech.name} | {tech.detected_count:,} | "
            f"{tech.license_status} | {tech.confidence} |"
        )
    lines.append("")
    if omitted:
        lines.extend([f"... and {omitted:,} more.", ""])


def _append_outlier_section(
    lines: list[str],
    technologies: list[EnrichedTechnology],
    threshold: int,
) -> None:
    """Append the low-count unknown-license outlier section."""
    lines.append("## Outlier technologies")
    lines.append("")
    shown, omitted = _limit_entries(technologies, threshold)
    if not shown:
        _append_empty_section(
            lines,
            "No low-count unknown-license outliers found.",
        )
        return

    for tech in shown:
        lines.append(f"- {tech.name} — {tech.detected_count:,} detected pages")
    lines.append("")
    if omitted:
        lines.extend([f"... and {omitted:,} more.", ""])


def _build_summary_markdown(
    enriched: list[EnrichedTechnology],
    generated_at: str,
    scope_note: str,
    stats: dict[str, int],
    outlier_threshold: int,
) -> str:
    """Build the markdown summary report content.

    Args:
        enriched: Enriched technology records.
        generated_at: Human-readable UTC timestamp.
        scope_note: Shared scope note written into the JSON output.
        stats: Summary stats dictionary from ``build_output``.
        outlier_threshold: Maximum items listed in each section.

    Returns:
        Markdown document text.
    """
    osi_approved = [
        tech for tech in enriched if tech.license_status == "osi_approved"
    ]
    proprietary_or_service = [
        tech
        for tech in enriched
        if tech.license_status in {"proprietary", "not_applicable_service"}
    ]
    manual_review = [tech for tech in enriched if tech.requires_manual_review]
    outliers = [
        tech
        for tech in enriched
        if tech.license_status == "unknown" and tech.detected_count <= 5
    ]
    outliers.sort(key=lambda tech: tech.name)

    lines = [
        "# Technology License Summary",
        "",
        scope_note,
        "",
        f"Generated at: {generated_at}",
        "",
        "## Stats",
        "",
    ]
    lines.extend(_build_stats_table(stats))
    lines.append("")
    _append_osi_section(lines, osi_approved, outlier_threshold)
    _append_service_section(lines, proprietary_or_service, outlier_threshold)
    _append_manual_review_section(lines, manual_review, outlier_threshold)
    _append_outlier_section(lines, outliers, outlier_threshold)
    lines.extend(
        [
            "License classifications are best-effort and should be verified "
            "against upstream projects before making policy claims.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    """Run the technology license enrichment pipeline."""
    args = _parse_args()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    technology_index = _load_json(args.input)
    overrides = load_overrides(args.overrides)
    enriched = enrich_all(technology_index, overrides)
    output_payload = build_output(enriched, generated_at)

    _write_json(args.output, output_payload)
    summary_text = _build_summary_markdown(
        enriched=enriched,
        generated_at=generated_at,
        scope_note=output_payload["scope_note"],
        stats=output_payload["stats"],
        outlier_threshold=args.outlier_threshold,
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(summary_text, encoding="utf-8")

    stats = output_payload["stats"]
    print(f"Enriched {stats['total_technologies']:,} technologies.")
    print(f"JSON written: {args.output}")
    print(f"Summary written: {args.summary}")
    print(
        "Stats: "
        f"OSI-approved={stats['osi_approved_count']:,}, "
        "proprietary/service="
        f"{stats['proprietary_or_service_count']:,}, "
        f"unknown={stats['unknown_count']:,}, "
        f"manual-review={stats['manual_review_queue_count']:,}"
    )


if __name__ == "__main__":
    main()
