"""Unit tests for Playwright fallback behavior and fixture gating."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import scrapers.playwright_fallback as pw_module
from scrapers.base_scraper import RequestSpec, ScrapeJob


@pytest.fixture
def sample_job() -> ScrapeJob:
    return ScrapeJob(
        source="indigo",
        origin="DEL",
        destination="BOM",
        depart_date=date(2026, 10, 13),
        lead_time=7,
        scrape_date=date(2026, 10, 6),
    )


@pytest.fixture
def mock_scraper():
    scraper = MagicMock()
    scraper.source = "indigo"
    scraper.build_request.return_value = RequestSpec(
        url="https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search",
        method="POST",
        headers={"origin": "https://www.goindigo.in", "user_key": "test_key"},
        json_body={"codes": {"currency": "INR"}},
    )
    scraper.parse_ok.return_value = True
    return scraper


def test_missing_dependencies_returns_failure_by_default(sample_job, mock_scraper):
    """By default (in production), uninstalled Playwright returns ok=False, not fixture data."""
    with (
        patch.dict("sys.modules", {"playwright.async_api": None}),
        patch.object(pw_module, "ALLOW_FIXTURE_FALLBACK", False),
    ):
        result = asyncio.run(pw_module.fetch_with_browser(sample_job, mock_scraper))
        assert result.ok is False
        assert "Playwright not installed" in (result.error or "")
        assert result.payload is None


def test_missing_dependencies_with_fixture_gate_enabled(sample_job, mock_scraper):
    """When explicit test gate is enabled, fixture fallback is allowed."""
    with (
        patch.dict("sys.modules", {"playwright.async_api": None}),
        patch.object(pw_module, "ALLOW_FIXTURE_FALLBACK", True),
    ):
        result = asyncio.run(pw_module.fetch_with_browser(sample_job, mock_scraper))
        assert result.ok is True
        assert result.payload is not None
        assert result.method == "playwright"


def test_browser_timeout_returns_failure_without_fixtures(sample_job, mock_scraper):
    """When no response is captured, return ok=False instead of fabricating fixture data."""
    mock_pw = MagicMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    # page.on() is synchronous in Playwright — must not be an AsyncMock
    mock_page.on = MagicMock()

    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_page.evaluate = AsyncMock(return_value=None)
    mock_page.request = AsyncMock()
    mock_api_resp = AsyncMock()
    mock_api_resp.ok = False
    mock_page.request.fetch = AsyncMock(return_value=mock_api_resp)

    import contextlib

    @contextlib.asynccontextmanager
    async def _mock_async_playwright():
        yield mock_pw

    with (
        patch("playwright.async_api.async_playwright", side_effect=_mock_async_playwright),
        patch.object(pw_module, "ALLOW_FIXTURE_FALLBACK", False),
        patch("asyncio.wait_for", side_effect=TimeoutError),
    ):
        result = asyncio.run(pw_module.fetch_with_browser(sample_job, mock_scraper))

    assert result.ok is False
    assert "no fare response intercepted" in (result.error or "").lower()
    assert result.payload is None


def test_browser_post_spec_captured_returns_success(sample_job, mock_scraper):
    """When browser navigation captures valid fare JSON, return ok=True."""
    import contextlib

    mock_pw = MagicMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    # page.on() is synchronous in Playwright — must not be an AsyncMock
    mock_page.on = MagicMock()
    mock_page.goto = AsyncMock()  # Mock goto to complete without raising

    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)

    # Mock page.goto for navigation-based search
    mock_page.goto = AsyncMock()
    mock_page.title = AsyncMock(return_value="Google Flights")
    mock_page.content = AsyncMock(return_value="<html></html>")
    mock_page.screenshot = AsyncMock()

    fake_fares = [{"flight_no": "6E-101", "total_fare": 4500.0}]

    # Mock the API response from page.request.fetch()
    mock_api_resp = AsyncMock()
    mock_api_resp.ok = True
    mock_api_resp.json = AsyncMock(return_value=fake_fares)

    mock_page.request = AsyncMock()
    mock_page.request.fetch = AsyncMock(return_value=mock_api_resp)

    @contextlib.asynccontextmanager
    async def _mock_async_playwright():
        yield mock_pw

    # The response handler captures data from page.on("response", ...) callbacks.
    # We need to simulate a response that parse_ok accepts.
    captured_responses = []

    def capture_response(event_name, handler):
        # Store the handler so we can call it to simulate a response
        if event_name == "response":
            captured_responses.append(handler)

    mock_page.on = MagicMock(side_effect=capture_response)

    with (
        patch("playwright.async_api.async_playwright", side_effect=_mock_async_playwright),
        patch.object(pw_module, "ALLOW_FIXTURE_FALLBACK", False),
    ):
        # Run the fetch — the response handler will capture data from page.evaluate
        result = asyncio.run(pw_module.fetch_with_browser(sample_job, mock_scraper))

    # The page.evaluate call returns fake_fares which parse_ok accepts
    assert result.ok is True
    assert result.method == "playwright"
    assert result.status_code == 200
