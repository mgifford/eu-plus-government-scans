"""URL validation service for checking government site accessibility."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

import httpx


@dataclass(slots=True)
class ValidationResult:
    """Result of a URL validation check."""
    url: str
    is_valid: bool
    status_code: int | None = None
    error_message: str | None = None
    redirected_to: str | None = None
    redirect_chain: List[str] | None = None
    validated_at: str | None = None


class UrlValidator:
    """Service for validating URL accessibility with redirect tracking."""

    def __init__(
        self,
        timeout_seconds: int = 20,
        max_redirects: int = 10,
        user_agent: str = "EU-Government-Accessibility-Scanner/1.0",
    ):
        self.timeout_seconds = timeout_seconds
        self.max_redirects = max_redirects
        self.user_agent = user_agent

    async def validate_url(self, url: str) -> ValidationResult:
        """
        Validate a single URL and track redirects.
        
        Returns ValidationResult with success/failure status, error codes,
        and redirect information.
        """
        validated_at = datetime.now(timezone.utc).isoformat()
        
        # Track redirect chain
        redirect_chain: List[str] = []
        
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                max_redirects=self.max_redirects,
                timeout=self.timeout_seconds,
                event_hooks={
                    "response": [self._track_redirect(redirect_chain)]
                },
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                )
                
                # Determine final URL after redirects
                final_url = str(response.url)
                redirected_to = final_url if final_url != url else None
                
                # Consider 2xx and 3xx as valid (3xx should have been followed)
                is_valid = response.status_code < 400
                
                return ValidationResult(
                    url=url,
                    is_valid=is_valid,
                    status_code=response.status_code,
                    redirected_to=redirected_to,
                    redirect_chain=redirect_chain if redirect_chain else None,
                    validated_at=validated_at,
                )
                
        except httpx.TooManyRedirects as e:
            return ValidationResult(
                url=url,
                is_valid=False,
                error_message=f"Too many redirects: {str(e)}",
                validated_at=validated_at,
            )
        except httpx.TimeoutException as e:
            return ValidationResult(
                url=url,
                is_valid=False,
                error_message=f"Timeout: {str(e)}",
                validated_at=validated_at,
            )
        except httpx.ConnectError as e:
            return ValidationResult(
                url=url,
                is_valid=False,
                error_message=f"Connection error: {str(e)}",
                validated_at=validated_at,
            )
        except httpx.HTTPError as e:
            return ValidationResult(
                url=url,
                is_valid=False,
                error_message=f"HTTP error: {str(e)}",
                validated_at=validated_at,
            )
        except Exception as e:
            return ValidationResult(
                url=url,
                is_valid=False,
                error_message=f"Unexpected error: {str(e)}",
                validated_at=validated_at,
            )

    def _track_redirect(self, redirect_chain: List[str]):
        """
        Create event hook to track redirect chain.
        
        Returns a callback function for use with httpx event hooks that
        appends intermediate redirect URLs to the redirect_chain list
        when responses have redirect status codes (3xx).
        
        Args:
            redirect_chain: List to accumulate redirect URLs
            
        Returns:
            Event hook function that accepts an httpx Response
        """
        def hook(response: httpx.Response):
            if response.is_redirect:
                redirect_chain.append(str(response.url))
        return hook

    async def validate_urls_batch(
        self,
        urls: List[str],
        rate_limit_per_second: float = 2.0,
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to validate
            rate_limit_per_second: Maximum requests per second
            
        Returns:
            Dictionary mapping URL to ValidationResult
        """
        results: Dict[str, ValidationResult] = {}
        delay = 1.0 / rate_limit_per_second if rate_limit_per_second > 0 else 0
        
        total = len(urls)
        for idx, url in enumerate(urls, 1):
            print(f"  [{idx}/{total}] Validating: {url}")
            result = await self.validate_url(url)
            results[url] = result
            
            # Print result status
            if result.is_valid:
                status_msg = f"✓ {result.status_code}" if result.status_code else "✓"
                if result.redirected_to:
                    status_msg += f" → {result.redirected_to}"
            else:
                status_msg = f"✗ {result.error_message or 'Failed'}"
            print(f"      {status_msg}")
            
            # Rate limiting delay
            if delay > 0:
                await asyncio.sleep(delay)
        
        return results
