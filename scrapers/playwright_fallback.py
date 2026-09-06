"""Playwright stealth browser fallback for anti-bot protected sites."""

from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from scrapers.base_scraper import ScrapeJob, ScrapeResult

# Test-only gate: fixtures must NOT be used as silent fallback in production
ALLOW_FIXTURE_FALLBACK = os.getenv("JETINDEX_ALLOW_FIXTURE_FALLBACK", "").strip().lower() in ("1", "true", "yes")


def _build_fixture_fallback_result(job: ScrapeJob, scraper_instance) -> ScrapeResult:
    """Build a ScrapeResult using route-specific fixtures (TEST/DEBUG ONLY)."""
    fixture_map = {
        "indigo": Path("tests/fixtures/indigo_sample.json"),
        "makemytrip": Path("tests/fixtures/makemytrip_sample.json"),
    }
    fixture_path = fixture_map.get(job.source)
    if fixture_path and fixture_path.exists():
        try:
            with open(fixture_path) as f:
                raw = json.load(f)

            if job.source == "indigo" and isinstance(raw, list):
                adapted = copy.deepcopy(raw)
                for item in adapted:
                    item["source"] = job.source
                    item["route_code"] = f"{job.origin}-{job.destination}"
                    item["origin"] = job.origin
                    item["destination"] = job.destination
                    item["depart_date"] = job.depart_date.isoformat()
                    item["scrape_date"] = job.scrape_date.isoformat()
                    item["lead_time"] = job.lead_time
                    item["scraped_at"] = datetime.now(UTC).isoformat()
                if scraper_instance.parse_ok(adapted):
                    logger.info(f"Using route-adapted test fixture for {job.source} {job.origin}-{job.destination}")
                    return ScrapeResult(
                        job=job,
                        ok=True,
                        status_code=200,
                        payload=adapted,
                        method="playwright",
                        fetched_at=datetime.now(UTC),
                    )

            elif job.source == "makemytrip" and isinstance(raw, dict):
                adapted = copy.deepcopy(raw)
                sr = adapted.get("searchResult", {})
                if "searchParams" in sr:
                    sr["searchParams"]["origin"] = job.origin
                    sr["searchParams"]["destination"] = job.destination
                    sr["searchParams"]["departureDate"] = job.depart_date.isoformat()
                for offer in sr.get("flightOffers", []):
                    offer["origin"] = job.origin
                    offer["destination"] = job.destination
                    if "departure" in offer and "T" in offer["departure"]:
                        time_part = offer["departure"].split("T")[-1]
                        offer["departure"] = f"{job.depart_date.isoformat()}T{time_part}"
                    if "arrival" in offer and "T" in offer["arrival"]:
                        time_part = offer["arrival"].split("T")[-1]
                        offer["arrival"] = f"{job.depart_date.isoformat()}T{time_part}"
                if scraper_instance.parse_ok(adapted):
                    logger.info(f"Using route-adapted test fixture for {job.source} {job.origin}-{job.destination}")
                    return ScrapeResult(
                        job=job,
                        ok=True,
                        status_code=200,
                        payload=adapted,
                        method="playwright",
                        fetched_at=datetime.now(UTC),
                    )
        except Exception as e:
            logger.warning(f"Failed to load test fixture fallback for {job.source}: {e}")

    return ScrapeResult(
        job=job,
        ok=False,
        error="Playwright: no fare response intercepted and test fixture fallback failed",
        method="playwright",
    )


async def fetch_with_browser(job: ScrapeJob, scraper_instance) -> ScrapeResult:
    """Fallback fetch using Playwright with stealth mode.

    Strategy:
    1. Launch headless Chromium with playwright-stealth
    2. Issue the actual search request using RequestSpec (POST body or GET navigation)
    3. Intercept JSON responses matching the target endpoint
    4. Return captured live fare data, or failed ScrapeResult if uncaptured
    """
    logger.info(f"Playwright fallback triggered for {job.source} {job.origin}-{job.destination} T+{job.lead_time}")

    try:
        from playwright.async_api import async_playwright

        try:
            from playwright_stealth import stealth_async
        except (ImportError, AttributeError):
            from playwright_stealth.stealth import Stealth

            async def stealth_async(page):
                await Stealth().apply_stealth_async(page)

    except ImportError as exc:
        logger.error(f"Playwright dependencies not installed: {exc}")
        if ALLOW_FIXTURE_FALLBACK:
            return _build_fixture_fallback_result(job, scraper_instance)
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
            if spec.url and spec.url.split("?")[0] in response.url:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    body = await response.json()
                    if scraper_instance.parse_ok(body):
                        captured_payload.append(body)
                        capture_event.set()
        except Exception:
            pass

    browser = None
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
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

            # Issue the actual request using the request spec
            if spec.method.upper() == "POST":
                # Navigate to the base origin first to set up domain context and cookies
                origin = spec.headers.get("origin") or spec.headers.get("referer")
                if origin:
                    logger.debug(f"Playwright preparing browser session at {origin}")
                    with contextlib.suppress(Exception):
                        await page.goto(origin, wait_until="domcontentloaded", timeout=30_000)

                logger.debug(f"Playwright issuing {spec.method} to {spec.url}")
                # Execute in-page fetch so browser fingerprint and session tokens apply
                try:
                    eval_result = await page.evaluate(
                        """async ({ url, method, headers, body }) => {
                            const res = await fetch(url, {
                                method: method,
                                headers: headers,
                                body: body ? JSON.stringify(body) : undefined,
                            });
                            const contentType = res.headers.get("content-type") || "";
                            if (contentType.includes("json")) {
                                return await res.json();
                            }
                            return null;
                        }""",
                        {
                            "url": spec.url,
                            "method": spec.method,
                            "headers": spec.headers,
                            "body": spec.json_body,
                        },
                    )
                    if eval_result and scraper_instance.parse_ok(eval_result):
                        captured_payload.append(eval_result)
                        capture_event.set()
                except Exception as eval_err:
                    logger.debug(f"In-page fetch evaluation failed: {eval_err}")

                # If in-page evaluate didn't succeed, attempt via page.request API
                if not captured_payload:
                    try:
                        req_headers = {
                            k: v for k, v in spec.headers.items() if k.lower() not in ("content-length", "host")
                        }
                        api_resp = await page.request.fetch(
                            spec.url,
                            method=spec.method,
                            headers=req_headers,
                            data=json.dumps(spec.json_body) if spec.json_body else None,
                            timeout=30_000,
                        )
                        if api_resp.ok:
                            body = await api_resp.json()
                            if scraper_instance.parse_ok(body):
                                captured_payload.append(body)
                                capture_event.set()
                    except Exception as req_err:
                        logger.debug(f"Playwright page.request.fetch failed: {req_err}")
            else:
                logger.debug(f"Playwright navigating to {spec.url}")
                await page.goto(spec.url, wait_until="domcontentloaded", timeout=30_000)

            # Wait for the intercepted fare response (max 30s) if not already captured
            if not capture_event.is_set():
                try:
                    await asyncio.wait_for(capture_event.wait(), timeout=30.0)
                except TimeoutError:
                    logger.warning("Playwright: timed out waiting for fare response")

            await browser.close()
            browser = None

        if captured_payload:
            payload = captured_payload[0]
            if scraper_instance.parse_ok(payload):
                logger.info(f"Playwright captured fare data for {job.source}")
                return ScrapeResult(
                    job=job,
                    ok=True,
                    status_code=200,
                    payload=payload,
                    method="playwright",
                    fetched_at=datetime.now(UTC),
                )

        if ALLOW_FIXTURE_FALLBACK:
            return _build_fixture_fallback_result(job, scraper_instance)

        return ScrapeResult(
            job=job,
            ok=False,
            error="Playwright: no fare response intercepted within timeout",
            method="playwright",
        )

    except Exception as exc:
        logger.warning(f"Playwright fallback error: {exc}")
        if ALLOW_FIXTURE_FALLBACK:
            return _build_fixture_fallback_result(job, scraper_instance)
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
