"""Unit tests for the country-by-service dependency matrix."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.cli.generate_dependency_matrix import (
    DEPENDENCY_TYPES,
    bucket_for,
    build_country_index,
    build_matrix,
    render_page,
)


def _row(source, target, rel_type="script_dependency", category="cdn"):
    """Build a relationship row."""
    return {
        "source_domain": source,
        "target_domain": target,
        "target_hostname": f"www.{target}",
        "relationship_type": rel_type,
        "target_category": category,
    }


INDEX = {"a.gov.uk": "UNITED_KINGDOM_UK", "b.gov.uk": "UNITED_KINGDOM_UK", "c.gov.pl": "POLAND"}


class TestCountryIndex:
    """Countries come from the seed files, not from the TLD."""

    def test_index_maps_registrable_domain_to_country(self, tmp_path: Path) -> None:
        """Seeds list hostnames; relationship rows carry registrable domains."""
        (tmp_path / "iceland.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "abendingar.hafnarfjordur.is"}]}),
            encoding="utf-8",
        )

        index = build_country_index(tmp_path)

        assert index.get("hafnarfjordur.is") == "ICELAND"

    def test_missing_directory_yields_empty_index(self, tmp_path: Path) -> None:
        assert build_country_index(tmp_path / "absent") == {}

    def test_malformed_seed_is_skipped(self, tmp_path: Path) -> None:
        """One bad seed must not lose every other country."""
        (tmp_path / "broken.toon").write_text("{ not json", encoding="utf-8")
        (tmp_path / "iceland.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "island.is"}]}), encoding="utf-8"
        )

        assert build_country_index(tmp_path).get("island.is") == "ICELAND"


class TestBuildMatrix:
    """Cells count distinct domains, not requests."""

    def test_percent_is_share_of_scanned_domains(self) -> None:
        rows = [
            _row("a.gov.uk", "googleapis.com"),
            _row("b.gov.uk", "example.org"),
        ]
        matrix = build_matrix(rows, INDEX)

        cell = next(
            c for c in matrix["cells"]
            if c["country_code"] == "UNITED_KINGDOM_UK" and c["service"] == "googleapis.com"
        )
        assert cell["domains"] == 1
        assert cell["scanned_domains"] == 2
        assert cell["percent"] == 50.0

    def test_repeat_edges_from_one_domain_count_once(self) -> None:
        """A heavily-crawled site must not dominate its country's row."""
        rows = [
            _row("a.gov.uk", "googleapis.com"),
            _row("a.gov.uk", "googleapis.com", rel_type="stylesheet_dependency"),
            _row("a.gov.uk", "googleapis.com", rel_type="font_or_preload_dependency"),
            _row("b.gov.uk", "example.org"),
        ]
        matrix = build_matrix(rows, INDEX)

        cell = next(
            c for c in matrix["cells"]
            if c["country_code"] == "UNITED_KINGDOM_UK" and c["service"] == "googleapis.com"
        )
        assert cell["domains"] == 1
        assert cell["percent"] == 50.0

    def test_navigational_links_are_excluded(self) -> None:
        """A link to a platform is an editorial choice, not a runtime dependency."""
        rows = [
            _row("a.gov.uk", "twitter.com", rel_type="editorial_link",
                 category="social_platform"),
            _row("b.gov.uk", "googleapis.com"),
        ]
        matrix = build_matrix(rows, INDEX)

        assert [s["service"] for s in matrix["services"]] == ["googleapis.com"]

    def test_government_targets_are_excluded(self) -> None:
        """Gov-to-gov asset loads are not third-party dependencies."""
        rows = [_row("a.gov.uk", "b.gov.uk", category="known_government")]
        matrix = build_matrix(rows, INDEX)

        assert matrix["services"] == []

    def test_unresolvable_source_is_skipped(self) -> None:
        """A domain that maps to no seed country cannot be attributed."""
        rows = [_row("someone-elses.com", "googleapis.com"), _row("a.gov.uk", "googleapis.com")]
        matrix = build_matrix(rows, INDEX)

        assert {c["country_code"] for c in matrix["countries"]} == {"UNITED_KINGDOM_UK"}

    def test_services_ranked_by_country_reach(self) -> None:
        """Breadth across countries ranks above depth within one."""
        rows = [
            _row("a.gov.uk", "narrow.com"), _row("b.gov.uk", "narrow.com"),
            _row("c.gov.pl", "broad.com"), _row("a.gov.uk", "broad.com"),
        ]
        matrix = build_matrix(rows, INDEX, top_services=2)

        assert [s["service"] for s in matrix["services"]] == ["broad.com", "narrow.com"]

    def test_top_services_limit_is_honoured(self) -> None:
        rows = [_row("a.gov.uk", f"svc{i}.com") for i in range(30)]
        matrix = build_matrix(rows, INDEX, top_services=5)

        assert len(matrix["services"]) == 5

    def test_every_country_service_pair_has_a_cell(self) -> None:
        """A dense matrix: missing pairs would leave holes in the table."""
        rows = [_row("a.gov.uk", "one.com"), _row("c.gov.pl", "two.com")]
        matrix = build_matrix(rows, INDEX)

        assert len(matrix["cells"]) == len(matrix["countries"]) * len(matrix["services"])

    def test_dependency_types_are_all_counted(self) -> None:
        for rel_type in DEPENDENCY_TYPES:
            matrix = build_matrix([_row("a.gov.uk", "svc.com", rel_type=rel_type)], INDEX)
            assert matrix["services"], f"{rel_type} was not counted"


class TestBuckets:
    """Bucket edges decide the colour and must be stable."""

    @pytest.mark.parametrize(
        ("percent", "expected"),
        [
            (0, "b0"), (0.1, "b1"), (9.9, "b1"),
            (10, "b2"), (24.9, "b2"),
            (25, "b3"), (49.9, "b3"),
            (50, "b4"), (74.9, "b4"),
            (75, "b5"), (100, "b5"),
        ],
    )
    def test_bucket_edges(self, percent: float, expected: str) -> None:
        assert bucket_for(percent) == expected


class TestRenderedPage:
    """The rendered table has to be readable without colour."""

    @staticmethod
    def _page() -> str:
        rows = [
            _row("a.gov.uk", "googleapis.com"),
            _row("b.gov.uk", "googleapis.com"),
            _row("c.gov.pl", "other.com"),
        ]
        return render_page(build_matrix(rows, INDEX))

    def test_every_cell_prints_its_value(self) -> None:
        """Colour is a redundant encoding; colour-only would fail WCAG 1.4.1."""
        page = self._page()
        # 100% of UK domains depend on googleapis.com in this fixture.
        assert "100%" in page

    def test_zero_cells_are_marked_for_screen_readers(self) -> None:
        page = self._page()
        assert 'aria-hidden="true">—' in page
        assert "0 percent" in page

    def test_table_has_scoped_headers_and_caption(self) -> None:
        page = self._page()
        assert "<caption>" in page
        assert 'scope="col"' in page
        assert 'scope="row"' in page

    def test_wide_table_scrolls_in_its_own_region(self) -> None:
        """The page body must never scroll horizontally."""
        page = self._page()
        assert 'class="dep-matrix-scroll"' in page
        assert 'tabindex="0"' in page

    def test_page_has_front_matter(self) -> None:
        assert self._page().startswith("---\ntitle:")


class TestBackingData:
    """AGENTS.md requires published figures to be independently verifiable."""

    def test_percent_is_reproducible_from_the_cells(self) -> None:
        rows = [_row("a.gov.uk", "svc.com"), _row("b.gov.uk", "other.com")]
        matrix = build_matrix(rows, INDEX)

        for cell in matrix["cells"]:
            if cell["scanned_domains"]:
                expected = round(cell["domains"] / cell["scanned_domains"] * 100, 1)
                assert cell["percent"] == expected

    def test_csv_round_trips(self, tmp_path: Path) -> None:
        from src.cli.generate_dependency_matrix import _write_csv

        matrix = build_matrix([_row("a.gov.uk", "svc.com")], INDEX)
        out = tmp_path / "matrix.csv"
        _write_csv(matrix, out)

        with out.open(encoding="utf-8-sig", newline="") as handle:
            written = list(csv.DictReader(handle))

        assert len(written) == len(matrix["cells"])
        assert written[0]["service"] == "svc.com"


class TestCellFormatting:
    """The displayed number must never contradict the cell's own colour."""

    def test_tiny_nonzero_shows_less_than_one(self) -> None:
        """0.4% must not print as "0%" in a cell that is coloured as non-zero."""
        index = {f"d{i}.gov.uk": "UNITED_KINGDOM_UK" for i in range(300)}
        rows = [_row(f"d{i}.gov.uk", "other.com") for i in range(300)]
        rows.append(_row("d0.gov.uk", "rare.com"))

        page = render_page(build_matrix(rows, index))

        assert "&lt;1%" in page
        assert ">0%<" not in page

    def test_percentages_render_as_whole_numbers(self) -> None:
        """Mixed precision breaks decimal alignment in a right-aligned column."""
        import re

        index = {"a.gov.uk": "UNITED_KINGDOM_UK", "b.gov.uk": "UNITED_KINGDOM_UK",
                 "c.gov.uk": "UNITED_KINGDOM_UK"}
        rows = [_row("a.gov.uk", "svc.com"), _row("b.gov.uk", "other.com"),
                _row("c.gov.uk", "third.com")]

        page = render_page(build_matrix(rows, index))
        shown = re.findall(r">(\d+(?:\.\d+)?)%<", page)

        assert shown, "no percentages rendered"
        assert not any("." in value for value in shown), shown
