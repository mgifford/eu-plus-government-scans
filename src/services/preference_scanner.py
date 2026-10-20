"""User-preference signal scanner for government website pages.

EN 301 549 v4.1.1 clause 9.7 says a web page must not block or explicitly
override the user agent's modes that present the page according to the
user's own preference settings (colour filters, contrast, text size, pointer
size, text cursor, reduced motion) unless that is essential to the content.
The most common CSS levers that *respect* those settings are the media
features and properties this scan looks for:

- ``prefers-color-scheme`` / ``color-scheme`` — dark/light colour scheme
- ``prefers-reduced-motion`` — OS "reduce motion"
- ``prefers-contrast`` — OS "increase contrast"
- ``prefers-reduced-transparency`` — OS "reduce transparency"
- ``forced-colors`` — Windows contrast themes / forced-colours mode
- ``forced-color-adjust`` — named in NOTE 4 of clause 9.7 as the property
  that *overrides* user settings; ``forced-color-adjust: none`` is therefore
  recorded as an override risk rather than as support

Detection runs in two cheap tiers plus an optional runtime tier that is not
implemented here:

1. **HTML tier** (no extra requests): inline ``<style>`` blocks, ``style=``
   attributes, inline scripts (``matchMedia``), ``<meta name="color-scheme">``
   and design-system adoption signatures, all from the page HTML the scanner
   already fetched.
2. **CSS tier**: the page's linked stylesheets are fetched (capped per page,
   cached per URL across the batch so shared framework CSS is downloaded
   once) and scanned for the same features.  Each feature is attributed to
   its origin — HTML, first-party CSS, or third-party CSS — because a
   ``prefers-reduced-motion`` hit that comes from a framework is weaker
   evidence of deliberate design than one in the site's own stylesheet.
3. **Runtime tier** (future work): load the page in headless Chromium with
   ``prefers-color-scheme: dark`` / ``forced-colors`` emulation and diff
   computed styles.  That is the only way to catch JS-driven theming and to
   prove *effective* support rather than the mere presence of a query.

**A positive result is a signal, not a conformance verdict.**  Clause 9.7 is
a "do not override" rule: a page with no media queries at all can still pass
it, and a page whose stylesheet mentions ``prefers-color-scheme`` may still
break in forced-colours mode.  The scan measures evidence of effort and one
concrete risk; it cannot clear or fail a site on its own.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

from src.lib.design_system_registry import DesignSystemRegistry

# ---------------------------------------------------------------------------
# Feature inventory
# ---------------------------------------------------------------------------

# Media features and CSS properties that indicate a page responds to a
# browser/OS-level user preference.  Kept as exact strings; matching uses
# word-ish boundaries (see _compile_feature_regex) so that "color-scheme"
# does not match inside "prefers-color-scheme".
PREFERENCE_FEATURES: tuple[str, ...] = (
    "prefers-color-scheme",
    "prefers-reduced-motion",
    "prefers-contrast",
    "prefers-reduced-transparency",
    "forced-colors",
    "color-scheme",
)

# The override property named in NOTE 4 of EN 301 549 clause 9.7.  Any use is
# recorded; use with the value ``none`` is what removes user colours.
OVERRIDE_PROPERTY = "forced-color-adjust"
_OVERRIDE_NONE_RE = re.compile(
    rf"{re.escape(OVERRIDE_PROPERTY)}\s*:\s*none", re.IGNORECASE
)

# Script-side hints that a page implements its own theme switcher (which the
# static tiers cannot see the styling for).
THEME_HINT_PATTERNS: dict[str, re.Pattern[str]] = {
    "matchMedia": re.compile(r"matchMedia\s*\("),
    "data-theme": re.compile(r"data-theme"),
    "theme-persistence": re.compile(
        r"(?:localStorage|sessionStorage)[\s\S]{0,60}theme"
        r"|theme[\s\S]{0,60}(?:localStorage|sessionStorage)",
        re.IGNORECASE,
    ),
}

_META_COLOR_SCHEME_RE = re.compile(
    r"<meta\b[^>]*?(?:name\s*=\s*[\"']color-scheme[\"'][^>]*?"
    r"content\s*=\s*[\"']([^\"']+)[\"']"
    r"|content\s*=\s*[\"']([^\"']+)[\"'][^>]*?name\s*=\s*[\"']color-scheme[\"'])",
    re.IGNORECASE,
)

_STYLESHEET_HREF_RE = re.compile(
    r"<link\b[^>]*?rel\s*=\s*[\"']stylesheet[\"'][^>]*?>", re.IGNORECASE
)
_HREF_RE = re.compile(r"href\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)

_FEATURE_REGEXES: dict[str, re.Pattern[str]] = {
    feature: re.compile(rf"(?<![\w-]){re.escape(feature)}(?![\w-])", re.IGNORECASE)
    for feature in (*PREFERENCE_FEATURES, OVERRIDE_PROPERTY)
}


# ---------------------------------------------------------------------------
# Pure detection helpers
# ---------------------------------------------------------------------------

def _find_features(text: str) -> dict[str, int]:
    """Count occurrences of each preference feature/property in *text*.

    Args:
        text: Raw HTML or CSS to scan.

    Returns:
        Mapping of feature name to occurrence count, omitting features that
        were not found.
    """
    counts: dict[str, int] = {}
    for feature, regex in _FEATURE_REGEXES.items():
        found = len(regex.findall(text))
        if found:
            counts[feature] = found
    return counts


def _find_override_risks(text: str) -> list[str]:
    """Return override-risk signals (``forced-color-adjust: none``) in *text*."""
    if _OVERRIDE_NONE_RE.search(text):
        return [f"{OVERRIDE_PROPERTY}: none"]
    return []


def _extract_meta_color_scheme(html: str) -> Optional[str]:
    """Return the content of ``<meta name="color-scheme">`` when present."""
    match = _META_COLOR_SCHEME_RE.search(html)
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip() or None


def _extract_stylesheet_hrefs(html: str, base_url: str) -> list[str]:
    """Return absolute stylesheet URLs referenced by *html*, deduplicated.

    Args:
        html: Raw HTML source of the page.
        base_url: Absolute URL the HTML was fetched from (for resolving
            relative hrefs, including after redirects).

    Returns:
        Absolute http(s) stylesheet URLs in document order, deduplicated.
    """
    hrefs: list[str] = []
    for tag in _STYLESHEET_HREF_RE.findall(html):
        match = _HREF_RE.search(tag)
        if not match:
            continue
        css_url = urljoin(base_url, match.group(1).strip())
        if css_url.startswith(("http://", "https://")) and css_url not in hrefs:
            hrefs.append(css_url)
    return hrefs


def _find_theme_hints(html: str) -> list[str]:
    """Return names of script-side theme-switcher hints present in *html*."""
    return [name for name, regex in THEME_HINT_PATTERNS.items() if regex.search(html)]


def _same_origin(page_url: str, asset_url: str) -> bool:
    """Whether *asset_url* shares the registrable host of *page_url*.

    The ``www.`` prefix is ignored so ``www.example.gov`` and ``example.gov``
    count as the same origin for attribution purposes.
    """
    page_host = (urlparse(page_url).hostname or "").lower().removeprefix("www.")
    asset_host = (urlparse(asset_url).hostname or "").lower().removeprefix("www.")
    return bool(page_host) and page_host == asset_host


def _bump_source(
    sources: dict[str, dict[str, int]],
    feature: str,
    origin: str,
    count: int,
) -> None:
    """Add *count* to *feature*'s tally under *origin* inside *sources*."""
    sources.setdefault(feature, {})
    sources[feature][origin] = sources[feature].get(origin, 0) + count


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PreferenceScanResult:
    """User-preference signals detected for a single URL."""

    url: str
    is_reachable: bool = True
    meta_color_scheme: Optional[str] = None
    features: list[str] = field(default_factory=list)
    feature_sources: dict[str, dict[str, int]] = field(default_factory=dict)
    theme_toggle_hints: list[str] = field(default_factory=list)
    override_signals: list[str] = field(default_factory=list)
    design_systems: list[str] = field(default_factory=list)
    stylesheets_checked: int = 0
    stylesheets_total: int = 0
    error_message: Optional[str] = None
    scanned_at: Optional[str] = None

    @property
    def has_preference_support(self) -> bool:
        """True when at least one preference feature/property was detected."""
        return bool(self.features)

    @property
    def has_override_risk(self) -> bool:
        """True when an explicit override of user settings was detected."""
        return bool(self.override_signals)

    @property
    def css_scanned(self) -> bool:
        """True when at least one external stylesheet was successfully read."""
        return self.stylesheets_checked > 0

    @property
    def feature_count(self) -> int:
        """Number of distinct preference features detected."""
        return len(self.features)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class PreferenceScanner:
    """Scans pages for user-preference signals (tiers 1 and 2).

    The HTML tier runs on already-fetched markup via :meth:`scan_html`; the
    CSS tier fetches linked stylesheets with a per-instance cache so the same
    framework stylesheet shared by thousands of government pages is only
    downloaded once per run.
    """

    def __init__(
        self,
        timeout_seconds: int = 20,
        max_redirects: int = 10,
        user_agent: str = "EU-Government-Accessibility-Scanner/1.0",
        max_stylesheets: int = 6,
        max_css_bytes: int = 400_000,
        registry: Optional[DesignSystemRegistry] = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_redirects = max_redirects
        self.user_agent = user_agent
        self.max_stylesheets = max_stylesheets
        self.max_css_bytes = max_css_bytes
        self.registry = registry if registry is not None else DesignSystemRegistry()
        # css_url -> (feature counts, override risk found) — shared across the
        # whole batch so repeated stylesheets cost one request.
        self._css_cache: dict[str, tuple[dict[str, int], bool]] = {}

    def scan_html(
        self,
        url: str,
        html: str,
        scanned_at: Optional[str] = None,
        final_url: Optional[str] = None,
    ) -> PreferenceScanResult:
        """Analyse pre-fetched HTML (tier 1) without making any requests.

        Args:
            url: The original URL requested.
            html: Raw HTML of the page.
            scanned_at: ISO-8601 timestamp string.  Defaults to *now* in UTC.
            final_url: URL after redirects, used to resolve stylesheet hrefs.
                Defaults to *url*.

        Returns:
            :class:`PreferenceScanResult` with HTML-tier signals populated and
            ``stylesheets_checked=0`` (the CSS tier has not run).
        """
        if scanned_at is None:
            scanned_at = datetime.now(timezone.utc).isoformat()

        try:
            features: dict[str, int] = {}
            sources: dict[str, dict[str, int]] = {}
            for feature, count in _find_features(html).items():
                features[feature] = count
                _bump_source(sources, feature, "html", count)

            override_signals = _find_override_risks(html)
            stylesheet_hrefs = _extract_stylesheet_hrefs(html, final_url or url)
        except Exception as exc:  # noqa: BLE001
            return PreferenceScanResult(
                url=url,
                is_reachable=True,
                error_message=f"Parse error: {exc}",
                scanned_at=scanned_at,
            )

        return PreferenceScanResult(
            url=url,
            is_reachable=True,
            meta_color_scheme=_extract_meta_color_scheme(html),
            features=sorted(features),
            feature_sources=sources,
            theme_toggle_hints=_find_theme_hints(html),
            override_signals=override_signals,
            design_systems=self.registry.matched_systems(html),
            stylesheets_total=len(stylesheet_hrefs),
            scanned_at=scanned_at,
        )

    async def _apply_css_tier(
        self,
        result: PreferenceScanResult,
        html: str,
        final_url: str,
        client: httpx.AsyncClient,
    ) -> None:
        """Fetch linked stylesheets and merge their signals into *result*.

        Stylesheet failures are non-fatal: the page result stands on its HTML
        tier, and ``stylesheets_checked`` simply reports how much of the CSS
        tier actually ran so the report can state CSS coverage honestly.
        """
        hrefs = _extract_stylesheet_hrefs(html, final_url)
        for css_url in hrefs[: self.max_stylesheets]:
            cached = self._css_cache.get(css_url)
            if cached is None:
                try:
                    response = await client.get(css_url)
                    if response.status_code != 200:
                        continue
                    body = response.text[: self.max_css_bytes]
                except httpx.HTTPError:
                    continue
                cached = (_find_features(body), bool(_find_override_risks(body)))
                self._css_cache[css_url] = cached

            css_features, css_override = cached
            origin = "first_party_css" if _same_origin(final_url, css_url) else "third_party_css"
            for feature, count in css_features.items():
                _bump_source(result.feature_sources, feature, origin, count)
                if feature not in result.features:
                    result.features.append(feature)
            if css_override:
                signal = f"{OVERRIDE_PROPERTY}: none"
                if signal not in result.override_signals:
                    result.override_signals.append(signal)
            result.stylesheets_checked += 1

        result.features.sort()

    async def scan_url(
        self,
        url: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> PreferenceScanResult:
        """Fetch a URL and run both detection tiers against it.

        Args:
            url: The URL to fetch and scan.
            client: Shared HTTP client (set by the batch runner so connection
                reuse and the CSS cache apply across the batch).  When ``None``
                a short-lived client is created for this call.

        Returns:
            :class:`PreferenceScanResult` with HTML- and CSS-tier signals.
        """
        scanned_at = datetime.now(timezone.utc).isoformat()
        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient(
                follow_redirects=True,
                max_redirects=self.max_redirects,
                timeout=self.timeout_seconds,
            )

        try:
            try:
                response = await client.get(url, headers={"User-Agent": self.user_agent})
                html = response.text
                final_url = str(response.url)
            except httpx.TooManyRedirects as exc:
                return self._error_result(url, f"Too many redirects: {exc}", scanned_at)
            except httpx.TimeoutException as exc:
                return self._error_result(url, f"Timeout: {exc}", scanned_at)
            except httpx.ConnectError as exc:
                return self._error_result(url, f"Connection error: {exc}", scanned_at)
            except httpx.HTTPError as exc:
                return self._error_result(url, f"HTTP error: {exc}", scanned_at)
            except Exception as exc:  # noqa: BLE001
                return self._error_result(url, f"Unexpected error: {exc}", scanned_at)

            result = self.scan_html(url, html, scanned_at=scanned_at, final_url=final_url)
            await self._apply_css_tier(result, html, final_url, client)
            return result
        finally:
            if owns_client:
                await client.aclose()

    @staticmethod
    def _error_result(url: str, message: str, scanned_at: str) -> PreferenceScanResult:
        """Return an unreachable result carrying *message*."""
        return PreferenceScanResult(
            url=url,
            is_reachable=False,
            error_message=message,
            scanned_at=scanned_at,
        )

    async def scan_urls_batch(
        self,
        urls: list[str],
        rate_limit_per_second: float = 1.0,
        max_runtime_seconds: Optional[float] = None,
        start_time: Optional[float] = None,
        on_result: Optional[Callable[[PreferenceScanResult], None]] = None,
    ) -> dict[str, PreferenceScanResult]:
        """Scan multiple URLs with rate limiting and a shared HTTP client.

        Args:
            urls: List of URLs to scan.
            rate_limit_per_second: Maximum requests per second.
            max_runtime_seconds: Stop scanning early when this many seconds
                have elapsed since *start_time*, leaving a 60-second safety
                buffer.  ``None`` means no limit.
            start_time: ``time.monotonic()`` value recorded at the start of the
                overall job.  When ``None`` the clock starts here.
            on_result: Optional callback invoked after each URL is scanned
                (before the inter-request delay) for incremental persistence.

        Returns:
            Mapping of URL to :class:`PreferenceScanResult`; only the URLs
            scanned before any early stop are present.
        """
        results: dict[str, PreferenceScanResult] = {}
        delay = 1.0 / rate_limit_per_second if rate_limit_per_second > 0 else 0
        delay = min(delay, 60.0)
        _start = start_time if start_time is not None else time.monotonic()
        _safety_buffer = 60.0

        async with httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=self.max_redirects,
            timeout=self.timeout_seconds,
            headers={"User-Agent": self.user_agent},
        ) as client:
            total = len(urls)
            for idx, url in enumerate(urls, 1):
                if max_runtime_seconds is not None:
                    elapsed = time.monotonic() - _start
                    remaining = max_runtime_seconds - elapsed
                    if remaining < _safety_buffer:
                        print(
                            f"  ⏱️  Time budget near limit "
                            f"({elapsed / 60:.1f}m elapsed, "
                            f"{remaining / 60:.1f}m remaining) "
                            f"— stopping after {idx - 1}/{total} URLs"
                        )
                        break

                print(f"  [{idx}/{total}] Scanning: {url}")
                result = await self.scan_url(url, client=client)
                results[url] = result

                if on_result is not None:
                    on_result(result)

                if result.error_message:
                    print(f"      ✗ {result.error_message}")
                else:
                    signals = ", ".join(result.features) if result.features else "none"
                    print(
                        f"      {'⚠' if result.has_override_risk else '✓'} "
                        f"Features: {signals} "
                        f"(css {result.stylesheets_checked}/{result.stylesheets_total})"
                    )

                if delay > 0:
                    await asyncio.sleep(delay)

        return results
