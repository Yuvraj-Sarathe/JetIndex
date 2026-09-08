"""Lead-time elasticity matrix — fare vs lead time per route."""

from __future__ import annotations

import math
from datetime import date
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def compute_elasticity(
    session: Session | None = None,
    route_id: int | None = None,
    route_date: date | None = None,
) -> list[dict]:
    """
    Compute lead-time elasticity matrix.

    For each route × lead_time, compute median total_fare.
    Elasticity = d ln(P) / d ln(lead_time) via linear regression.

    Returns list of dicts with route_id, lead_time, avg_total_fare, avg_base_fare, n.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        if route_id is not None:
            rows = db_queries.get_elasticity_data(session, route_id=route_id, route_date=route_date)
            return [
                {
                    "route_id": route_id,
                    "lead_time": int(r["lead_time"]),
                    "avg_total_fare": float(r["median_fare"]) if r.get("median_fare") is not None else 0.0,
                    "avg_base_fare": float(r["median_base_fare"]) if r.get("median_base_fare") is not None else 0.0,
                    "n": int(r["n_quotes"]),
                }
                for r in rows
            ]

        routes = db_queries.get_active_routes(session)
        results = []
        for r in routes:
            rows = db_queries.get_elasticity_data(session, route_id=r.id, route_date=route_date)
            for row in rows:
                results.append(
                    {
                        "route_id": r.id,
                        "lead_time": int(row["lead_time"]),
                        "avg_total_fare": float(row["median_fare"]) if row.get("median_fare") is not None else 0.0,
                        "avg_base_fare": float(row["median_base_fare"])
                        if row.get("median_base_fare") is not None
                        else 0.0,
                        "n": int(row["n_quotes"]),
                    }
                )
        return results
    finally:
        if owns_session:
            session.close()


def compute_elasticity_coefficient(fares: list[float], lead_times: list[int]) -> float | None:
    """
    Compute elasticity coefficient using log-log regression.

    elasticity = d ln(P) / d ln(lead_time)

    Negative elasticity means fares decrease as lead time increases (advance purchase discount).
    """
    if len(fares) < 2 or len(lead_times) < 2:
        return None

    # Filter out zero/negative values
    valid = [(lt, f) for lt, f in zip(lead_times, fares, strict=False) if lt > 0 and f > 0]
    if len(valid) < 2:
        return None

    log_lts = [math.log(lt) for lt, _ in valid]
    log_fares = [math.log(f) for _, f in valid]

    try:
        from scipy.stats import linregress

        slope, _, _, _, _ = linregress(log_lts, log_fares)
        return round(slope, 4)
    except (ValueError, TypeError) as e:
        logger.error("Elasticity computation failed: {}", e)
        return None
