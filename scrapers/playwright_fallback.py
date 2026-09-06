"""Playwright stealth browser fallback for anti-bot protected sites."""

from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime

from loguru import logger

from scrapers.base_scraper import ScrapeJob, ScrapeResult


async def fetch_with_browser(job: ScrapeJob, scraper_instance) -> ScrapeResult:
    """
    Fallback fetch using Playwright with stealth mode.

    Strategy:
    1. Launch headless Chromium with playwright-stealth
    2. Intercept XHR responses (don't scrape DOM)
    3. Return the intercepted fare data

    This is triggered only after curl_cffi retries fail.
    """
    logger.info(f"Playwright fallback triggered for {job.source} {job.origin}-{job.destination} T+{job.lead_time}")

    try:
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async
    except ImportError as exc:
        logger.error(f"Playwright dependencies not installed: {exc}")
        return ScrapeResult(
            job=job,
            ok=False,
            error=f"Playwright not installed: {exc}",
            method="playwright",
        )

    # Build the request spec so we know what URL / endpoint to target
    try:
        spec = scraper_instance.build_request(job)
    except NotImplementedError:
        return ScrapeResult(
            job=job,
            ok=False,
            error="build_request() not implemented for this source",
            method="playwright",
        )

    # Container for the intercepted fare response payload
    captured_payload: list[dict | list] = []
    capture_event = asyncio.Event()

    async def _handle_response(response) -> None:
        """Capture JSON responses whose URL overlaps with the target endpoint."""
        try:
            # Match if the response URL contains the path portion of the spec URL
            # (e.g. "/api/fares" inside "https://www.example.com/api/fares?q=1")
            if spec.url and spec.url.split("?")[0] in response.url:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    body = await response.json()
                    captured_payload.append(body)
                    capture_event.set()
        except Exception:
            # Non-JSON or unreadable responses are silently ignored
            pass

    browser = None
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()
            await stealth_async(page)

            # Register XHR/fetch response interceptor
            page.on("response", _handle_response)

            # Navigate to the target URL
            logger.debug(f"Playwright navigating to {spec.url}")
            await page.goto(spec.url, wait_until="domcontentloaded", timeout=30_000)

            # Wait for the intercepted fare response (max 30s)
            try:
                await asyncio.wait_for(capture_event.wait(), timeout=30.0)
            except TimeoutError:
                logger.warning("Playwright: timed out waiting for fare response")

            await browser.close()
            browser = None  # avoid double-close in finally

        if captured_payload:
            # Use the first captured payload
            payload = captured_payload[0]
            logger.info(f"Playwright captured fare data for {job.source}")
            return ScrapeResult(
                job=job,
                ok=True,
                status_code=200,
                payload=payload,
                method="playwright",
                fetched_at=datetime.utcnow(),
            )

        return ScrapeResult(
            job=job,
            ok=False,
            error="Playwright: no fare response intercepted within timeout",
            method="playwright",
        )

    except Exception as exc:
        logger.error(f"Playwright fallback error: {exc}")
        return ScrapeResult(
            job=job,
            ok=False,
            error=f"Playwright error: {exc}",
            method="playwright",
        )
    finally:
        if browser:
            with contextlib.suppress(Exception):
                await browser.close()
