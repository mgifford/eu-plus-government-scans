"""Unit tests for URL validator service."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.services.url_validator import UrlValidator, ValidationResult


@pytest.mark.asyncio
async def test_validate_url_success():
    """Test successful URL validation."""
    validator = UrlValidator(timeout_seconds=10)
    
    # Mock httpx response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://example.com/"
    mock_response.is_redirect = False
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
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
    
    # Mock httpx response with redirect
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://example.com/new-page"
    mock_response.is_redirect = False
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await validator.validate_url("https://example.com/old-page")
        
        assert result.is_valid is True
        assert result.status_code == 200
        assert result.url == "https://example.com/old-page"
        assert result.redirected_to == "https://example.com/new-page"


@pytest.mark.asyncio
async def test_validate_url_404():
    """Test URL validation with 404 error."""
    validator = UrlValidator(timeout_seconds=10)
    
    # Mock httpx response with 404
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.url = "https://example.com/missing"
    mock_response.is_redirect = False
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await validator.validate_url("https://example.com/missing")
        
        assert result.is_valid is False
        assert result.status_code == 404
        assert result.error_message is None


@pytest.mark.asyncio
async def test_validate_url_timeout():
    """Test URL validation with timeout."""
    import httpx
    
    validator = UrlValidator(timeout_seconds=1)
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await validator.validate_url("https://slow-example.com/")
        
        assert result.is_valid is False
        assert result.status_code is None
        assert "Timeout" in result.error_message


@pytest.mark.asyncio
async def test_validate_url_connection_error():
    """Test URL validation with connection error."""
    import httpx
    
    validator = UrlValidator(timeout_seconds=10)
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await validator.validate_url("https://unreachable.example.com/")
        
        assert result.is_valid is False
        assert result.status_code is None
        assert "Connection error" in result.error_message


@pytest.mark.asyncio
async def test_validate_urls_batch():
    """Test batch URL validation."""
    validator = UrlValidator(timeout_seconds=10)
    
    urls = [
        "https://example1.com/",
        "https://example2.com/",
        "https://example3.com/",
    ]
    
    # Mock successful responses for all URLs
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.is_redirect = False
    
    async def mock_get_side_effect(*args, **kwargs):
        # Return mock response with URL from the call
        url_arg = args[0] if args else kwargs.get('url', urls[0])
        mock_response.url = url_arg
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(side_effect=mock_get_side_effect)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        results = await validator.validate_urls_batch(urls, rate_limit_per_second=0)
        
        assert len(results) == 3
        assert all(r.is_valid for r in results.values())
        assert all(r.url in urls for r in results.values())
