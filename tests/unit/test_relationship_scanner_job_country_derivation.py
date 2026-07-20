"""Tests for _derive_country_from_tld, which now looks up the government
domain registry (built from TOON seeds) instead of a hardcoded TLD table,
and for _registered_domain_from_url, the sibling helper that returns the
actual domain (previously, call sites needing a domain wrongly passed
_derive_country_from_tld()'s country-code return value into fields named
source_domain -- see test_source_domain_call_sites_use_domain_helper)."""

from __future__ import annotations

import inspect

import src.jobs.relationship_scanner_job as job_module
from src.jobs.relationship_scanner_job import (
    _derive_country_from_tld,
    _registered_domain_from_url,
)
from src.lib.gov_domain_registry import GovernmentDomainRegistry


class _FakeRegistry(GovernmentDomainRegistry):
    def __init__(self, domains: dict[str, str]):
        self._domain_to_country = {d.lower(): c for d, c in domains.items()}


def test_derives_country_for_known_domain(monkeypatch):
    monkeypatch.setattr(job_module, "_GOV_REGISTRY", _FakeRegistry({"mjusticia.gob.es": "SPAIN"}))
    assert _derive_country_from_tld("https://mjusticia.gob.es/page") == "SPAIN"


def test_unknown_domain_returns_unknown(monkeypatch):
    monkeypatch.setattr(job_module, "_GOV_REGISTRY", _FakeRegistry({"gob.es": "SPAIN"}))
    assert _derive_country_from_tld("https://facebook.com/page") == "UNKNOWN"


def test_previously_uncovered_country_now_resolves(monkeypatch):
    """Canada was entirely absent from the old hardcoded _TLD_TO_COUNTRY
    table, so any canada.ca URL always mapped to UNKNOWN regardless of
    whether it was a real seeded government domain."""
    monkeypatch.setattr(job_module, "_GOV_REGISTRY", _FakeRegistry({"canada.ca": "CANADA"}))
    assert _derive_country_from_tld("https://www.canada.ca/en.html") == "CANADA"


def test_multi_label_public_suffix_domain_still_resolves(monkeypatch):
    """tldextract's registered_domain is empty for a host entirely under a
    multi-label public suffix like gob.es -- must fall back to the raw
    hostname rather than losing the match."""
    monkeypatch.setattr(job_module, "_GOV_REGISTRY", _FakeRegistry({"gob.es": "SPAIN"}))
    assert _derive_country_from_tld("https://gob.es/") == "SPAIN"


def test_empty_url_returns_unknown(monkeypatch):
    monkeypatch.setattr(job_module, "_GOV_REGISTRY", _FakeRegistry({}))
    assert _derive_country_from_tld("") == "UNKNOWN"


def test_registered_domain_from_url_returns_domain_not_country():
    assert _registered_domain_from_url("https://mjusticia.gob.es/page") == "mjusticia.gob.es"


def test_registered_domain_from_url_multi_label_public_suffix():
    assert _registered_domain_from_url("https://gob.es/") == "gob.es"


def test_registered_domain_from_url_empty_for_empty_url():
    assert _registered_domain_from_url("") == ""


def test_source_domain_call_sites_use_domain_helper():
    """Regression guard for the bug where UrlEligibility.source_domain and
    the relationship_scan_state/relationship_scan_results DB columns (both
    named source_domain, both holding real domain strings everywhere else in
    this file) were populated with _derive_country_from_tld()'s country-code
    return value instead. Source-inspects the job module rather than
    exercising the full DB-backed job, since that would require a lot more
    setup for what is fundamentally a "which function got called" check."""
    source = inspect.getsource(job_module)
    assert "source_domain=_derive_country_from_tld(" not in source
    assert source.count("source_domain=_registered_domain_from_url(") == 3
