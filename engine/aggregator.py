"""Daily → weekly/monthly rollups and percentage change helpers."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def weekly_rollup(
    session: Session | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    """
    Compute weekly average APIx from daily values.

    Returns list of dicts with week_start, apix, apix_avg, apix_base_only, n_quotes, n_routes.
    Delegates to db.queries.get_apix_weekly.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        rows = db_queries.get_apix_weekly(session, from_date=start_date, to_date=end_date)
        results = []
        for r in rows:
            item = dict(r)
            # Ensure backward compatibility for callers expecting 'apix_avg' alias alongside 'apix'
            if "apix_avg" not in item:
                item["apix_avg"] = item.get("apix")
            results.append(item)
        return results
    finally:
        if owns_session:
            session.close()


def monthly_rollup(
    session: Session | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    """
    Compute monthly average APIx from daily values.

    Returns list of dicts with month_start, month, apix, apix_avg, apix_base_only, n_quotes, n_routes.
    Delegates to db.queries.get_apix_monthly.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        rows = db_queries.get_apix_monthly(session, from_date=start_date, to_date=end_date)
        results = []
        for r in rows:
            item = dict(r)
            # Ensure backward compatibility for callers expecting 'apix_avg' alias alongside 'apix'
            if "apix_avg" not in item:
                item["apix_avg"] = item.get("apix")
            if "month" not in item and "month_start" in item:
                ms = item["month_start"]
                item["month"] = ms.strftime("%Y-%m") if hasattr(ms, "strftime") else str(ms)[:7]
            results.append(item)
        return results
    finally:
        if owns_session:
            session.close()


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
