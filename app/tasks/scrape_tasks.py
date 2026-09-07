"""Celery tasks for scraping operations.

Design:
- run_daily_sweep: nightly entry point, fans out scrape_route tasks as a group,
  then chains clean_and_load → compute_daily_index via chord callback.
- scrape_route: single (source, route, lead_time) combination. Raw data goes
  to disk + raw_quotes table, not through Celery (payloads too large for Redis).
"""

from datetime import date, timedelta

from celery import chord, group, shared_task
from loguru import logger


@shared_task(name="app.tasks.scrape_tasks.run_daily_sweep", bind=True, max_retries=1)
def run_daily_sweep(self):
    """
    Nightly entry point (02:00 IST via beat).
    1. Build all scrape jobs for today
    2. Fan-out as a Celery group
    3. On completion, trigger clean_and_load → compute_daily_index
    """
    from app.tasks.index_tasks import compute_daily_index
    from app.tasks.pipeline_tasks import clean_and_load
    from scrapers.registry import build_jobs_for_date

    today = date.today()
    jobs = list(build_jobs_for_date(today))
    logger.info(f"Daily sweep: {len(jobs)} jobs for {today}")

    if not jobs:
        logger.warning("No jobs generated — check routes.yaml / sources.yaml")
        return {"status": "no_jobs", "date": str(today)}

    # Fan out scraping, then chain: clean → index
    scrape_group = group(
        scrape_route.s(
            source=j.source,
            route_code=f"{j.origin}-{j.destination}",
            lead_time=j.lead_time,
        )
        for j in jobs
    )

    # Callback fires only when ALL scrape jobs complete.
    # si() = immutable signature — prevents Celery from injecting group results as arg.
    callback = clean_and_load.si(str(today)) | compute_daily_index.si(str(today))

    workflow = chord(scrape_group, callback)
    workflow.apply_async()

    return {
        "status": "dispatched",
        "date": str(today),
        "n_jobs": len(jobs),
    }


@shared_task(
    name="app.tasks.scrape_tasks.scrape_route",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    reject_on_worker_lost=True,
)
def scrape_route(self, source: str, route_code: str, lead_time: int):
    """
    Scrape a single (source, route, lead_time) combination.
    Returns a dict summary (for monitoring), not the raw data
    (raw data goes to disk + raw_quotes table).
    """
    from scrapers.base_scraper import ScrapeJob
    from scrapers.registry import get_scraper

    today = date.today()
    origin, destination = route_code.split("-")
    depart_date = today + timedelta(days=lead_time)

    job = ScrapeJob(
        source=source,
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        lead_time=lead_time,
        scrape_date=today,
    )

    scraper = get_scraper(source)
    results = scraper.run_jobs([job])  # returns list[ScrapeResult]
    result = results[0]

    if not result.ok:
        logger.error(f"Scrape failed: {source}/{route_code}/T+{lead_time}: {result.error}")
        # Retry on transient failures (rate limit, bad gateway, service unavailable)
        if result.status_code in (429, 503, 502):
            raise self.retry(exc=Exception(result.error))

    return {
        "source": source,
        "route_code": route_code,
        "lead_time": lead_time,
        "ok": result.ok,
        "status_code": result.status_code,
        "method": result.method,
        "raw_path": result.raw_path,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run or submit a scrape_route task")
    parser.add_argument("--route", default="DEL-BOM", help="Route code (e.g. DEL-BOM)")
    parser.add_argument("--lead", type=int, default=7, help="Lead time in days")
    parser.add_argument("--source", default="indigo", help="Source name (e.g. indigo)")
    parser.add_argument("--async-celery", action="store_true", help="Submit asynchronously to Celery queue")
    args = parser.parse_args()

    if args.async_celery:
        result = scrape_route.delay(args.source, args.route, args.lead)
        print(f"Task submitted: {result.id}")
        print(f"  source={args.source}, route={args.route}, lead={args.lead}")
    else:
        res = scrape_route.apply(args=(args.source, args.route, args.lead)).get()
        if res.get("ok"):
            print("OK")
            print(f"Scraped {args.source} {args.route} T+{args.lead} -> {res.get('raw_path')}")
        else:
            print(f"FAILED: {res}")
