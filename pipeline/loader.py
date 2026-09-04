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

    # TODO: Implement when db models are ready
    # from db.session import SessionLocal
    # from db.models import FareQuote
    # from sqlalchemy.dialects.postgresql import insert
    #
    # session = SessionLocal()
    # count = 0
    # for row in df.iter_rows(named=True):
    #     stmt = insert(FareQuote).values(**row).on_conflict_do_update(...)
    #     session.execute(stmt)
    #     count += 1
    # session.commit()
    # session.close()
    # return count

    logger.info(f"Loader: would insert {len(df)} rows into fare_quotes (not yet implemented)")
    return len(df)
