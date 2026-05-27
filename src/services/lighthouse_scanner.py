"""Google Lighthouse scan service for government websites.

Runs the Lighthouse CLI via subprocess and extracts key audit scores
(performance, accessibility, best-practices, SEO, PWA) for each URL.

Requires the ``lighthouse`` CLI to be installed globally:
    npm install -g lighthouse

Chrome / Chromium must also be available on the system PATH.  In GitHub
Actions the ``ubuntu-latest`` runner ships with Chromium pre-installed.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence
from urllib.parse import urlparse


@dataclass(slots=True)
class LighthouseScanResult:
    """Result of a Google Lighthouse scan for a single URL."""

    url: str
    performance_score: float | None = None    # 0.0–1.0
    accessibility_score: float | None = None  # 0.0–1.0
    best_practices_score: float | None = None  # 0.0–1.0
    seo_score: float | None = None             # 0.0–1.0
    pwa_score: float | None = None             # 0.0–1.0
    error_message: str | None = None
    scanned_at: str | None = None


def _host_from_url(url: str) -> str:
    """Extract the hostname from a URL for circuit-breaker tracking."""
    try:
        hostname = urlparse(url).hostname
        return hostname or url
    except Exception:
        return url


def _parse_lighthouse_output(raw_json: str) -> Dict[str, float | None]:
    """Parse the Lighthouse JSON output and return category scores.

    Leading non-JSON content (e.g. Chrome DevTools protocol log lines) is
    stripped by scanning forward to the first ``{`` character before parsing.

    Args:
        raw_json: Raw output string from Lighthouse ``--output json``.

    Returns:
        Dictionary with keys ``performance``, ``accessibility``,
        ``best-practices``, ``seo``, ``pwa`` mapped to float scores
        (0.0–1.0) or ``None`` when the category was not run.

    Raises:
        ValueError: When the JSON cannot be parsed or has no categories.
    """
    # Skip any leading non-JSON content (Chrome DevTools noise, process logs).
    json_start = raw_json.find("{")
    if json_start == -1:
        raise ValueError(
            "Invalid JSON output from Lighthouse: no JSON object found in output"
        )
    if json_start > 0:
        raw_json = raw_json[json_start:]

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON output from Lighthouse: {exc}") from exc

    categories = data.get("categories")
    if not categories:
        raise ValueError("Lighthouse output contains no 'categories' key")

    def _score(key: str) -> float | None:
        cat = categories.get(key, {})
        return cat.get("score")

    return {
        "performance": _score("performance"),
        "accessibility": _score("accessibility"),
        "best-practices": _score("best-practices"),
        "seo": _score("seo"),
        "pwa": _score("pwa"),
    }


class LighthouseScanner:
    """
    Service that runs Google Lighthouse audits on government websites.

    Each URL is audited using the Lighthouse CLI in a subprocess.  The
    resulting JSON report is parsed and the five headline category scores
    are extracted:

    * **Performance** – page speed and user-experience metrics.
    * **Accessibility** – WCAG-aligned accessibility checks.
    * **Best Practices** – security and modern web best practices.
    * **SEO** – search-engine optimisation fundamentals.
    * **PWA** – Progressive Web App checks.

    All scores are returned on a 0.0–1.0 scale (multiply by 100 for
    the familiar 0–100 Lighthouse display value).
    """

    # Chrome flags required for headless operation in CI and sandboxed envs.
    _DEFAULT_CHROME_FLAGS = (
        "--headless "
        "--no-sandbox "
        "--disable-dev-shm-usage "
        "--disable-gpu"
    )

    def __init__(
        self,
        timeout_seconds: int = 120,
        lighthouse_path: str = "lighthouse",
        chrome_flags: str | None = None,
        extra_args: List[str] | None = None,
        only_categories: Sequence[str] | None = None,
        throttling_method: str | None = None,
        lighthouse_timeout_ms: int | None = 45000,
        max_retries: int = 2,
        retry_backoff_seconds: float = 2.0,
    ):
        """
        Args:
            timeout_seconds: Maximum wall-clock seconds to wait for a single
                Lighthouse run.  Lighthouse can be slow (30–90 s per URL).
            lighthouse_path: Path to the ``lighthouse`` binary.  Defaults to
                searching the system ``PATH``.
            chrome_flags: Chrome flags string passed to
                ``--chrome-flags``.  ``None`` uses the default headless flags.
            extra_args: Additional CLI arguments appended to every Lighthouse
                invocation (e.g. ``["--only-categories=accessibility"]``).
            only_categories: When provided, pass
                ``--only-categories=<comma-joined>`` to Lighthouse to skip
                unwanted audit categories and speed up each run.  Common
                value for government sites:
                ``["performance", "accessibility", "best-practices", "seo"]``.
            throttling_method: When provided, pass
                ``--throttling-method=<value>`` to Lighthouse.  Use
                ``"provided"`` to skip simulated slow-network throttling
                (appropriate for server-to-server audits).
            lighthouse_timeout_ms: When provided, pass
                ``--timeout=<value>`` (milliseconds) to Lighthouse so slow
                pages fail fast and free concurrency slots.
            max_retries: Maximum number of retry attempts for transient
                failures (timeout, non-zero exit, invalid JSON).  0 disables
                retries entirely.  Defaults to 2.
            retry_backoff_seconds: Base back-off duration in seconds between
                retry attempts.  Actual delay is
                ``min(2**(attempt-1) * retry_backoff_seconds, 30)``.
        """
        self.timeout_seconds = timeout_seconds
        self.lighthouse_path = lighthouse_path
        self.chrome_flags = chrome_flags if chrome_flags is not None else self._DEFAULT_CHROME_FLAGS
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

        # Build extra_args from explicit flags + caller-supplied list.
        built_extra: List[str] = list(extra_args or [])
        if only_categories:
            built_extra.append(f"--only-categories={','.join(only_categories)}")
        if throttling_method:
            built_extra.append(f"--throttling-method={throttling_method}")
        has_timeout_arg = any(arg.startswith("--timeout=") for arg in built_extra)
        if lighthouse_timeout_ms is not None and not has_timeout_arg:
            built_extra.append(f"--timeout={lighthouse_timeout_ms}")
        self.extra_args = built_extra

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_command(self, url: str) -> List[str]:
        """Return the subprocess command list for scanning *url*."""
        cmd = [
            self.lighthouse_path,
            url,
            "--output=json",
            "--output-path=stdout",
            "--quiet",
            f"--chrome-flags={self.chrome_flags}",
        ]
        cmd.extend(self.extra_args)
        return cmd

    def _run_lighthouse(self, url: str) -> str:
        """Run Lighthouse synchronously and return stdout.

        Raises:
            subprocess.TimeoutExpired: When the process exceeds *timeout_seconds*.
            subprocess.CalledProcessError: When Lighthouse exits non-zero.
                Always raised on non-zero exit codes, even when stdout is
                present — a non-zero exit indicates Lighthouse or Chrome
                encountered an error and any JSON in stdout may be truncated.
            FileNotFoundError: When the ``lighthouse`` binary is not found.
        """
        cmd = self._build_command(url)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        # Always raise on non-zero exit, even when stdout contains data.
        # A non-zero return code indicates Chrome/Lighthouse encountered an
        # error, and any JSON in stdout may be partial (truncated).
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )
        return result.stdout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def scan_url(self, url: str) -> LighthouseScanResult:
        """
        Run a Lighthouse audit on a single URL.

        The Lighthouse CLI is CPU-bound, so the subprocess is dispatched
        to a thread-pool executor so it does not block the event loop.

        Transient failures (timeout, non-zero exit, truncated JSON) are
        retried up to *max_retries* times with exponential back-off.

        Returns:
            LighthouseScanResult with category scores or an error message.
        """
        scanned_at = datetime.now(timezone.utc).isoformat()
        last_error: str | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                backoff = min(2 ** (attempt - 1) * self.retry_backoff_seconds, 30.0)
                await asyncio.sleep(backoff)

            try:
                loop = asyncio.get_running_loop()
                stdout = await loop.run_in_executor(None, self._run_lighthouse, url)
            except FileNotFoundError:
                return LighthouseScanResult(
                    url=url,
                    error_message=(
                        "Lighthouse CLI not found. "
                        "Install it with: npm install -g lighthouse"
                    ),
                    scanned_at=scanned_at,
                )
            except subprocess.TimeoutExpired:
                last_error = f"Lighthouse timed out after {self.timeout_seconds}s"
                continue  # retry
            except subprocess.CalledProcessError as exc:
                stderr_preview = (exc.stderr or "")[:200].strip()
                last_error = (
                    f"Lighthouse exited with code {exc.returncode}"
                    + (f": {stderr_preview}" if stderr_preview else "")
                )
                continue  # retry
            except Exception as exc:  # noqa: BLE001
                return LighthouseScanResult(
                    url=url,
                    error_message=f"Unexpected error: {exc}",
                    scanned_at=scanned_at,
                )

            try:
                scores = _parse_lighthouse_output(stdout)
            except ValueError as exc:
                last_error = str(exc)
                continue  # retry — truncated/corrupt JSON may be transient

            return LighthouseScanResult(
                url=url,
                performance_score=scores["performance"],
                accessibility_score=scores["accessibility"],
                best_practices_score=scores["best-practices"],
                seo_score=scores["seo"],
                pwa_score=scores["pwa"],
                scanned_at=scanned_at,
            )

        # All attempts exhausted.
        return LighthouseScanResult(
            url=url,
            error_message=last_error,
            scanned_at=scanned_at,
        )

    async def scan_urls_batch(
        self,
        urls: List[str],
        rate_limit_per_second: float = 0.2,
        max_runtime_seconds: Optional[float] = None,
        start_time: Optional[float] = None,
        on_result: Optional[Callable[["LighthouseScanResult"], None]] = None,
        concurrency: int = 1,
        circuit_breaker_threshold: int = 3,
    ) -> Dict[str, "LighthouseScanResult"]:
        """
        Run Lighthouse audits for multiple URLs with rate limiting and
        optional concurrency.

        Lighthouse is slow (30–90 s per URL), so the default rate limit is
        0.2 req/s (one request every 5 seconds) to avoid overloading
        government servers.  Setting *concurrency* > 1 allows multiple
        Lighthouse processes to run simultaneously, which can significantly
        improve throughput when the bottleneck is network I/O rather than CPU.

        A per-host **circuit breaker** skips further URLs for any hostname
        that accumulates *circuit_breaker_threshold* consecutive failures,
        preventing a single unresponsive domain from exhausting the run budget.

        After the submission loop, in-flight tasks are drained with a
        deadline equal to ``timeout_seconds + 30`` seconds so that the
        scanner exits cleanly even if the runner receives an external shutdown
        signal.

        Args:
            urls: List of URLs to audit.
            rate_limit_per_second: Minimum gap between *starting* new
                Lighthouse processes.  With concurrency > 1 this controls
                how quickly new processes are submitted, not how quickly they
                complete.
            max_runtime_seconds: Stop scanning early when this many seconds
                have elapsed since *start_time*, leaving a 60-second safety
                buffer.  ``None`` means no limit.
            start_time: ``time.monotonic()`` value recorded at the start of
                the overall job.  ``None`` uses the first call to this method.
            on_result: Optional callback invoked immediately after each URL
                is scanned.  Useful for incremental persistence so that
                partial results survive a timeout.
            concurrency: Maximum number of Lighthouse processes to run in
                parallel.  Defaults to 1 (sequential).  Values > 1 increase
                throughput but consume more CPU and memory.
            circuit_breaker_threshold: Number of consecutive failures on a
                single hostname before further URLs from that host are skipped.
                Defaults to 3.  Set to 0 to disable the circuit breaker.

        Returns:
            Dictionary mapping URL to LighthouseScanResult.  When stopped
            early the dict contains only the URLs that were actually scanned
            or circuit-breaker-skipped.
        """
        results: Dict[str, LighthouseScanResult] = {}
        delay = 1.0 / rate_limit_per_second if rate_limit_per_second > 0 else 0
        # Cap delay at 120 seconds to prevent accidental freezes.
        delay = min(delay, 120.0)

        _start = start_time if start_time is not None else time.monotonic()
        _safety_buffer = 60.0
        max_concurrency = max(1, concurrency)
        semaphore = asyncio.Semaphore(max_concurrency)

        total = len(urls)
        # Per-host consecutive failure counts for the circuit breaker.
        host_failure_counts: dict[str, int] = {}
        _heartbeat_every = 10  # emit a progress line every N completed scans
        _completed_count = 0

        async def _scan_one_url(idx: int, url: str) -> None:
            nonlocal _completed_count
            host = _host_from_url(url)

            # Circuit breaker: skip without consuming a concurrency slot.
            if circuit_breaker_threshold > 0 and host_failure_counts.get(host, 0) >= circuit_breaker_threshold:
                streak = host_failure_counts[host]
                print(
                    f"  [{idx}/{total}] ⚡ Circuit breaker: "
                    f"skipping {url} ({streak} consecutive failures on {host})"
                )
                skip_result = LighthouseScanResult(
                    url=url,
                    error_message=(
                        f"Circuit breaker: {streak} consecutive failures on {host}"
                    ),
                    scanned_at=datetime.now(timezone.utc).isoformat(),
                )
                results[url] = skip_result
                if on_result is not None:
                    on_result(skip_result)
                _completed_count += 1
                return

            async with semaphore:
                print(f"  [{idx}/{total}] Scanning: {url}")
                result = await self.scan_url(url)
                results[url] = result

                if on_result is not None:
                    on_result(result)

                # Update circuit breaker state.
                if result.error_message:
                    host_failure_counts[host] = host_failure_counts.get(host, 0) + 1
                    print(f"      ✗ {result.error_message}")
                else:
                    host_failure_counts[host] = 0  # reset streak on success
                    perf = (
                        f"{result.performance_score * 100:.0f}"
                        if result.performance_score is not None
                        else "—"
                    )
                    a11y = (
                        f"{result.accessibility_score * 100:.0f}"
                        if result.accessibility_score is not None
                        else "—"
                    )
                    print(f"      ✓ perf={perf} a11y={a11y}")

                _completed_count += 1
                if _heartbeat_every > 0 and _completed_count % _heartbeat_every == 0:
                    elapsed_h = time.monotonic() - _start
                    success_h = sum(1 for r in results.values() if not r.error_message)
                    errors_h = len(results) - success_h
                    budget_info = (
                        f", {(max_runtime_seconds - elapsed_h) / 60:.1f}m remaining"
                        if max_runtime_seconds is not None
                        else ""
                    )
                    print(
                        f"  📊 Progress: {_completed_count}/{total} scanned "
                        f"({success_h} ok, {errors_h} failed, "
                        f"{elapsed_h / 60:.1f}m elapsed{budget_info})"
                    )

        running_tasks: set[asyncio.Task[None]] = set()
        submitted_count = 0
        for idx, url in enumerate(urls, 1):
            if max_runtime_seconds is not None:
                elapsed = time.monotonic() - _start
                remaining = max_runtime_seconds - elapsed
                if remaining < _safety_buffer:
                    print(
                        f"  ⏱️  Time budget near limit "
                        f"({elapsed / 60:.1f}m elapsed, "
                        f"{remaining / 60:.1f}m remaining) "
                        f"— stopping after submitting {submitted_count}/{total} URLs"
                    )
                    break

            while len(running_tasks) >= max_concurrency:
                done, pending = await asyncio.wait(
                    running_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                running_tasks = pending
                for done_task in done:
                    if done_task.cancelled():
                        continue
                    exc = done_task.exception()
                    if exc is not None:
                        print(f"      ✗ Unexpected task error: {exc}")

            running_tasks.add(asyncio.create_task(_scan_one_url(idx, url)))
            submitted_count += 1

            if delay > 0:
                await asyncio.sleep(delay)

        # Drain remaining in-flight tasks with a deadline so that an external
        # runner shutdown does not leave orphan Chrome processes indefinitely.
        if running_tasks:
            drain_deadline = float(self.timeout_seconds) + 30.0
            done, pending = await asyncio.wait(running_tasks, timeout=drain_deadline)
            for task in pending:
                task.cancel()
                print(
                    f"      ⚠️  Cancelled in-flight task "
                    f"(drain deadline {drain_deadline:.0f}s exceeded)"
                )
            for done_task in done:
                if done_task.cancelled():
                    continue
                exc = done_task.exception()
                if exc is not None:
                    print(f"      ✗ Unexpected task error: {exc}")

        return results
