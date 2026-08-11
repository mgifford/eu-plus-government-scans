"""Unit tests for URL validator service."""

from contextlib import contextmanager
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.url_validator import UrlValidator


def _response(status_code=200, url="https://example.com/", history=()):
    """Build a stand-in httpx response.

    ``history`` carries the intermediate redirect responses, which is where the
    validator reads the redirect chain from.
    """
    response = Mock()
    response.status_code = status_code
    response.url = url
    response.is_redirect = False
    response.history = [Mock(url=hop) for hop in history]
    return response


@contextmanager
def mock_http(get):
    """Patch ``httpx.AsyncClient`` with a client whose ``get`` is *get*.

    The validator uses a client either directly (single call, which then closes
    it) or as an async context manager (batch, sharing one pool across URLs), so
    the double has to support both.
    """
    client = AsyncMock()
    client.get = get
    client.aclose = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    with patch("httpx.AsyncClient", return_value=client) as factory:
        yield factory, client


def _responder(urls):
    """Return an async ``get`` that echoes back whichever URL was requested."""

    async def get(*args, **kwargs):
        url = args[0] if args else kwargs.get("url", urls[0])
        return _response(url=url)

    return AsyncMock(side_effect=get)


@pytest.mark.asyncio
async def test_validate_url_success():
    """Test successful URL validation."""
    validator = UrlValidator(timeout_seconds=10)

    with mock_http(AsyncMock(return_value=_response())):
        result = await validator.validate_url("https://example.com/")

    assert result.is_valid is True
    assert result.status_code == 200
    assert result.url == "https://example.com/"
    assert result.error_message is None
    assert result.redirected_to is None


@pytest.mark.asyncio
async def test_validate_url_redirect():
    """Test URL validation with redirect."""
    validator = UrlValidator(timeout_seconds=10)
    response = _response(url="https://example.com/new-page")

    with mock_http(AsyncMock(return_value=response)):
        result = await validator.validate_url("https://example.com/old-page")

    assert result.is_valid is True
    assert result.status_code == 200
    assert result.url == "https://example.com/old-page"
    assert result.redirected_to == "https://example.com/new-page"


@pytest.mark.asyncio
async def test_redirect_chain_comes_from_response_history():
    """Intermediate hops are read off httpx's own redirect history."""
    validator = UrlValidator(timeout_seconds=10)
    response = _response(
        url="https://example.com/final",
        history=["https://example.com/first", "https://example.com/second"],
    )

    with mock_http(AsyncMock(return_value=response)):
        result = await validator.validate_url("https://example.com/first")

    assert result.redirect_chain == [
        "https://example.com/first",
        "https://example.com/second",
    ]


@pytest.mark.asyncio
async def test_no_redirect_chain_when_not_redirected():
    """A direct response records no chain rather than an empty list."""
    validator = UrlValidator(timeout_seconds=10)

    with mock_http(AsyncMock(return_value=_response())):
        result = await validator.validate_url("https://example.com/")

    assert result.redirect_chain is None


@pytest.mark.asyncio
async def test_validate_url_404():
    """Test URL validation with 404 error."""
    validator = UrlValidator(timeout_seconds=10)
    response = _response(status_code=404, url="https://example.com/missing")

    with mock_http(AsyncMock(return_value=response)):
        result = await validator.validate_url("https://example.com/missing")

    assert result.is_valid is False
    assert result.status_code == 404
    assert result.error_message is None


@pytest.mark.asyncio
async def test_validate_url_timeout():
    """Test URL validation with timeout."""
    import httpx

    validator = UrlValidator(timeout_seconds=1)

    with mock_http(AsyncMock(side_effect=httpx.TimeoutException("Timeout"))):
        result = await validator.validate_url("https://slow-example.com/")

    assert result.is_valid is False
    assert result.status_code is None
    assert "Timeout" in result.error_message


@pytest.mark.asyncio
async def test_validate_url_connection_error():
    """Test URL validation with connection error."""
    import httpx

    validator = UrlValidator(timeout_seconds=10)

    with mock_http(AsyncMock(side_effect=httpx.ConnectError("Connection failed"))):
        result = await validator.validate_url("https://unreachable.example.com/")

    assert result.is_valid is False
    assert result.status_code is None
    assert "Connection error" in result.error_message


@pytest.mark.asyncio
async def test_standalone_call_closes_the_client_it_created():
    """A one-off validation must not leak the connection pool it opened."""
    validator = UrlValidator(timeout_seconds=10)

    with mock_http(AsyncMock(return_value=_response())) as (_factory, client):
        await validator.validate_url("https://example.com/")

    client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_caller_supplied_client_is_not_closed():
    """A shared client outlives the individual request."""
    validator = UrlValidator(timeout_seconds=10)

    with mock_http(AsyncMock(return_value=_response())) as (_factory, client):
        await validator.validate_url("https://example.com/", client=client)

    client.aclose.assert_not_awaited()


@pytest.mark.asyncio
async def test_batch_reuses_a_single_client():
    """The batch opens one connection pool rather than one per URL.

    Re-handshaking per URL is what made a full run of tens of thousands of URLs
    needlessly slow.
    """
    validator = UrlValidator(timeout_seconds=10)
    urls = [f"https://example{i}.com/" for i in range(5)]

    with mock_http(_responder(urls)) as (factory, _client):
        results = await validator.validate_urls_batch(urls, rate_limit_per_second=0)

    assert len(results) == 5
    assert factory.call_count == 1


@pytest.mark.asyncio
async def test_validate_urls_batch():
    """Test batch URL validation."""
    validator = UrlValidator(timeout_seconds=10)
    urls = [
        "https://example1.com/",
        "https://example2.com/",
        "https://example3.com/",
    ]

    with mock_http(_responder(urls)):
        results = await validator.validate_urls_batch(urls, rate_limit_per_second=0)

    assert len(results) == 3
    assert all(r.is_valid for r in results.values())
    assert all(r.url in urls for r in results.values())


@pytest.mark.asyncio
async def test_validate_urls_batch_stops_early_when_budget_exhausted():
    """Test that validate_urls_batch stops early when the time budget runs out."""
    import time

    validator = UrlValidator(timeout_seconds=10)
    urls = [f"https://example{i}.com/" for i in range(10)]

    with mock_http(_responder(urls)):
        # Set start_time far in the past so the budget is already exhausted
        past_start = time.monotonic() - 10_000
        results = await validator.validate_urls_batch(
            urls,
            rate_limit_per_second=0,
            max_runtime_seconds=100,   # budget = 100 s; but 10,000 s have elapsed
            start_time=past_start,
        )

    # Should have processed 0 URLs because the budget is already exhausted
    assert len(results) == 0


@pytest.mark.asyncio
async def test_validate_urls_batch_on_result_called_for_each_url():
    """Test that the on_result callback is called for every URL validated."""
    validator = UrlValidator(timeout_seconds=10)
    urls = [
        "https://example1.com/",
        "https://example2.com/",
    ]
    collected: list = []

    with mock_http(_responder(urls)):
        results = await validator.validate_urls_batch(
            urls,
            rate_limit_per_second=0,
            on_result=collected.append,
        )

    assert len(collected) == 2
    assert len(results) == 2


@pytest.mark.asyncio
async def test_validate_urls_batch_no_max_runtime_validates_all():
    """With no max_runtime_seconds all URLs should be validated."""
    validator = UrlValidator(timeout_seconds=10)
    urls = [f"https://example{i}.com/" for i in range(5)]

    with mock_http(_responder(urls)):
        results = await validator.validate_urls_batch(urls, rate_limit_per_second=0)

    assert len(results) == 5
