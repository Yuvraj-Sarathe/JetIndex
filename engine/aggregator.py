"""Daily → weekly/monthly rollups and percentage change helpers."""

from datetime import date

from loguru import logger


def weekly_rollup(session, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
    """
    Compute weekly average APIx from daily values.

    Returns list of dicts with week_start, apix_avg, n_days.
    """
    # TODO: Implement with real DB query
    # SELECT date_trunc('week', date) as week_start,
    #        AVG(apix) as apix_avg,
    #        COUNT(*) as n_days
    # FROM apix_daily
    # WHERE date BETWEEN :start AND :end
    # GROUP BY week_start
    # ORDER BY week_start

    logger.warning("weekly_rollup: using placeholder values")
    return []


def monthly_rollup(session, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
    """
    Compute monthly average APIx from daily values.

    Returns list of dicts with month, apix_avg, n_days.
    """
    # TODO: Implement with real DB query
    # SELECT date_trunc('month', date) as month,
    #        AVG(apix) as apix_avg,
    #        COUNT(*) as n_days
    # FROM apix_daily
    # WHERE date BETWEEN :start AND :end
    # GROUP BY month
    # ORDER BY month

    logger.warning("monthly_rollup: using placeholder values")
    return []


def pct_change(current: float, previous: float) -> float | None:
    """Calculate percentage change between two values."""
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 2)


def daily_with_pct(series: list[dict]) -> list[dict]:
    """Add day-over-day percentage change to a daily APIx series."""
    for i, entry in enumerate(series):
        if i == 0:
            entry["pct_change_dod"] = None
        else:
            entry["pct_change_dod"] = pct_change(entry["apix"], series[i - 1]["apix"])
    return series
