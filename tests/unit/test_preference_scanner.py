"""Unit tests for the user-preference signal scanner (tiers 1 and 2)."""

from __future__ import annotations

import httpx
import pytest

from src.lib.design_system_registry import DesignSystemRegistry
from src.services.preference_scanner import (
    PREFERENCE_FEATURES,
    PreferenceScanner,
    _extract_meta_color_scheme,
    _extract_stylesheet_hrefs,
    _find_features,
    _find_override_risks,
    _find_theme_hints,
    _same_origin,
)


def _registry_with(tmp_path, signature: str = "example-ds") -> DesignSystemRegistry:
    """Build a registry containing one system whose signature is *signature*."""
    from pathlib import Path

    import yaml

    path: Path = tmp_path / "design-systems.yaml"
    path.write_text(
        yaml.safe_dump({
            "design_systems": [{
                "name": "Example Design System",
                "country_code": "ESTONIA",
                "type": "design_system",
                "url": "https://example.gov/design",
                "adoption_signatures": [signature],
                "confidence": "high",
                "needs_review": False,
            }]
        }),
        encoding="utf-8",
    )
    return DesignSystemRegistry(path)


class TestFeatureDetection:
    """Regex-level detection over raw HTML/CSS text."""

    def test_prefers_color_scheme_is_not_counted_as_color_scheme(self) -> None:
        counts = _find_features(":root {} @media (prefers-color-scheme: dark) {}")
        assert counts.get("prefers-color-scheme") == 1
        assert "color-scheme" not in counts

    def test_bare_color_scheme_property_is_counted(self) -> None:
        counts = _find_features(":root { color-scheme: light dark; }")
        assert counts.get("color-scheme") == 1
        assert "prefers-color-scheme" not in counts

    def test_all_media_features_detected_together(self) -> None:
        text = """
        @media (prefers-reduced-motion: reduce) {}
        @media (prefers-contrast: more) {}
        @media (prefers-reduced-transparency: reduce) {}
        @media (forced-colors: active) {}
        """
        counts = _find_features(text)
        assert set(counts) == {
            "prefers-reduced-motion",
            "prefers-contrast",
            "prefers-reduced-transparency",
            "forced-colors",
        }

    def test_forced_colors_is_distinct_from_forced_color_adjust(self) -> None:
        counts = _find_features("a { forced-color-adjust: none; }")
        assert "forced-colors" not in counts
        assert counts.get("forced-color-adjust") == 1

    def test_case_insensitive(self) -> None:
        assert _find_features("@media (FORCED-COLORS: active)").get("forced-colors") == 1

    def test_unknown_text_yields_nothing(self) -> None:
        assert _find_features("<p>plain content</p>") == {}


class TestOverrideRisks:
    """forced-color-adjust: none is the clause 9.7 override signal."""

    def test_detects_none_value(self) -> None:
        assert _find_override_risks("a{forced-color-adjust:none}") == [
            "forced-color-adjust: none"
        ]

    def test_detects_none_with_whitespace(self) -> None:
        assert _find_override_risks("a { forced-color-adjust :  none ; }")

    def test_other_values_are_not_risks(self) -> None:
        assert _find_override_risks("a { forced-color-adjust: preserve; }") == []


class TestHtmlExtraction:
    """Meta tags, stylesheet links, and script-side theme hints."""

    @pytest.mark.parametrize(
        "tag,expected",
        [
            ('<meta name="color-scheme" content="light dark">', "light dark"),
            ('<meta content="dark" name="color-scheme">', "dark"),
        ],
    )
    def test_meta_color_scheme_both_attribute_orders(
        self, tag: str, expected: str
    ) -> None:
        assert _extract_meta_color_scheme(f"<head>{tag}</head>") == expected

    def test_meta_color_scheme_absent(self) -> None:
        assert _extract_meta_color_scheme("<head></head>") is None

    def test_stylesheet_hrefs_are_absolute_and_deduplicated(self) -> None:
        html = (
            '<link rel="stylesheet" href="/assets/a.css">'
            '<link rel="stylesheet" href="https://cdn.example.org/b.css">'
            '<link rel="stylesheet" href="/assets/a.css">'
            '<link rel="preload" as="style" href="/assets/skip.css">'
        )
        hrefs = _extract_stylesheet_hrefs(html, "https://www.example.gov/page/")
        assert hrefs == [
            "https://www.example.gov/assets/a.css",
            "https://cdn.example.org/b.css",
        ]

    def test_theme_hints_found(self) -> None:
        html = (
            "<script>matchMedia('(prefers-color-scheme: dark)')</script>"
            "<div data-theme='dark'></div>"
            "<script>localStorage.setItem('theme', 'dark')</script>"
        )
        hints = _find_theme_hints(html)
        assert "matchMedia" in hints
        assert "data-theme" in hints
        assert "theme-persistence" in hints

    def test_same_origin_ignores_www_prefix(self) -> None:
        assert _same_origin("https://www.example.gov/page", "https://example.gov/a.css")
        assert not _same_origin("https://example.gov/", "https://cdn.other.org/a.css")


class TestScanHtml:
    """Tier 1: everything derived from already-fetched HTML."""

    def test_signals_from_inline_style_and_meta(self) -> None:
        html = """
        <head>
          <meta name="color-scheme" content="light dark">
          <style>:root { color-scheme: light dark; }
                 @media (prefers-reduced-motion: reduce) {}
                 .card { forced-color-adjust: none; }</style>
        </head>
        """
        result = PreferenceScanner().scan_html("https://example.gov/", html)
        assert result.is_reachable
        assert "prefers-reduced-motion" in result.features
        assert "color-scheme" in result.features
        assert result.meta_color_scheme == "light dark"
        assert result.has_preference_support
        assert result.override_signals == ["forced-color-adjust: none"]
        assert result.has_override_risk

    def test_feature_sources_attribute_html_tier(self) -> None:
        html = "<style>@media (forced-colors: active) {}</style>"
        result = PreferenceScanner().scan_html("https://example.gov/", html)
        assert result.feature_sources["forced-colors"]["html"] == 1
        assert result.stylesheets_checked == 0

    def test_adoption_signatures_matched_from_registry(self, tmp_path) -> None:
        html = '<link rel="stylesheet" href="/example-ds.min.css">'
        scanner = PreferenceScanner(registry=_registry_with(tmp_path))
        result = scanner.scan_html("https://example.gov/", html)
        assert result.design_systems == ["Example Design System"]

    def test_clean_page_reports_no_signals(self) -> None:
        result = PreferenceScanner().scan_html("https://example.gov/", "<html></html>")
        assert result.features == []
        assert not result.has_preference_support
        assert not result.has_override_risk

    def test_parse_error_is_reported_not_raised(self) -> None:
        """Unexpected input types surface as an error result, not an exception."""
        result = PreferenceScanner().scan_html("https://example.gov/", b"<html></html>")  # type: ignore[arg-type]
        assert result.error_message is not None
        assert "Parse error" in result.error_message


class TestCssTier:
    """Tier 2: linked stylesheets fetched, attributed, and cached."""

    @staticmethod
    def _client(handler) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(handler))

    @pytest.mark.asyncio
    async def test_css_features_merged_and_attributed(self) -> None:
        html = '<link rel="stylesheet" href="/site.css">'

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/site.css":
                return httpx.Response(200, text="@media (prefers-color-scheme: dark) {}")
            return httpx.Response(200, text=html)

        async with self._client(handler) as client:
            scanner = PreferenceScanner()
            result = await scanner.scan_url("https://www.example.gov/", client=client)

        assert result.is_reachable
        assert "prefers-color-scheme" in result.features
        assert result.stylesheets_checked == 1
        assert result.stylesheets_total == 1
        # www.example.gov page vs example.gov stylesheet: same origin.
        assert result.feature_sources["prefers-color-scheme"]["first_party_css"] == 1
        assert result.css_scanned

    @pytest.mark.asyncio
    async def test_third_party_stylesheet_attributed_separately(self) -> None:
        html = '<link rel="stylesheet" href="https://cdn.vendor.org/x.css">'

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == "cdn.vendor.org":
                return httpx.Response(200, text="a { forced-color-adjust: none; }")
            return httpx.Response(200, text=html)

        async with self._client(handler) as client:
            result = await PreferenceScanner().scan_url(
                "https://example.gov/", client=client
            )

        assert result.override_signals == ["forced-color-adjust: none"]
        assert result.feature_sources["forced-color-adjust"]["third_party_css"] == 1

    @pytest.mark.asyncio
    async def test_stylesheet_fetch_failure_keeps_html_tier(self) -> None:
        html = (
            '<style>@media (prefers-reduced-motion: reduce) {}</style>'
            '<link rel="stylesheet" href="/broken.css">'
        )

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/broken.css":
                return httpx.Response(500, text="server error")
            return httpx.Response(200, text=html)

        async with self._client(handler) as client:
            result = await PreferenceScanner().scan_url(
                "https://example.gov/", client=client
            )

        assert result.is_reachable
        assert "prefers-reduced-motion" in result.features
        assert result.stylesheets_checked == 0

    @pytest.mark.asyncio
    async def test_stylesheets_are_capped(self) -> None:
        links = "".join(
            f'<link rel="stylesheet" href="/s{i}.css">' for i in range(10)
        )

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=links)

        async with self._client(handler) as client:
            scanner = PreferenceScanner(max_stylesheets=3)
            result = await scanner.scan_url("https://example.gov/", client=client)

        assert result.stylesheets_total == 10
        assert result.stylesheets_checked == 3

    @pytest.mark.asyncio
    async def test_css_cache_reuses_first_fetch(self) -> None:
        html = '<link rel="stylesheet" href="/shared.css">'
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request.url.path)
            if request.url.path == "/shared.css":
                return httpx.Response(200, text="a { color-scheme: dark; }")
            return httpx.Response(200, text=html)

        async with self._client(handler) as client:
            scanner = PreferenceScanner()
            await scanner.scan_url("https://example.gov/a", client=client)
            await scanner.scan_url("https://example.gov/b", client=client)

        assert calls.count("/shared.css") == 1

    @pytest.mark.asyncio
    async def test_unreachable_page_reports_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused", request=request)

        async with self._client(handler) as client:
            result = await PreferenceScanner().scan_url(
                "https://dead.example.gov/", client=client
            )

        assert not result.is_reachable
        assert result.error_message
        assert not result.has_preference_support


class TestFeatureInventory:
    """The published inventory must stay internally consistent."""

    def test_no_feature_is_a_suffix_collision_of_another(self) -> None:
        """A short feature name must not appear inside a longer one unbound-ed."""
        for i, a in enumerate(PREFERENCE_FEATURES):
            for b in PREFERENCE_FEATURES[i + 1:]:
                assert a != b
        assert "color-scheme" in PREFERENCE_FEATURES
        assert "prefers-color-scheme" in PREFERENCE_FEATURES
