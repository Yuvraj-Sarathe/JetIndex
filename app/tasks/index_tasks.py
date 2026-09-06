"""Celery tasks for index computation.

The compute_daily_index task calculates the DGCA-weighted Laspeyres index
for a given date and writes the result to the apix_daily table.
"""

from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.index_tasks.compute_daily_index", bind=True)
def compute_daily_index(self, compute_date_str: str) -> dict:
    """
    Compute Laspeyres index for the given date, write to apix_daily.

    Steps:
    1. Get median fares per route for compute_date
    2. Load DGCA weights
    3. Get base period prices (first 7 days of data)
    4. Compute Laspeyres index
    5. Upsert to apix_daily table
    """
    from datetime import date

    from db.session import SessionLocal
    from engine.index_calculator import compute_daily

    compute_date = date.fromisoformat(compute_date_str)

    session = SessionLocal()
    try:
        result = compute_daily(compute_date, session)
        logger.info(f"Index computed for {compute_date}: APIx={result['apix']}")
        return result
    finally:
        session.close()
