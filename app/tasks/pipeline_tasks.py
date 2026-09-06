"""Celery tasks for pipeline operations.

The clean_and_load task runs the full cleaning pipeline for a given scrape date:
parse → validate → unbundle → IQR filter → load to fare_quotes.
"""

from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.pipeline_tasks.clean_and_load", bind=True)
def clean_and_load(self, scrape_date_str: str) -> dict:
    """
    Run the full cleaning pipeline for a given scrape date.

    Calls pipeline.run.run_pipeline() programmatically (not CLI).
    Returns stats dict: {parsed, valid, unbundled, outliers, loaded}.
    """
    from datetime import date

    from pipeline.run import run_pipeline

    scrape_date = date.fromisoformat(scrape_date_str)

    stats = run_pipeline(scrape_date.isoformat())
    # stats = {"parsed": N, "valid": N, "loaded": N, "outliers": N}

    logger.info(f"Pipeline complete for {scrape_date}: {stats}")
    return stats
