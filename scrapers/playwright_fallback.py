"""Playwright stealth browser fallback for anti-bot protected sites."""

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

    # TODO: Implement when Playwright is needed
    # from playwright.async_api import async_playwright
    # from playwright_stealth import stealth_async
    #
    # async with async_playwright() as p:
    #     browser = await p.chromium.launch(headless=True)
    #     context = await browser.new_context()
    #     page = await context.new_page()
    #     await stealth_async(page)
    #
    #     # Intercept fare responses
    #     fare_data = []
    #     async def handle_response(response):
    #         if <fare-endpoint-pattern> in response.url:
    #             fare_data.append(await response.json())
    #     page.on("response", handle_response)
    #
    #     # Navigate to search page
    #     await page.goto(search_url)
    #     await page.wait_for_timeout(10000)
    #
    #     await browser.close()
    #     return fare_data

    raise NotImplementedError("Owner: Sourabh/Abhay — implement when Playwright fallback needed")
