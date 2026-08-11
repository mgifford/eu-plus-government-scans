import pytest
from src.services.relationship_scanner import RelationshipScanner


@pytest.fixture
def scanner():
    return RelationshipScanner()


def test_integration_extract_various_relationships(scanner):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="https://cdn.example.com/styles.css">
        <link rel="preload" href="/fonts/custom.woff2" as="font">
        <script src="https://analytics.example.com/tracker.js"></script>
    </head>
    <body>
        <header>
            <a href="https://login.example.gov">Login</a>
        </header>
        <main>
            <form action="https://search.example.gov/query">
                <input type="text" name="q">
            </form>
            <img src="https://images.example.com/hero.jpg">
            <a href="/about">About Us</a>
        </main>
        <footer>
            <a href="https://twitter.com/examplegov">Twitter</a>
        </footer>
    </body>
    </html>
    """
    url = "https://www.example.gov"
    result = scanner.scan_html(url, html)

    assert result.is_reachable is True
    assert len(result.relationships) > 0

    types = [edge.relationship_type for edge in result.relationships]
    assert "stylesheet_dependency" in types
    assert "font_or_preload_dependency" in types
    assert "script_dependency" in types
    assert "editorial_link" in types
    assert "form_destination" in types
    assert "image_or_media_dependency" in types

    # Check specific edge
    twitter_edges = [e for e in result.relationships if e.target_domain == "twitter.com"]
    assert len(twitter_edges) == 1
    assert twitter_edges[0].page_region == "footer"

    login_edges = [e for e in result.relationships if e.target_domain == "example.gov"]
    assert any(e.page_region == "header" for e in login_edges)
