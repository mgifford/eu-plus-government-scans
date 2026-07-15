import pytest
from src.services.relationship_scanner import RelationshipScanner


@pytest.fixture
def scanner():
    return RelationshipScanner()


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
