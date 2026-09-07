"""Loader — upsert CleanQuote rows into fare_quotes table."""

import polars as pl
from loguru import logger


def load(df: pl.DataFrame) -> int:
    """
    Load a Polars DataFrame of CleanQuote rows into the fare_quotes table.

    Returns the number of rows inserted/updated.
    """
    if df.is_empty():
        logger.info("Nothing to load — empty DataFrame")
        return 0

    from db.queries import upsert_fare_quotes
    from db.session import SessionLocal

    records = df.to_dicts()
    session = SessionLocal()
    try:
        count = upsert_fare_quotes(session, records)
        return count
    finally:
        session.close()
