"""Tests for BaseScraper.fetch() — the core fetch loop engine.

All network calls are mocked.  No real HTTP requests are made.
"""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.base_scraper import (
    BaseScraper,
    RequestSpec,
    ScrapeJob,
    ScrapeResult,
)

# ---------------------------------------------------------------------------
# Stub scraper with deterministic build_request / parse_ok
# ---------------------------------------------------------------------------


class _StubScraper(BaseScraper):
    """Concrete scraper used only in tests."""

    source = "stub"

    def build_request(self, job: ScrapeJob) -> RequestSpec:
        return RequestSpec(
            url="https://example.com/api/fares",
            method="POST",
            headers={"X-Custom": "1"},
            json_body={"origin": job.origin, "destination": job.destination},
        )

    def parse_ok(self, response) -> bool:
        return True


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_job():
    return ScrapeJob(
        source="stub",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 20),
        lead_time=7,
        scrape_date=date(2026, 10, 13),
    )


def _fake_response(status_code: int = 200, body: dict | None = None):
    """Return a mock that quacks like a curl_cffi Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = json.dumps(body or {"fares": []}).encode()
    resp.json.return_value = body or {"fares": []}
    return resp


# Mock targets — since fetch() uses lazy imports, we patch at the *source*
# module rather than at scrapers.base_scraper.
_FP_TARGET = "scrapers.fingerprints.get_random_profile"
_SAVE_TARGET = "scrapers.storage.save_raw"
_CFG_TARGET = "scrapers.base_scraper._load_source_config"
_CFFI_TARGET = "scrapers.base_scraper.cffi_requests"
_TIME_TARGET = "scrapers.base_scraper.time"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@patch(_SAVE_TARGET)
@patch(
    _FP_TARGET,
    return_value={
        "impersonate": "chrome120",
        "headers": {"User-Agent": "TestAgent"},
    },
)
@patch(
    _CFG_TARGET,
    return_value={
        "max_retries": 4,
        "use_playwright_fallback": True,
    },
)
@patch(_TIME_TARGET)
@patch(_CFFI_TARGET)
class TestFetchSuccess:
    """Successful fetch — 200 OK on first attempt."""

    def test_returns_ok_result(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(200, {"fares": [1, 2]})
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()
        result = scraper.fetch(sample_job)

        assert result.ok is True
        assert result.status_code == 200
        assert result.payload == {"fares": [1, 2]}
        assert result.method == "curl_cffi"

    def test_calls_save_raw(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(200, {"fares": []})
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()
        scraper.fetch(sample_job)

        mock_save.assert_called_once()


@patch(_SAVE_TARGET)
@patch(
    _FP_TARGET,
    return_value={
        "impersonate": "chrome120",
        "headers": {"User-Agent": "TestAgent"},
    },
)
@patch(
    _CFG_TARGET,
    return_value={
        "max_retries": 2,
        "use_playwright_fallback": False,
    },
)
@patch(_TIME_TARGET)
@patch(_CFFI_TARGET)
class TestFetchRetries:
    """Retry behaviour on 403 / 429 / 5xx."""

    def test_403_triggers_retry_and_mark_bad(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        # First call 403, second call 200
        mock_session.post.side_effect = [
            _fake_response(403),
            _fake_response(200, {"ok": True}),
        ]
        mock_cffi.Session.return_value = mock_session

        pm = MagicMock()
        pm.get.return_value = "http://proxy1:8080"

        scraper = _StubScraper(proxy_manager=pm)
        result = scraper.fetch(sample_job)

        assert result.ok is True
        pm.mark_bad.assert_called_once_with("http://proxy1:8080")

    def test_429_triggers_retry(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.side_effect = [
            _fake_response(429),
            _fake_response(200, {"ok": True}),
        ]
        mock_cffi.Session.return_value = mock_session

        pm = MagicMock()
        pm.get.return_value = "http://proxy1:8080"

        scraper = _StubScraper(proxy_manager=pm)
        result = scraper.fetch(sample_job)

        assert result.ok is True

    def test_500_triggers_retry(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.side_effect = [
            _fake_response(500),
            _fake_response(200, {"ok": True}),
        ]
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()
        result = scraper.fetch(sample_job)

        assert result.ok is True

    def test_max_retries_exhausted_returns_failure(
        self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job
    ):
        """All attempts return 403 → result.ok should be False."""
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(403)
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()
        result = scraper.fetch(sample_job)

        assert result.ok is False
        assert "retries exhausted" in (result.error or "").lower()


@patch(_SAVE_TARGET)
@patch(
    _FP_TARGET,
    return_value={
        "impersonate": "chrome120",
        "headers": {"User-Agent": "TestAgent"},
    },
)
@patch(
    _CFG_TARGET,
    return_value={
        "max_retries": 1,
        "use_playwright_fallback": True,
    },
)
@patch(_TIME_TARGET)
@patch(_CFFI_TARGET)
class TestPlaywrightFallback:
    """Playwright fallback is invoked when all curl_cffi retries fail."""

    @patch("scrapers.playwright_fallback.fetch_with_browser", new_callable=AsyncMock)
    def test_playwright_called_on_exhaustion(
        self, mock_pw, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job
    ):
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(403)
        mock_cffi.Session.return_value = mock_session

        pw_result = ScrapeResult(job=sample_job, ok=True, status_code=200, payload={"pw": True}, method="playwright")
        mock_pw.return_value = pw_result

        scraper = _StubScraper()
        result = scraper.fetch(sample_job)

        assert result.ok is True
        assert result.method == "playwright"


@patch(_SAVE_TARGET)
@patch(
    _FP_TARGET,
    return_value={
        "impersonate": "chrome120",
        "headers": {"User-Agent": "TestAgent"},
    },
)
@patch(
    _CFG_TARGET,
    return_value={
        "max_retries": 4,
        "use_playwright_fallback": False,
    },
)
@patch(_CFFI_TARGET)
class TestRateLimiting:
    """Rate limiting jitter: time.sleep called with 1–4 s."""

    @patch(_TIME_TARGET)
    def test_sleep_called_after_request(self, mock_time, mock_cffi, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(200)
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()
        scraper.fetch(sample_job)

        mock_time.sleep.assert_called_once()
        delay = mock_time.sleep.call_args[0][0]
        assert 1.0 <= delay <= 4.0


class TestFetchNoProxy:
    """When no proxy_manager is passed, fetch uses direct connection."""

    @patch(_SAVE_TARGET)
    @patch(
        _FP_TARGET,
        return_value={
            "impersonate": "chrome120",
            "headers": {"User-Agent": "TestAgent"},
        },
    )
    @patch(
        _CFG_TARGET,
        return_value={
            "max_retries": 4,
            "use_playwright_fallback": False,
        },
    )
    @patch(_TIME_TARGET)
    @patch(_CFFI_TARGET)
    def test_no_proxy_dict_passed(self, mock_cffi, mock_time, mock_cfg, mock_fp, mock_save, sample_job):
        mock_session = MagicMock()
        mock_session.post.return_value = _fake_response(200)
        mock_cffi.Session.return_value = mock_session

        scraper = _StubScraper()  # no proxy_manager
        scraper.fetch(sample_job)

        # proxies kwarg should be None (direct connection)
        call_kwargs = mock_session.post.call_args
        assert call_kwargs.kwargs.get("proxies") is None or call_kwargs[1].get("proxies") is None
