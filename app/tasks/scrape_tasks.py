"""Celery tasks for scraping operations."""

from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.scrape_tasks.run_daily_sweep")
def run_daily_sweep() -> dict:
    """
    Orchestrate the nightly scrape sweep.

    For each enabled source × route × lead_time, enqueue scrape_route tasks.
    On completion, trigger clean_and_load → compute_daily_index.
    """
    logger.info("Starting daily sweep")
    # TODO: Implement when scrapers are ready
    # from scrapers.registry import build_jobs_for_date
    # from datetime import date
    # jobs = build_jobs_for_date(date.today())
    # return {"jobs_queued": len(jobs)}
    raise NotImplementedError("Owner: Sourabh/Abhay")


@shared_task(name="app.tasks.scrape_tasks.scrape_route")
def scrape_route(source: str, route_code: str, lead_time: int) -> dict:
    """
    Scrape a single route × lead time × source combination.

    Returns dict with status and path to raw payload.
    """
    logger.info(f"Scraping {source} {route_code} T+{lead_time}")
    # TODO: Implement when scrapers are ready
    # from scrapers.registry import get_scraper
    # from scrapers.base_scraper import ScrapeJob
    # scraper = get_scraper(source)
    # job = ScrapeJob(...)
    # result = scraper.fetch(job)
    # return {"ok": result.ok, "raw_path": result.raw_path}
    raise NotImplementedError("Owner: Sourabh/Abhay")
