"""Validates that every cron expression in .github/workflows/*.yml is
well-formed.

This is the Phase 1 slice of WORKFLOW_ORCHESTRATION_AUDIT.md Section 13.1
(schedule tests). The collision-detection assertions from that section
("no two scanning workflows share a start-minute", "none start at :00")
describe the *proposed* Phase 2 staggered schedule (Section 6), not the
current one -- adding them now would fail against the still-unstaggered
cron values and doesn't belong in an additive, no-scheduling-changes-yet
phase. Those tests land together with the actual Phase 2 cron edits so the
test and the schedule it enforces change in the same commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

WORKFLOWS_DIR = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def _all_cron_expressions() -> list[tuple[str, str]]:
    """Return (workflow_filename, cron_expression) for every schedule trigger."""
    crons: list[tuple[str, str]] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        # "on:" is a YAML boolean key (True) in some parsers unless quoted;
        # PyYAML 6.x with safe_load keeps it as the string "on" in practice
        # for these files (verified against this repo's actual workflows),
        # but check both to be safe.
        on_block = data.get("on") or data.get(True) or {}
        schedule = on_block.get("schedule") if isinstance(on_block, dict) else None
        if not schedule:
            continue
        for entry in schedule:
            cron = entry.get("cron")
            if cron:
                crons.append((path.name, cron))
    return crons


def _cron_fields(cron: str) -> list[str]:
    return cron.split()


@pytest.mark.parametrize("workflow_name,cron", _all_cron_expressions())
def test_cron_has_five_fields(workflow_name: str, cron: str):
    fields = _cron_fields(cron)
    assert len(fields) == 5, (
        f"{workflow_name}: cron {cron!r} has {len(fields)} fields, expected 5 "
        f"(minute hour day-of-month month day-of-week)"
    )


@pytest.mark.parametrize("workflow_name,cron", _all_cron_expressions())
def test_cron_minute_field_in_valid_range(workflow_name: str, cron: str):
    minute_field = _cron_fields(cron)[0]
    # Accept "*", "*/N", "N", or "N,M,..." -- extract every literal integer
    # mentioned and check it's a valid minute (0-59).
    for token in minute_field.replace("*/", "").replace(",", " ").split():
        if token.isdigit():
            assert 0 <= int(token) <= 59, (
                f"{workflow_name}: minute field {minute_field!r} in cron "
                f"{cron!r} contains out-of-range value {token}"
            )


@pytest.mark.parametrize("workflow_name,cron", _all_cron_expressions())
def test_cron_hour_field_in_valid_range(workflow_name: str, cron: str):
    hour_field = _cron_fields(cron)[1]
    for token in hour_field.replace("*/", "").replace(",", " ").split():
        if token.isdigit():
            assert 0 <= int(token) <= 23, (
                f"{workflow_name}: hour field {hour_field!r} in cron "
                f"{cron!r} contains out-of-range value {token}"
            )


def test_at_least_one_scheduled_workflow_exists():
    """Sanity check that the parser above is actually finding real crons,
    so a YAML-shape change upstream can't silently make every test above
    vacuously pass with zero parametrized cases."""
    assert len(_all_cron_expressions()) >= 10
