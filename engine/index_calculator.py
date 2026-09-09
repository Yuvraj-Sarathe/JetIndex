"""Index calculation — Laspeyres, Geometric Young, Jevons, Paasche, Fisher, Törnqvist, Walsh, and daily computation.

Superlative index formulas ported from VayuSutra-V4 for ILO CPI Manual compliance.
CPI transmission (bps) calculation included.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import date, timedelta
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# ──────────────────────────────────────────────────────────────────────────────
# CPI Basket Weights (from config/cpi_weights.yaml, hardcoded for speed)
# ──────────────────────────────────────────────────────────────────────────────
_AIRFARE_SHARE_IN_TRANSPORT = 0.0385  # 3.85%
_TRANSPORT_CPI_WEIGHT = 0.0859  # 8.59%
_DEMAND_ELASTICITY = -0.85  # Paasche substitution parameter


def laspeyres(p_t: dict[str, float], p_0: dict[str, float], q_0: dict[str, float]) -> float:
    """
    Compute Laspeyres price index.

    I_t = Σ(P_it · Q_i0) / Σ(P_i0 · Q_i0) × 100

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}

    Returns:
        Index value (base period = 100)
    """
    numerator = 0.0
    denominator = 0.0

    for route in p_0:
        if route in p_t and route in q_0:
            numerator += p_t[route] * q_0[route]
            denominator += p_0[route] * q_0[route]

    if denominator == 0:
        logger.error("Laspeyres: denominator is zero")
        return 100.0

    index = (numerator / denominator) * 100
    return round(index, 4)


def geometric_young(p_t: dict[str, float], p_0: dict[str, float], q_0: dict[str, float]) -> float:
    """
    Compute Geometric Young price index.

    I_t = Π(P_it / P_i0)^(Q_i0) × 100

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}

    Returns:
        Index value (base period = 100)
    """
    log_sum = 0.0
    for route in p_0:
        if route in p_t and route in q_0 and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            log_sum += q_0[route] * math.log(ratio)

    index = math.exp(log_sum) * 100
    return round(index, 4)


def jevons(p_t: dict[str, float], p_0: dict[str, float], q_0: dict[str, float]) -> float:
    """
    Compute Jevons (geometric mean of price relatives) index.

    J_r = (∏ p_1k / p_0k)^(1/n)

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights (unused, kept for signature consistency)

    Returns:
        Index value (base period = 100)
    """
    log_sum = 0.0
    n = 0

    for route in p_0:
        if route in p_t and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            log_sum += math.log(max(1e-6, ratio))
            n += 1

    if n == 0:
        logger.error("Jevons: no valid price relatives")
        return 100.0

    index = math.exp(log_sum / n) * 100
    return round(index, 4)


def paasche(
    p_t: dict[str, float], p_0: dict[str, float], q_t: dict[str, float], elasticity: float = _DEMAND_ELASTICITY
) -> float:
    """
    Compute Paasche price index with demand substitution.

    I_P = Σ(p_1 × q_1) / Σ(p_0 × q_1) × 100

    Uses current-period quantity weights derived from price elasticity:
        q_1r ∝ w_r × R_r^(1+ε)  where R_r = p_1r/p_0r

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_t: Current period quantities/weights {route_code: weight}
        elasticity: Demand price elasticity (default -0.85)

    Returns:
        Index value (base period = 100)
    """
    numerator = 0.0
    denominator = 0.0

    for route in p_0:
        if route in p_t and route in q_t and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            # Current-period expenditure weight: w_r × R_r^(1+ε)
            current_weight = q_t[route] * (ratio ** (1.0 + elasticity))
            numerator += p_t[route] * current_weight
            denominator += p_0[route] * current_weight

    if denominator == 0:
        logger.error("Paasche: denominator is zero")
        return 100.0

    index = (numerator / denominator) * 100
    return round(index, 4)


def fisher(
    p_t: dict[str, float],
    p_0: dict[str, float],
    q_0: dict[str, float],
    q_t: dict[str, float] | None = None,
    elasticity: float = _DEMAND_ELASTICITY,
) -> float:
    """
    Compute Fisher Ideal index (geometric mean of Laspeyres and Paasche).

    I_F = sqrt(I_L × I_P)

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}
        q_t: Current period quantities/weights (defaults to q_0 if None)
        elasticity: Demand price elasticity for Paasche calculation

    Returns:
        Index value (base period = 100)
    """
    if q_t is None:
        q_t = q_0

    i_l = laspeyres(p_t, p_0, q_0)
    i_p = paasche(p_t, p_0, q_t, elasticity)

    index = math.sqrt(i_l * i_p)
    return round(index, 4)


def tornqvist(
    p_t: dict[str, float],
    p_0: dict[str, float],
    q_0: dict[str, float],
    q_t: dict[str, float] | None = None,
    elasticity: float = _DEMAND_ELASTICITY,
) -> float:
    """
    Compute Törnqvist superlative index.

    I_T = ∏(p_1/p_0)^((s_0+s_1)/2) × 100

    Where s_0 and s_1 are base and current period expenditure shares.

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}
        q_t: Current period quantities/weights (defaults to q_0 if None)
        elasticity: Demand price elasticity for current weight derivation

    Returns:
        Index value (base period = 100)
    """
    if q_t is None:
        q_t = q_0

    # Compute expenditure shares (s_0 and s_1)
    total_base = sum(q_0[r] * p_0.get(r, 0) for r in q_0 if r in p_0)
    total_current = 0.0

    current_weights: dict[str, float] = {}
    for route in p_0:
        if route in p_t and route in q_0 and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            cw = q_t.get(route, q_0[route]) * (ratio ** (1.0 + elasticity))
            current_weights[route] = cw
            total_current += cw

    log_sum = 0.0
    for route in p_0:
        if route in p_t and route in q_0 and p_0[route] > 0 and total_base > 0 and total_current > 0:
            s_0 = (q_0[route] * p_0[route]) / total_base
            s_1 = current_weights.get(route, 0) / total_current
            ratio = p_t[route] / p_0[route]
            log_sum += ((s_0 + s_1) / 2.0) * math.log(max(1e-6, ratio))

    index = math.exp(log_sum) * 100
    return round(index, 4)


def walsh(
    p_t: dict[str, float],
    p_0: dict[str, float],
    q_0: dict[str, float],
    q_t: dict[str, float] | None = None,
    elasticity: float = _DEMAND_ELASTICITY,
) -> float:
    """
    Compute Walsh geometric weight superlative index.

    I_W = Σ(p_1 × √(q_0 × q_1)) / Σ(p_0 × √(q_0 × q_1)) × 100

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}
        q_t: Current period quantities/weights (defaults to q_0 if None)
        elasticity: Demand price elasticity for current weight derivation

    Returns:
        Index value (base period = 100)
    """
    if q_t is None:
        q_t = q_0

    numerator = 0.0
    denominator = 0.0

    for route in p_0:
        if route in p_t and route in q_0 and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            cw = q_t.get(route, q_0[route]) * (ratio ** (1.0 + elasticity))
            geometric_weight = math.sqrt(q_0[route] * max(1e-6, cw))
            numerator += p_t[route] * geometric_weight
            denominator += p_0[route] * geometric_weight

    if denominator == 0:
        logger.error("Walsh: denominator is zero")
        return 100.0

    index = (numerator / denominator) * 100
    return round(index, 4)


def cpi_transmission_bps(
    current_index: float,
    previous_index: float,
) -> dict[str, float]:
    """
    Calculate CPI transmission in basis points.

    Δ% = (current_index - previous_index) / previous_index × 100
    transport_bps = Δ% × 3.85 / 100 × 10000
    headline_bps = transport_bps × 8.59 / 100

    Args:
        current_index: Current period index value
        previous_index: Previous period index value

    Returns:
        Dict with daily_pct_change, transport_bps, headline_bps
    """
    if previous_index == 0:
        return {"daily_pct_change": 0.0, "transport_bps": 0.0, "headline_bps": 0.0}

    daily_pct = ((current_index - previous_index) / previous_index) * 100.0
    transport_bps = daily_pct * _AIRFARE_SHARE_IN_TRANSPORT * 100.0
    headline_bps = transport_bps * _TRANSPORT_CPI_WEIGHT

    return {
        "daily_pct_change": round(daily_pct, 4),
        "transport_bps": round(transport_bps, 4),
        "headline_bps": round(headline_bps, 4),
    }


def compute_all_indices(
    p_t: dict[str, float],
    p_0: dict[str, float],
    q_0: dict[str, float],
    previous_index: float | None = None,
) -> dict[str, float]:
    """
    Compute all 6 index formulas and CPI transmission in one call.

    Args:
        p_t: Current period prices {route_code: price}
        p_0: Base period prices {route_code: price}
        q_0: Base period quantities/weights {route_code: weight}
        previous_index: Previous period Laspeyres index (for chaining and CPI calc)

    Returns:
        Dict with all index values, substitution bias, and CPI transmission bps
    """
    i_l = laspeyres(p_t, p_0, q_0)
    i_j = jevons(p_t, p_0, q_0)
    i_p = paasche(p_t, p_0, q_0)
    i_f = fisher(p_t, p_0, q_0)
    i_t = tornqvist(p_t, p_0, q_0)
    i_w = walsh(p_t, p_0, q_0)

    # Substitution bias: Laspeyres overstates relative to Fisher
    sub_bias_points = i_l - i_f
    sub_bias_bps = sub_bias_points * _AIRFARE_SHARE_IN_TRANSPORT * 100.0

    # CPI transmission
    cpi = (
        cpi_transmission_bps(i_l, previous_index)
        if previous_index
        else {
            "daily_pct_change": 0.0,
            "transport_bps": 0.0,
            "headline_bps": 0.0,
        }
    )

    # Chained index
    chained = previous_index * (i_l / previous_index) if previous_index and previous_index > 0 else i_l

    return {
        "laspeyres": i_l,
        "jevons": i_j,
        "paasche": i_p,
        "fisher": i_f,
        "tornqvist": i_t,
        "walsh": i_w,
        "chained": round(chained, 4),
        "substitution_bias_points": round(sub_bias_points, 4),
        "substitution_bias_bps": round(sub_bias_bps, 4),
        "daily_pct_change": cpi["daily_pct_change"],
        "transport_bps": cpi["transport_bps"],
        "headline_bps": cpi["headline_bps"],
    }


def compute_daily(
    compute_date: str | date,
    session: Session | None = None,
    lead_times: tuple[int, ...] = (1, 7, 15, 30, 45),
    price_agg: str = "median",
) -> dict[str, str | float | int]:
    """
    Compute the daily APIx index for a given date.

    Steps:
    1. Get prices for each route on compute_date (median across carriers & lead times)
    2. Get DGCA weights
    3. Get base period prices
    4. Compute Laspeyres index
    5. Write to apix_daily table

    Args:
        compute_date: Date to compute index for
        session: SQLAlchemy session (optional)
        lead_times: Lead times to aggregate over
        price_agg: Aggregation method ("median" or "mean")

    Returns:
        Dict with apix value and metadata
    """
    if isinstance(compute_date, str):
        compute_date = date.fromisoformat(compute_date)

    logger.info("Computing daily index for {}", compute_date)

    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        # 1. Fetch median fares per route
        fare_rows = db_queries.get_median_fares_by_route(
            session=session,
            scrape_date=compute_date,
            lead_times=lead_times,
        )

        # Fallback: if no data for exact date, try ±3 day window
        if not fare_rows:
            logger.info("No fare data for exact date {}, trying ±3 day window", compute_date)

            for offset in range(1, 4):
                for sign in (1, -1):
                    alt_date = compute_date + timedelta(days=sign * offset)
                    fare_rows = db_queries.get_median_fares_by_route(
                        session=session,
                        scrape_date=alt_date,
                        lead_times=lead_times,
                    )
                    if fare_rows:
                        logger.info("Found fare data for {} ({} route×lead_time groups)", alt_date, len(fare_rows))
                        break
                if fare_rows:
                    break

        logger.info("compute_daily: got {} route×lead_time groups for {}", len(fare_rows), compute_date)

        # 2. Fetch DGCA weights
        weights = db_queries.get_weights(session)

        # 3. Fetch base period prices
        base_prices = db_queries.get_base_period_prices(session)

        # Aggregate lead-time fares per route
        route_total_fares: dict[int, list[float]] = defaultdict(list)
        route_base_fares: dict[int, list[float]] = defaultdict(list)
        n_quotes = 0

        for row in fare_rows:
            r_id = row["route_id"]
            if row.get("median_fare") is not None:
                route_total_fares[r_id].append(float(row["median_fare"]))
            if row.get("median_base_fare") is not None:
                route_base_fares[r_id].append(float(row["median_base_fare"]))
            n_quotes += int(row.get("n_quotes", 0))

        prices_today: dict[int, float] = {}
        prices_base_today: dict[int, float] = {}
        agg_fn = statistics.mean if price_agg == "mean" else statistics.median

        for r_id, fares in route_total_fares.items():
            if fares:
                prices_today[r_id] = float(agg_fn(fares))

        for r_id, b_fares in route_base_fares.items():
            if b_fares:
                prices_base_today[r_id] = float(agg_fn(b_fares))

        logger.info(
            "compute_daily: {} routes with prices, {} routes with weights, {} routes with base prices",
            len(prices_today),
            len(weights),
            len(base_prices),
        )

        # 4. Compute Laspeyres index
        if prices_today and base_prices and weights:
            apix = laspeyres(prices_today, base_prices, weights)
            apix_base_only = laspeyres(prices_base_today, base_prices, weights) if prices_base_today else apix
        else:
            logger.warning(
                "compute_daily: Insufficient data for {} (prices={}, base={}, weights={}). Defaulting to 100.0",
                compute_date,
                len(prices_today),
                len(base_prices),
                len(weights),
            )
            apix = 100.0
            apix_base_only = 100.0

        # 5. Persist to apix_daily table
        record = {
            "date": compute_date,
            "apix": apix,
            "apix_base_only": apix_base_only,
            "n_quotes": n_quotes,
            "n_routes": len(prices_today),
            "method": "laspeyres",
            "base_period": "first_7_days",
        }
        db_queries.upsert_apix_daily(session, record)

        return {
            "date": compute_date.isoformat(),
            "apix": apix,
            "apix_base_only": apix_base_only,
            "n_quotes": n_quotes,
            "n_routes": len(prices_today),
            "method": "laspeyres",
            "base_period": "first_7_days",
        }
    finally:
        if owns_session:
            session.close()


# ──────────────────────────────────────────────────────────────────────────────
# Chained Index
# ──────────────────────────────────────────────────────────────────────────────


def chained_index(period_indices: list[float]) -> float:
    """Compute chained (link) index from a sequence of period-to-period indices.

    Each entry in *period_indices* is a percentage change relative to the
    previous period (e.g. 102.3 means +2.3 %).  The chained index is the
    product of all periodic indices, with base = 100.

    Chaining corrects substitution bias that accumulates in a fixed-basket
    (Laspeyres) index over long horizons.
    """
    chained = 100.0
    for idx in period_indices:
        chained *= idx / 100.0
    return round(chained, 4)


# ──────────────────────────────────────────────────────────────────────────────
# Regional Breakdown
# ──────────────────────────────────────────────────────────────────────────────

_REGION_MAP: dict[str, list[str]] = {
    "Delhi NCR": ["DEL"],
    "Mumbai MMR": ["BOM"],
    "Bengaluru Karnataka": ["BLR"],
    "Eastern Hub": ["CCU"],
    "Southern Hub": ["MAA", "HYD"],
}


def regional_breakdown(
    route_indices: dict[str, float],
    weights: dict[str, float],
) -> dict[str, dict]:
    """Aggregate route-level indices into five broad regions.

    Returns a dict keyed by region name with sub-keys: index, weight,
    routes, route_count.
    """
    region_data: dict[str, dict] = {}
    for region, iatas in _REGION_MAP.items():
        r_indices = {r: route_indices[r] for r in iatas if r in route_indices}
        r_weights = {r: weights.get(r, 0) for r in r_indices}
        total_w = sum(r_weights.values())
        idx = sum(r_indices[r] * r_weights[r] for r in r_indices) / total_w if total_w > 0 else 100.0
        region_data[region] = {
            "index": round(idx, 4),
            "weight": round(total_w, 6),
            "routes": list(r_indices.keys()),
            "route_count": len(r_indices),
        }
    return region_data


# ──────────────────────────────────────────────────────────────────────────────
# Substitution Bias Measurement
# ──────────────────────────────────────────────────────────────────────────────


def substitution_bias(laspeyres_index: float, fisher_index: float) -> dict:
    """Quantify the substitution bias captured by Laspeyres vs Fisher ideal.

    Laspeyres systematically overstates inflation because consumers
    substitute away from routes that become relatively more expensive.
    Fisher (geometric mean of Laspeyres and Paasche) corrects for this.

    Returns bias in index points and CPI basis points.
    """
    bias_index_points = round(laspeyres_index - fisher_index, 4)
    bias_pct = (laspeyres_index - fisher_index) / fisher_index * 100 if fisher_index else 0
    bias_cpi_bps = round(bias_pct * _TRANSPORT_CPI_WEIGHT * 100, 2)

    return {
        "laspeyres_index": laspeyres_index,
        "fisher_index": fisher_index,
        "bias_index_points": bias_index_points,
        "bias_pct": round(bias_pct, 4),
        "bias_transport_cpi_bps": bias_cpi_bps,
        "interpretation": (
            "Laspeyres overstates inflation"
            if bias_index_points > 0
            else "Laspeyres understates inflation"
            if bias_index_points < 0
            else "No substitution bias detected"
        ),
    }
