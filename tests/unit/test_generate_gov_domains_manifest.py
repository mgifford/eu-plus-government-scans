"""Tests for the gov-domains manifest generator CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.cli.generate_gov_domains_manifest import build_manifest, main


def _write_toon(path: Path, domains: list[str]) -> None:
    data = {
        "version": "0.1-seed",
        "country": path.stem.title(),
        "domain_count": len(domains),
        "page_count": 0,
        "domains": [
            {"canonical_domain": d, "subnational": [], "source_tabs": [], "pages": []}
            for d in domains
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_build_manifest_shape(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    _write_toon(tmp_path / "canada.toon", ["canada.ca"])

    manifest = build_manifest(tmp_path)

    assert manifest["domain_count"] == 2
    assert manifest["domains"] == {"canada.ca": "CANADA", "gob.es": "SPAIN"}


def test_main_writes_manifest_file(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    output = tmp_path / "out" / "gov-domains.json"

    exit_code = main(["--toon-dir", str(tmp_path), "--output", str(output)])

    assert exit_code == 0
    assert output.exists()
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["domain_count"] == 1
    assert written["domains"] == {"gob.es": "SPAIN"}
