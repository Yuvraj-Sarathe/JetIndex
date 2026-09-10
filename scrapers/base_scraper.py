"""Abstract base scraper and dataclasses for scrape jobs/results."""

from __future__ import annotations

import random
import time
import urllib.parse
import urllib.robotparser
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
# Ethical scraping infrastructure (ported from VayuSutra-V4)
# ---------------------------------------------------------------------------


class EthicalRateLimiter:
    """Token-bucket rate limiter with jitter to prevent server pulse spikes.

    Unlike a simple ``time.sleep(1/rps)`` loop, the token-bucket algorithm
    allows short bursts (up to ``burst_capacity``) while maintaining a
    long-term average of ``rate_limit_rps`` requests per second.  After
    consuming a token, a random jitter (default 50-180 ms) is injected so
    that concurrent workers don't hammer the server at exactly the same
    instant.
    """

    def __init__(
        self,
        rate_limit_rps: float = 1.5,
        burst_capacity: float = 2.0,
        min_jitter_sec: float = 0.05,
        max_jitter_sec: float = 0.18,
    ):
        self.rate = float(rate_limit_rps)
        self.capacity = float(burst_capacity)
        self.tokens = float(burst_capacity)
        self.last_refill = time.monotonic()
        self.min_jitter = min_jitter_sec
        self.max_jitter = max_jitter_sec

    def _refill(self) -> None:
        """Add tokens based on elapsed monotonic time."""
        now = time.monotonic()
        if not isinstance(now, (int, float)):
            return
        if not isinstance(self.last_refill, (int, float)):
            self.last_refill = now
            return
        elapsed = now - self.last_refill
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

    def acquire(self, tokens_requested: float = 1.0) -> float:
        """Block until enough tokens are available, then inject jitter.

        Returns the total sleep duration in seconds.
        """
        total_slept = 0.0
        while True:
            self._refill()
            if not isinstance(self.tokens, (int, float)) or self.tokens >= tokens_requested:
                if isinstance(self.tokens, (int, float)):
                    self.tokens -= tokens_requested
                break
            needed = tokens_requested - self.tokens
            wait_time = needed / self.rate
            time.sleep(wait_time)
            total_slept += wait_time

        jitter = random.uniform(self.min_jitter, self.max_jitter)
        time.sleep(jitter)
        total_slept += jitter
        return total_slept

    def get_token_count(self) -> float:
        """Inspect current available tokens."""
        self._refill()
        return self.tokens


class RobotsChecker:
    """Automatic robots.txt parsing, caching, and compliance validator.

    Fetches ``robots.txt`` once per domain, caches it for 24 hours, and
    checks ``can_fetch()`` before every request.  If the file is
    unreachable the checker defaults to permissive (standard convention).
    """

    def __init__(self, cache_ttl_sec: int = 86400):
        self.cache_ttl = cache_ttl_sec
        self._parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._cache_timestamps: dict[str, float] = {}

    def is_allowed(
        self,
        target_url: str,
        user_agent: str = "JetIndex-Bot/1.0 (+https://github.com/Yuvraj-Sarathe/JetIndex)",
    ) -> bool:
        """Check if scraping *target_url* is permitted under the domain robots.txt."""
        parsed = urllib.parse.urlparse(target_url)
        domain = parsed.netloc
        now = time.time()
        is_expired = False
        if isinstance(now, (int, float)):
            last_ts = self._cache_timestamps.get(domain, 0)
            if isinstance(last_ts, (int, float)) and (now - last_ts) > self.cache_ttl:
                is_expired = True

        if domain not in self._parsers or is_expired:
            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            try:
                import httpx as _httpx

                resp = _httpx.get(
                    robots_url,
                    headers={"User-Agent": user_agent},
                    timeout=4.0,
                )
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.allow_all = True
            except Exception as exc:
                logger.debug(
                    "Failed to fetch robots.txt for {}: {}. Defaulting to permissive.",
                    domain,
                    exc,
                )
                rp.allow_all = True

            self._parsers[domain] = rp
            self._cache_timestamps[domain] = now

        return self._parsers[domain].can_fetch(user_agent, target_url)


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
        self.limiter = EthicalRateLimiter(
            rate_limit_rps=self.rate_limit_rps,
            min_jitter_sec=1.0,
            max_jitter_sec=4.0,
        )
        self.robots = RobotsChecker()

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

            # Ethical: check robots.txt before requesting
            if not self.robots.is_allowed(spec.url, profile_info["headers"].get("User-Agent", "")):
                logger.debug("robots.txt disallows {}, skipping", spec.url)
                # Return a synthetic 403-like response to trigger fallback logic
                # We can't easily fake a Response, so raise to skip
                raise RetryableStatusError(403, "Blocked by robots.txt")

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

            # Token-bucket rate limiting with ethical jitter
            self.limiter.acquire()

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
