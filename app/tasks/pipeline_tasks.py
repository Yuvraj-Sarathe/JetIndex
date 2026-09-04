"""Celery tasks for pipeline operations."""

from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.pipeline_tasks.clean_and_load")
def clean_and_load(scrape_date: str) -> dict:
    """
    Run the cleaning pipeline for a given scrape date.

    Parses raw payloads → validates → unbundles → IQR filters → loads to fare_quotes.
    """
    logger.info(f"Running pipeline for {scrape_date}")
    # TODO: Implement when pipeline is ready
    # from pipeline.run import run_pipeline
    # return run_pipeline(scrape_date)
    raise NotImplementedError("Owner: Vanshika")
