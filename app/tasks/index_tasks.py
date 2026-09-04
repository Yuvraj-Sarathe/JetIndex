"""Celery tasks for index computation."""

from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.index_tasks.compute_daily_index")
def compute_daily_index(compute_date: str) -> dict:
    """
    Compute the daily APIx index for a given date.

    Runs Laspeyres calculation with DGCA weights, writes to apix_daily.
    """
    logger.info(f"Computing daily index for {compute_date}")
    # TODO: Implement when engine is ready
    # from engine.index_calculator import compute_daily
    # return compute_daily(compute_date)
    raise NotImplementedError("Owner: Sourabh/Abhay")
