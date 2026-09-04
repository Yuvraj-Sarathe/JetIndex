"""Data cleaning — deduplication, IQR outlier detection, batch processing."""

import polars as pl
from loguru import logger

from pipeline.schemas import CleanQuote


def dedupe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove duplicate quotes based on key columns.

    Keeps the first occurrence (earliest scraped_at).
    """
    key_cols = ["source", "route_code", "carrier", "flight_no", "depart_date", "scrape_date", "fare_class"]
    existing_cols = [c for c in key_cols if c in df.columns]
    before = len(df)
    df = df.unique(subset=existing_cols, keep="first")
    after = len(df)
    if before != after:
        logger.info(f"Deduplication: removed {before - after} duplicates")
    return df


def iqr_filter(
    df: pl.DataFrame,
    group_cols: list[str] | None = None,
    k: float = 1.5,
    value_col: str = "total_fare",
) -> pl.DataFrame:
    """
    IQR-based outlier detection and filtering.

    Groups by group_cols (default: route_code, lead_time, scrape_date),
    computes IQR for total_fare, and flags outliers.
    """
    if group_cols is None:
        group_cols = ["route_code", "lead_time", "scrape_date"]

    # Only use group_cols that exist in the DataFrame
    group_cols = [c for c in group_cols if c in df.columns]

    def flag_outliers(group: pl.DataFrame) -> pl.DataFrame:
        """Flag outliers within a single group."""
        if len(group) < 4:
            return group.with_columns(pl.lit("ok").alias("iqr_flag"))

        q1 = group[value_col].quantile(0.25)
        q3 = group[value_col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - k * iqr
        upper = q3 + k * iqr

        return group.with_columns(
            pl.when((pl.col(value_col) < lower) | (pl.col(value_col) > upper))
            .then(pl.lit("iqr_outlier"))
            .otherwise(pl.lit("ok"))
            .alias("iqr_flag")
        )

    result = df.group_by(group_cols, maintain_order=True).map_groups(flag_outliers) if group_cols else flag_outliers(df)

    # Update quality_flag
    result = result.with_columns(
        pl.when(pl.col("iqr_flag") == "iqr_outlier")
        .then(pl.lit("iqr_outlier"))
        .otherwise(pl.col("quality_flag"))
        .alias("quality_flag")
    )

    n_outliers = len(result.filter(pl.col("quality_flag") == "iqr_outlier"))
    if n_outliers:
        logger.info(f"IQR filter: flagged {n_outliers} outliers")

    return result.drop("iqr_flag")


def flag_sold_out(df: pl.DataFrame) -> pl.DataFrame:
    """Flag sold-out flights, preserving them for audit but excluding from index."""
    if "sold_out" in df.columns:
        return df.with_columns(
            pl.when(pl.col("sold_out")).then(pl.lit("sold_out")).otherwise(pl.col("quality_flag")).alias("quality_flag")
        )
    return df


def clean_batch(quotes: list[CleanQuote]) -> pl.DataFrame:
    """
    Clean a batch of CleanQuote objects:
    1. Convert to Polars DataFrame
    2. Deduplicate
    3. Flag sold-out
    4. IQR outlier detection
    5. Return clean DataFrame
    """
    if not quotes:
        return pl.DataFrame()

    # Convert to DataFrame
    data = [q.model_dump() for q in quotes]
    df = pl.DataFrame(data)

    logger.info(f"Clean batch: starting with {len(df)} quotes")

    # Pipeline
    df = dedupe(df)
    df = flag_sold_out(df)
    df = iqr_filter(df)

    # Summary
    status_counts = df.group_by("quality_flag").agg(pl.len().alias("count"))
    logger.info(f"Clean batch: quality_flag distribution: {status_counts.to_dicts()}")

    return df
