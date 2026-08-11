import pytest
from src.lib.gov_domain_registry import GovernmentDomainRegistry
from src.services.relationship_scanner import RelationshipScanner


@pytest.fixture
def scanner():
    return RelationshipScanner()


class _FakeRegistry(GovernmentDomainRegistry):
    """A registry pre-seeded with fixed domains, bypassing disk I/O."""

    def __init__(self, domains: dict[str, str]):
        self._domain_to_country = {d.lower(): c for d, c in domains.items()}


def test_normalize_url_basic(scanner):
    base = "https://www.example.gov/path/page.html"
    result = scanner._normalize_url("/about", base)
    assert result is not None
    url, host, domain = result
    assert url == "https://www.example.gov/about"
    assert host == "www.example.gov"
    assert domain == "example.gov"


def test_normalize_url_removes_fragment(scanner):
    base = "https://example.gov"
    result = scanner._normalize_url("https://example.gov/page#section", base)
    assert result is not None
    assert result[0] == "https://example.gov/page"


def test_normalize_url_removes_default_ports(scanner):
    base = "https://example.gov"
    res1 = scanner._normalize_url("http://example.com:80/path", base)
    assert res1[0] == "http://example.com/path"

    res2 = scanner._normalize_url("https://example.com:443/path", base)
    assert res2[0] == "https://example.com/path"


def test_normalize_url_idna(scanner):
    base = "https://example.gov"
    res = scanner._normalize_url("https://xn--ls-eka.is", base)
    # the IDNA conversion should map it correctly, testing basic IDNA
    assert res is not None
    assert "xn--ls-eka.is" in res[1] or "lás.is" in res[1]  # Depends on idna decode behavior


def test_get_category_unknown(scanner):
    assert scanner._get_category("unknown-domain.com") == "unknown_external"


def test_get_category_known(scanner):
    # Mock category
    scanner.categories["google-analytics.com"] = "analytics"
    assert scanner._get_category("google-analytics.com") == "analytics"


def test_get_category_cross_country_government_link():
    """A link to a *different* known government domain (e.g. a Spanish
    ministry linking to govern.cat) must be categorized as known_government,
    not fall through to unknown_external -- this was the target_category
    mislabeling bug: 'known_government' previously just meant same-origin."""
    registry = _FakeRegistry({"govern.cat": "SPAIN", "gob.es": "SPAIN"})
    scanner = RelationshipScanner(gov_registry=registry)
    assert scanner._get_category("govern.cat") == "known_government"


def test_get_category_same_origin_not_in_registry_is_not_government():
    """Same-origin alone must no longer be sufficient to label a domain as
    government -- only registry membership should. (Regression guard for the
    'is_external else known_government' bug.)"""
    registry = _FakeRegistry({"gob.es": "SPAIN"})
    scanner = RelationshipScanner(gov_registry=registry)
    assert scanner._get_category("not-in-registry.com") == "unknown_external"


def test_get_category_prefers_registry_over_third_party_rules():
    registry = _FakeRegistry({"gob.es": "SPAIN"})
    scanner = RelationshipScanner(gov_registry=registry)
    scanner.categories["gob.es"] = "cdn"  # should never happen, but registry wins
    assert scanner._get_category("gob.es") == "known_government"


def test_scan_html_cross_domain_government_link_categorized_correctly():
    registry = _FakeRegistry({"source.gov": "SPAIN", "target.gov": "SPAIN"})
    scanner = RelationshipScanner(gov_registry=registry)
    html = '<html><body><a href="https://target.gov/page">Link</a></body></html>'
    result = scanner.scan_html("https://source.gov", html)
    assert len(result.relationships) == 1
    assert result.relationships[0].target_category == "known_government"
    assert result.relationships[0].is_external is True


def test_scan_html_deduplication(scanner):
    html = """
    <html>
      <body>
        <a href="https://target.com/page1">Link 1</a>
        <a href="https://target.com/page2">Link 2</a>
      </body>
    </html>
    """
    result = scanner.scan_html("https://source.gov", html)
    # Even though there are two links, they both go to target.com via editorial_link
    # So deduplication should result in 1 edge
    assert len(result.relationships) == 1
    edge = result.relationships[0]
    assert edge.source_domain == "source.gov"
    assert edge.target_domain == "target.com"
    assert edge.relationship_type == "editorial_link"
