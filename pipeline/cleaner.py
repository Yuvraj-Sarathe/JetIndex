"""Data cleaning — deduplication, MAD/IQR outlier detection, batch processing."""

import numpy as np
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


def mad_filter(
    df: pl.DataFrame,
    group_cols: list[str] | None = None,
    threshold: float = 3.0,
    value_col: str = "total_fare",
) -> pl.DataFrame:
    """Median Absolute Deviation (MAD) modified Z-score outlier detection.

    MAD = median(|x_i - median(x)|)
    M_i = 0.6745 * (x_i - median(x)) / MAD

    Falls back to IQR when MAD is near zero (tight clusters with spikes).
    Also flags absolute price-floor (< ₹500) and price-ceiling (> ₹75,000)
    violations regardless of the MAD score.

    Reference: Iglewicz & Hoaglin (1993)
    """
    if group_cols is None:
        group_cols = ["route_code", "lead_time", "scrape_date"]
    group_cols = [c for c in group_cols if c in df.columns]

    def _mad_flag(group: pl.DataFrame) -> pl.DataFrame:
        n = len(group)
        if n < 3:
            return group.with_columns(pl.lit("ok").alias("mad_flag"))

        fares = group[value_col].to_numpy().astype(float)
        med = float(np.median(fares))
        abs_dev = float(np.median(np.abs(fares - med)))

        if abs_dev > 1e-4:
            mod_z = 0.6745 * np.abs(fares - med) / abs_dev
            outlier_mask = (mod_z > threshold) | (fares > 75_000) | (fares < 500)
        else:
            # Fallback: Tukey IQR
            q25 = float(np.percentile(fares, 25))
            q75 = float(np.percentile(fares, 75))
            iqr = q75 - q25
            if iqr > 1e-4:
                outlier_mask = (fares < q25 - 1.5 * iqr) | (fares > q75 + 1.5 * iqr) | (fares > 75_000) | (fares < 500)
            else:
                outlier_mask = (fares < 0.3 * med) | (fares > 3.0 * med) | (fares > 75_000) | (fares < 500)

        flags = ["mad_outlier" if m else "ok" for m in outlier_mask]
        return group.with_columns(pl.Series("mad_flag", flags))

    result = df.group_by(group_cols, maintain_order=True).map_groups(_mad_flag) if group_cols else _mad_flag(df)

    # Merge MAD flag into quality_flag
    result = result.with_columns(
        pl.when(pl.col("mad_flag") == "mad_outlier")
        .then(pl.lit("mad_outlier"))
        .otherwise(pl.col("quality_flag"))
        .alias("quality_flag")
    )

    n_outliers = len(result.filter(pl.col("quality_flag") == "mad_outlier"))
    if n_outliers:
        logger.info(f"MAD filter: flagged {n_outliers} outliers")

    return result.drop("mad_flag")


def dedupe_multi_ota(df: pl.DataFrame) -> pl.DataFrame:
    """Cross-source deduplication: prefer direct airline quotes over OTA copies.

    Groups by (flight_no, depart_date, depart_time) — if a route has both a
    DIRECT source and an OTA source for the same physical flight, keep only
    the direct quote.  If no direct quote exists, keep the lowest net fare.

    This prevents double-counting the same seat when the same flight appears
    on both the airline portal and MakeMyTrip/EaseMyTrip/Cleartrip.
    """
    if "source" not in df.columns or "flight_no" not in df.columns:
        return df

    before = len(df)
    key_cols = ["flight_no", "depart_date"]
    if "depart_time" in df.columns:
        key_cols.append("depart_time")

    # Ensure key columns exist
    key_cols = [c for c in key_cols if c in df.columns]
    if not key_cols:
        return df

    def _pick_best(group: pl.DataFrame) -> pl.DataFrame:
        if len(group) == 1:
            return group

        # Prefer direct airline source
        direct = group.filter(pl.col("source").str.contains("indigo|airindia|akasa|spicejet", literal=False))
        if len(direct) > 0:
            return direct.head(1)

        # Fallback: lowest total_fare
        return group.sort("total_fare").head(1)

    result = df.group_by(key_cols, maintain_order=True).map_groups(_pick_best)
    after = len(result)
    if before != after:
        logger.info(f"Multi-OTA dedup: removed {before - after} duplicate quotes across sources")
    return result


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
    df = dedupe_multi_ota(df)
    df = flag_sold_out(df)
    df = mad_filter(df)
    df = iqr_filter(df)

    # Summary
    status_counts = df.group_by("quality_flag").agg(pl.len().alias("count"))
    logger.info(f"Clean batch: quality_flag distribution: {status_counts.to_dicts()}")

    return df


def cleaning_summary(df: pl.DataFrame) -> dict:
    """Return telemetry stats from a cleaned DataFrame."""
    total = len(df)
    if total == 0:
        return {"total": 0, "valid": 0, "deduped": 0, "outliers": 0, "routes": 0}

    valid = len(df.filter(pl.col("quality_flag") == "ok"))
    outliers = len(df.filter(pl.col("quality_flag").is_in(["iqr_outlier", "mad_outlier"])))
    routes = df["route_code"].n_unique() if "route_code" in df.columns else 0

    return {
        "total": total,
        "valid": valid,
        "outliers": outliers,
        "routes": routes,
    }
