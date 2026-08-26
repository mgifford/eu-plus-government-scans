"""Tests for src/cli/import_swh_gov_domains and src/cli/import_url_domains."""

from __future__ import annotations

import json
import socket
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.cli.import_swh_gov_domains import (
    check_swh_urls,
    extract_existing_domains,
    extract_iso3_from_country,
    fetch_csv,
    filter_european_domains,
    find_new_domains,
    list_swh_files,
    normalize_domain,
)
from src.cli.import_url_domains import (
    domain_resolves,
    extract_domain,
    extract_links,
    is_likely_gov_domain,
    load_manifest_urls,
)


class TestNormalizeDomain:
    def test_strips_whitespace(self) -> None:
        assert normalize_domain("  example.be  ") == "example.be"

    def test_lowercases(self) -> None:
        assert normalize_domain("EXAMPLE.BE") == "example.be"

    def test_removes_trailing_dot(self) -> None:
        assert normalize_domain("example.be.") == "example.be"

    def test_removes_www_prefix(self) -> None:
        assert normalize_domain("www.example.be") == "example.be"


class TestExtractIso3:
    def test_simple(self) -> None:
        assert extract_iso3_from_country("BEL_Belgium") == "BEL"

    def test_uppercases(self) -> None:
        assert extract_iso3_from_country("bel_belgium") == "BEL"

    def test_no_underscore(self) -> None:
        assert extract_iso3_from_country("BEL") == "BEL"


class TestListSwhFiles:
    def test_returns_filenames_on_success(self) -> None:
        api_response = json.dumps(
            [
                {"name": "public-sector.csv", "type": "blob"},
                {"name": "public-sector-central-gov.csv", "type": "blob"},
                {"name": "README.md", "type": "blob"},
            ]
        ).encode()
        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = api_response

        with patch("src.cli.import_swh_gov_domains.urlopen", return_value=mock_response):
            result = list_swh_files()

        assert result == ["public-sector.csv", "public-sector-central-gov.csv", "README.md"]

    def test_returns_none_on_network_error(self) -> None:
        with patch(
            "src.cli.import_swh_gov_domains.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            result = list_swh_files()

        assert result is None


class TestCheckSwhUrls:
    def test_warns_on_missing_file(self, capsys: pytest.CaptureFixture[str]) -> None:
        # Only 'public-sector.csv' is present; central-gov is missing
        with patch(
            "src.cli.import_swh_gov_domains.list_swh_files",
            return_value=["public-sector.csv"],
        ):
            check_swh_urls()

        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "public-sector-central-gov.csv" in out

    def test_no_warning_when_all_present(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch(
            "src.cli.import_swh_gov_domains.list_swh_files",
            return_value=["public-sector.csv", "public-sector-central-gov.csv"],
        ):
            check_swh_urls()

        out = capsys.readouterr().out
        assert "WARNING" not in out

    def test_no_warning_when_api_unavailable(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("src.cli.import_swh_gov_domains.list_swh_files", return_value=None):
            check_swh_urls()  # should not raise

        out = capsys.readouterr().out
        assert "WARNING" not in out


class TestFetchCsv:
    def _make_mock_response(self, content: str) -> MagicMock:
        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = content.encode()
        return mock_response

    def test_returns_rows(self) -> None:
        csv_content = "country,domain\nBEL_Belgium,example.be\n"
        with patch(
            "src.cli.import_swh_gov_domains.urlopen",
            return_value=self._make_mock_response(csv_content),
        ):
            rows = fetch_csv("https://example.com/test.csv")

        assert rows == [{"country": "BEL_Belgium", "domain": "example.be"}]

    def test_exits_on_404(self) -> None:
        with patch(
            "src.cli.import_swh_gov_domains.urlopen",
            side_effect=urllib.error.HTTPError(
                "https://example.com/missing.csv", 404, "Not Found", {}, None  # type: ignore[arg-type]
            ),
        ):
            with pytest.raises(SystemExit) as exc_info:
                fetch_csv("https://example.com/missing.csv")

        assert exc_info.value.code == 1

    def test_exits_on_other_http_error(self) -> None:
        with patch(
            "src.cli.import_swh_gov_domains.urlopen",
            side_effect=urllib.error.HTTPError(
                "https://example.com/test.csv", 503, "Service Unavailable", {}, None  # type: ignore[arg-type]
            ),
        ):
            with pytest.raises(SystemExit) as exc_info:
                fetch_csv("https://example.com/test.csv")

        assert exc_info.value.code == 1

    def test_exits_on_network_error(self) -> None:
        with patch(
            "src.cli.import_swh_gov_domains.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                fetch_csv("https://example.com/test.csv")

        assert exc_info.value.code == 1


class TestFilterEuropeanDomains:
    def test_filters_european_countries(self) -> None:
        central = [{"country": "BEL_Belgium", "domain": "gov.be"}]
        public = [{"country": "USA_United States", "subdomain": "whitehouse.gov", "parent_domain": "gov"}]

        result = filter_european_domains(central, public)
        assert "Belgium" in result
        assert "gov.be" in result["Belgium"]
        # USA should be excluded
        assert all("whitehouse.gov" not in domains for domains in result.values())

    def test_includes_subdomain_and_parent(self) -> None:
        central: list = []
        public = [{"country": "BEL_Belgium", "subdomain": "www.service.be", "parent_domain": "service.be"}]

        result = filter_european_domains(central, public)
        assert "Belgium" in result
        assert "service.be" in result["Belgium"]
        # www.service.be is normalized to service.be by normalize_domain()


class TestFindNewDomains:
    def test_excludes_existing(self) -> None:
        sh = {"Belgium": {"new.be", "existing.be"}}
        existing = {"Belgium": {"existing.be"}}
        result = find_new_domains(sh, existing)
        assert result["Belgium"] == ["new.be"]

    def test_empty_when_all_exist(self) -> None:
        sh = {"Belgium": {"existing.be"}}
        existing = {"Belgium": {"existing.be"}}
        result = find_new_domains(sh, existing)
        assert "Belgium" not in result


class TestExtractExistingDomains:
    def test_loads_from_toon_files(self, tmp_path: Path) -> None:
        countries_dir = tmp_path / "countries"
        countries_dir.mkdir()
        toon = {
            "domains": [
                {"canonical_domain": "example.be"},
                {"canonical_domain": "other.be"},
            ]
        }
        (countries_dir / "belgium-bel.toon").write_text(json.dumps(toon))
        index = {
            "countries": [
                {"country": "Belgium", "file": "data/toon-seeds/countries/belgium-bel.toon"}
            ]
        }
        (tmp_path / "index.json").write_text(json.dumps(index))

        result = extract_existing_domains(tmp_path)
        assert result["Belgium"] == {"example.be", "other.be"}


# ---------------------------------------------------------------------------
# import_url_domains
# ---------------------------------------------------------------------------


class TestExtractDomain:
    def test_strips_www(self) -> None:
        assert extract_domain("https://www.example.be/path") == "example.be"

    def test_lowercases(self) -> None:
        assert extract_domain("https://GOV.BE/") == "gov.be"

    def test_strips_port(self) -> None:
        assert extract_domain("https://example.be:8080/") == "example.be"

    def test_returns_none_for_empty(self) -> None:
        assert extract_domain("") is None


class TestExtractLinks:
    def test_extracts_absolute_links(self) -> None:
        html = '<a href="https://www.example.be/page">link</a>'
        links = extract_links(html, "https://source.be/")
        assert "https://www.example.be/page" in links

    def test_resolves_relative_links(self) -> None:
        html = '<a href="/local/page">link</a>'
        links = extract_links(html, "https://source.be/")
        assert "https://source.be/local/page" in links

    def test_skips_mailto(self) -> None:
        html = '<a href="mailto:test@example.be">email</a>'
        links = extract_links(html, "https://source.be/")
        assert links == []

    def test_skips_anchors(self) -> None:
        html = '<a href="#section">anchor</a>'
        links = extract_links(html, "https://source.be/")
        assert links == []


class TestIsLikelyGovDomain:
    @pytest.mark.parametrize("domain", [
        "service.gov.be",
        "minfin.fgov.be",
        "portal.belgium.be",
        "example.vlaanderen.be",
        "example.europa.eu",
        "www.admin.ch",
    ])
    def test_gov_domains(self, domain: str) -> None:
        assert is_likely_gov_domain(domain) is True

    @pytest.mark.parametrize("domain", [
        "example.com",
        "google.com",
        "wikipedia.org",
    ])
    def test_non_gov_domains(self, domain: str) -> None:
        assert is_likely_gov_domain(domain) is False


class TestDomainResolves:
    def test_returns_true_when_resolves(self) -> None:
        with patch("src.cli.import_url_domains.socket.getaddrinfo", return_value=[()]):
            assert domain_resolves("example.be") is True

    def test_returns_false_on_gaierror(self) -> None:
        with patch(
            "src.cli.import_url_domains.socket.getaddrinfo",
            side_effect=socket.gaierror("Name or service not known"),
        ):
            assert domain_resolves("nonexistent.invalid") is False


class TestSaveResults:
    def test_writes_csv_with_all_statuses(self, tmp_path: Path) -> None:
        results = {
            "https://example.be/list": {
                "new": ["new.be"],
                "unresolved": ["broken.be"],
                "duplicates": ["existing.be"],
            }
        }
        from src.cli.import_url_domains import save_results

        save_results(results, tmp_path)

        csv_path = tmp_path / "url_import_example_be.csv"
        assert csv_path.exists()
        rows = csv_path.read_text().splitlines()
        assert rows[0] == "domain,source,status"
        statuses = {row.split(",")[0]: row.split(",")[2] for row in rows[1:]}
        assert statuses["new.be"] == "new"
        assert statuses["broken.be"] == "dns_failed"
        assert statuses["existing.be"] == "duplicate"

    def test_summary_includes_duplicate_count(self, tmp_path: Path) -> None:
        results = {
            "https://example.be/list": {
                "new": ["new.be"],
                "unresolved": [],
                "duplicates": ["dup1.be", "dup2.be"],
            }
        }
        from src.cli.import_url_domains import save_results

        save_results(results, tmp_path)

        summary = json.loads((tmp_path / "url_import_summary.json").read_text())
        src = summary["sources"]["https://example.be/list"]
        assert src["duplicate_count"] == 2
        assert "dup1.be" in src["skipped_duplicates"]

    def test_dry_run_writes_nothing(self, tmp_path: Path) -> None:
        results = {
            "https://example.be/list": {
                "new": ["new.be"],
                "unresolved": [],
                "duplicates": ["dup.be"],
            }
        }
        from src.cli.import_url_domains import save_results

        save_results(results, tmp_path, dry_run=True)

        assert not list(tmp_path.iterdir())


class TestPromoteToToon:
    def _make_toon_tree(self, tmp_path: Path) -> Path:
        """Create a minimal toon-seeds tree with a Belgium file."""
        toon_dir = tmp_path / "toon-seeds"
        countries_dir = toon_dir / "countries"
        countries_dir.mkdir(parents=True)

        toon = {
            "version": "0.1-seed",
            "country": "Belgium",
            "domain_count": 1,
            "domains": [{"canonical_domain": "existing.be", "subnational": [], "pages": []}],
        }
        (countries_dir / "belgium.toon").write_text(json.dumps(toon))
        index = {
            "countries": [
                {"country": "Belgium", "file": "data/toon-seeds/countries/belgium.toon"}
            ]
        }
        (toon_dir / "index.json").write_text(json.dumps(index))
        return toon_dir

    def test_adds_new_domain(self, tmp_path: Path) -> None:
        toon_dir = self._make_toon_tree(tmp_path)
        from src.cli.import_url_domains import promote_to_toon

        results = {"https://example.be/list": {"new": ["brand-new.be"], "unresolved": [], "duplicates": []}}
        existing = {"Belgium": {"existing.be"}}

        added = promote_to_toon(results, toon_dir, existing)

        assert "Belgium" in added
        assert "brand-new.be" in added["Belgium"]

        toon_data = json.loads((toon_dir / "countries" / "belgium.toon").read_text())
        domains = [d["canonical_domain"] for d in toon_data["domains"]]
        assert "brand-new.be" in domains
        assert toon_data["domain_count"] == 2

    def test_skips_existing_domain(self, tmp_path: Path) -> None:
        toon_dir = self._make_toon_tree(tmp_path)
        from src.cli.import_url_domains import promote_to_toon

        results = {"https://example.be/list": {"new": ["existing.be"], "unresolved": [], "duplicates": []}}
        existing = {"Belgium": {"existing.be"}}

        added = promote_to_toon(results, toon_dir, existing)

        assert "Belgium" not in added

    def test_skips_unknown_tld(self, tmp_path: Path) -> None:
        toon_dir = self._make_toon_tree(tmp_path)
        from src.cli.import_url_domains import promote_to_toon

        results = {"https://example.be/list": {"new": ["unknown.xyz"], "unresolved": [], "duplicates": []}}
        existing: dict = {}

        added = promote_to_toon(results, toon_dir, existing)

        assert not added

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        toon_dir = self._make_toon_tree(tmp_path)
        from src.cli.import_url_domains import promote_to_toon

        results = {"https://example.be/list": {"new": ["brand-new.be"], "unresolved": [], "duplicates": []}}
        existing: dict = {}

        added = promote_to_toon(results, toon_dir, existing, dry_run=True)

        assert "Belgium" in added
        # File should be unchanged
        toon_data = json.loads((toon_dir / "countries" / "belgium.toon").read_text())
        domains = [d["canonical_domain"] for d in toon_data["domains"]]
        assert "brand-new.be" not in domains

    def test_new_entry_records_source_url(self, tmp_path: Path) -> None:
        toon_dir = self._make_toon_tree(tmp_path)
        from src.cli.import_url_domains import promote_to_toon

        source = "https://example.be/list"
        results = {source: {"new": ["brand-new.be"], "unresolved": [], "duplicates": []}}
        existing: dict = {}

        promote_to_toon(results, toon_dir, existing)

        toon_data = json.loads((toon_dir / "countries" / "belgium.toon").read_text())
        entry = next(d for d in toon_data["domains"] if d["canonical_domain"] == "brand-new.be")
        assert entry["source"] == "url_import"
        assert entry["source_url"] == source



    def test_loads_html_scrape_manual(self, tmp_path: Path) -> None:
        manifest = tmp_path / "domain_sources.yaml"
        manifest.write_text(
            "sources:\n"
            "  - name: Test source\n"
            "    url: https://example.be/audit-list\n"
            "    type: html_scrape\n"
            "    schedule: manual\n"
            "    countries: [BEL]\n"
            "  - name: CSV source\n"
            "    url: https://example.com/data.csv\n"
            "    type: csv_download\n"
            "    schedule: monthly\n"
            "    countries: [all_european]\n"
        )

        result = load_manifest_urls(manifest, schedule_filter="manual")
        assert result == ["https://example.be/audit-list"]

    def test_no_schedule_filter_returns_all_html_scrape(self, tmp_path: Path) -> None:
        manifest = tmp_path / "domain_sources.yaml"
        manifest.write_text(
            "sources:\n"
            "  - name: A\n"
            "    url: https://a.be/\n"
            "    type: html_scrape\n"
            "    schedule: manual\n"
            "    countries: [BEL]\n"
            "  - name: B\n"
            "    url: https://b.be/\n"
            "    type: html_scrape\n"
            "    schedule: monthly\n"
            "    countries: [BEL]\n"
        )

        result = load_manifest_urls(manifest, schedule_filter=None)
        assert len(result) == 2
