"""URL validation service for checking government site accessibility."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

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

    def _new_client(self) -> httpx.AsyncClient:
        """Build a client configured with this validator's limits."""
        return httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=self.max_redirects,
            timeout=self.timeout_seconds,
        )

    async def validate_url(
        self,
        url: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> ValidationResult:
        """
        Validate a single URL and track redirects.

        Args:
            url: URL to validate.
            client: Optional client to reuse.  Passing one lets a batch share a
                single connection pool instead of completing a fresh TLS
                handshake per URL, which matters across tens of thousands of
                URLs.  When omitted a client is created for this call alone.

        Returns:
            ValidationResult with success/failure status, error codes, and
            redirect information.
        """
        validated_at = datetime.now(timezone.utc).isoformat()

        owned_client = client is None
        if client is None:
            client = self._new_client()

        try:
            response = await client.get(
                url,
                headers={"User-Agent": self.user_agent},
            )

            # Determine final URL after redirects
            final_url = str(response.url)
            redirected_to = final_url if final_url != url else None

            # httpx records every intermediate redirect response in .history,
            # so the chain comes straight off the response rather than needing
            # a client-level event hook (which could not be scoped per request
            # once the client is shared across a batch).
            redirect_chain = [str(hop.url) for hop in response.history]

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
        finally:
            # Only close what this call created; a shared client outlives it.
            if owned_client:
                await client.aclose()

    async def validate_urls_batch(
        self,
        urls: List[str],
        rate_limit_per_second: float = 2.0,
        max_runtime_seconds: Optional[float] = None,
        start_time: Optional[float] = None,
        on_result: Optional[Callable[["ValidationResult"], None]] = None,
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple URLs with rate limiting.

        Args:
            urls: List of URLs to validate.
            rate_limit_per_second: Maximum requests per second.
            max_runtime_seconds: Stop validating early when this many seconds
                have elapsed since *start_time*, leaving a 60-second safety
                buffer.  ``None`` means no limit.
            start_time: ``time.monotonic()`` value recorded at the start of
                the overall job.  When ``None`` the clock starts at the first
                call to this method.
            on_result: Optional callback invoked immediately after each URL is
                validated (before the inter-request delay).  Useful for
                incremental persistence so that partial results survive a
                timeout.

        Returns:
            Dictionary mapping URL to ValidationResult.  When stopped early
            the dict contains only the URLs that were actually validated.
        """
        results: Dict[str, ValidationResult] = {}
        delay = 1.0 / rate_limit_per_second if rate_limit_per_second > 0 else 0

        _start = start_time if start_time is not None else time.monotonic()
        # Stop validating this many seconds before the hard deadline so the
        # caller has time to flush results and upload artifacts.
        _safety_buffer = 60.0

        total = len(urls)
        # One client for the whole batch: connections and TLS sessions are
        # reused across URLs instead of being renegotiated for each of the tens
        # of thousands of URLs a full run covers.
        async with self._new_client() as client:
            for idx, url in enumerate(urls, 1):
                # Check remaining runtime budget before making the next request.
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

                print(f"  [{idx}/{total}] Validating: {url}")
                result = await self.validate_url(url, client=client)
                results[url] = result

                if on_result is not None:
                    on_result(result)

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
