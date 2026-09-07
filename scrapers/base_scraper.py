"""Abstract base scraper and dataclasses for scrape jobs/results."""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Literal

import yaml
from curl_cffi import requests as cffi_requests
from loguru import logger
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# NOTE: scrapers.fingerprints.get_random_profile and scrapers.storage.save_raw
# are imported lazily inside fetch() to avoid circular imports
# (storage.py imports ScrapeResult from this module).


# ---------------------------------------------------------------------------
# Custom exception used to signal tenacity that a retry is needed.
# ---------------------------------------------------------------------------
class RetryableStatusError(Exception):
    """Raised when the HTTP response has a retryable status code."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(message or f"Retryable HTTP {status_code}")


# ---------------------------------------------------------------------------
# Dataclasses — DO NOT MODIFY
# ---------------------------------------------------------------------------


@dataclass
class ScrapeJob:
    """Describes a single scrape task: source × route × lead time."""

    source: str
    origin: str
    destination: str
    depart_date: date
    lead_time: int
    scrape_date: date


@dataclass
class ScrapeResult:
    """Outcome of a single scrape attempt."""

    job: ScrapeJob
    ok: bool
    status_code: int | None = None
    payload: dict | list | None = None
    error: str | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    method: Literal["curl_cffi", "playwright"] = "curl_cffi"
    proxy_used: str | None = None
    raw_path: str | None = None


@dataclass
class RequestSpec:
    """Specification for an HTTP request to be made by the scraper."""

    url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    params: dict[str, str] | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_source_config(source: str) -> dict:
    """Load config/sources.yaml and return the section for *source*."""
    try:
        with open("config/sources.yaml") as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("sources", {}).get(source, {})
    except (OSError, yaml.YAMLError):
        return {}


def _is_retryable(status_code: int) -> bool:
    """Return True for status codes that should trigger a retry."""
    return status_code in (401, 403, 429) or status_code >= 500


# ---------------------------------------------------------------------------
# BaseScraper
# ---------------------------------------------------------------------------


class BaseScraper(ABC):
    """Abstract base class for all scrapers.

    Subclasses implement build_request() and parse_ok().
    The base class implements the fetch loop with retries and Playwright fallback.
    """

    source: str
    rate_limit_rps: float = 0.33  # 1 request per 3 seconds

    def __init__(self, proxy_manager=None, session_manager=None):
        self.proxy_manager = proxy_manager
        self.session_manager = session_manager

    @abstractmethod
    def build_request(self, job: ScrapeJob) -> RequestSpec:
        """Build the HTTP request for a given scrape job."""
        raise NotImplementedError(f"Owner: {self.source}")

    @abstractmethod
    def parse_ok(self, response: Any) -> bool:
        """Check if the response contains valid fare data."""
        raise NotImplementedError(f"Owner: {self.source}")

    # ------------------------------------------------------------------
    # Core fetch loop
    # ------------------------------------------------------------------

    def fetch(self, job: ScrapeJob) -> ScrapeResult:
        """
        Execute the full fetch loop:
        1. Build request via subclass
        2. Attempt with curl_cffi (TLS impersonation)
        3. Retry on 403/429/5xx with new proxy (tenacity backoff, max 4)
        4. Fallback to Playwright stealth browser if configured
        5. Save raw payload via storage.save_raw()
        """
        # Lazy imports to avoid circular dependency (storage → base_scraper)
        from scrapers.fingerprints import get_random_profile
        from scrapers.storage import save_raw

        spec = self.build_request(job)

        # Merge session cookies/headers into the request spec
        if self.session_manager is not None:
            session_data = self.session_manager.get_or_refresh(self.source)
            if session_data:
                spec.headers.update(session_data.get("headers", {}))
                # Cookies are forwarded as a Cookie header value
                if session_data.get("cookies"):
                    cookie_str = "; ".join(f"{k}={v}" for k, v in session_data["cookies"].items())
                    spec.headers["Cookie"] = cookie_str

        # Mutable state shared across retry attempts
        current_proxy: list[str | None] = [self.proxy_manager.get() if self.proxy_manager else None]
        current_profile: list[dict] = [get_random_profile()]

        source_cfg = _load_source_config(self.source)
        max_retries = source_cfg.get("max_retries", 4)

        # ---- inner helper decorated with tenacity ----
        @retry(
            retry=retry_if_exception_type(RetryableStatusError),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            stop=stop_after_attempt(max_retries),
            reraise=True,
        )
        def _attempt() -> cffi_requests.Response:
            profile_info = current_profile[0]
            proxy = current_proxy[0]

            merged_headers = {**profile_info["headers"], **spec.headers}

            proxy_dict = {"https": proxy, "http": proxy} if proxy else None

            sess = cffi_requests.Session(impersonate=profile_info["impersonate"])
            try:
                if spec.method.upper() == "POST":
                    resp = sess.post(
                        spec.url,
                        headers=merged_headers,
                        json=spec.json_body,
                        params=spec.params,
                        proxies=proxy_dict,
                        timeout=30,
                    )
                else:
                    resp = sess.get(
                        spec.url,
                        headers=merged_headers,
                        params=spec.params,
                        proxies=proxy_dict,
                        timeout=30,
                    )
            finally:
                sess.close()

            # Rate-limiting jitter after each request
            time.sleep(random.uniform(1.0, 4.0))

            if _is_retryable(resp.status_code):
                # Mark the proxy as bad on 403/429
                if proxy and self.proxy_manager and resp.status_code in (403, 429):
                    self.proxy_manager.mark_bad(proxy)

                # Rotate proxy and fingerprint for the next attempt
                current_proxy[0] = self.proxy_manager.get() if self.proxy_manager else None
                current_profile[0] = get_random_profile()

                raise RetryableStatusError(resp.status_code)

            return resp

        # ---- execute ----
        try:
            resp = _attempt()
            payload = resp.json() if resp.content else None
            is_ok = (resp.status_code == 200) and self.parse_ok(resp)
            if not is_ok:
                # Intentional: triggers Playwright fallback, not curl_cffi retry
                raise RetryableStatusError(resp.status_code)

            result = ScrapeResult(
                job=job,
                ok=True,
                status_code=resp.status_code,
                payload=payload,
                method="curl_cffi",
                proxy_used=current_proxy[0],
            )

        except (RetryError, RetryableStatusError):
            # All curl_cffi retries exhausted — try Playwright fallback
            use_pw = source_cfg.get("use_playwright_fallback", False)
            if use_pw:
                logger.info(
                    "curl_cffi retries exhausted for {} {}-{}; falling back to Playwright",
                    self.source,
                    job.origin,
                    job.destination,
                )
                import asyncio

                from scrapers.playwright_fallback import fetch_with_browser

                try:
                    result = asyncio.run(fetch_with_browser(job, self))
                except Exception as pw_err:
                    logger.error("Playwright fallback also failed: {}", pw_err)
                    result = ScrapeResult(
                        job=job,
                        ok=False,
                        error=f"All retries + Playwright failed: {pw_err}",
                        method="playwright",
                    )
            else:
                result = ScrapeResult(
                    job=job,
                    ok=False,
                    error="All curl_cffi retries exhausted (Playwright fallback disabled)",
                    method="curl_cffi",
                )

        except Exception as exc:
            logger.error("Unexpected error fetching {}: {}", job.source, exc)
            result = ScrapeResult(
                job=job,
                ok=False,
                error=str(exc),
                method="curl_cffi",
            )

        # Persist successful payloads
        if result.ok and result.payload is not None:
            try:
                save_raw(result)
            except Exception as storage_err:
                logger.warning("save_raw failed (non-fatal): {}", storage_err)

        return result

    def run_jobs(self, jobs: list[ScrapeJob]) -> list[ScrapeResult]:
        """Execute multiple scrape jobs sequentially."""
        results = []
        for job in jobs:
            try:
                result = self.fetch(job)
                results.append(result)
            except Exception as e:
                results.append(
                    ScrapeResult(
                        job=job,
                        ok=False,
                        error=str(e),
                    )
                )
        return results
