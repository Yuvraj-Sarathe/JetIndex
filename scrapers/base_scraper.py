"""Abstract base scraper and dataclasses for scrape jobs/results."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Literal


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
    fetched_at: datetime = field(default_factory=datetime.utcnow)
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

    def fetch(self, job: ScrapeJob) -> ScrapeResult:
        """
        Execute the full fetch loop:
        1. Build request
        2. Attempt with curl_cffi (TLS impersonation)
        3. Retry on 403/429/5xx with new proxy (tenacity backoff, max 4)
        4. Fallback to Playwright stealth browser
        5. Save raw payload via storage.save_raw()
        """
        # TODO: Implement full fetch loop when scrapers are ready
        # from scrapers.storage import save_raw
        # from scrapers.fingerprints import get_random_profile
        # from scrapers.playwright_fallback import fetch_with_browser
        raise NotImplementedError(f"Owner: Sourabh/Abhay — {self.source}")

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
