"""Index calculation — Laspeyres, Geometric Young, and daily computation."""

from datetime import date

from loguru import logger


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
    import math

    log_sum = 0.0
    for route in p_0:
        if route in p_t and route in q_0 and p_0[route] > 0:
            ratio = p_t[route] / p_0[route]
            log_sum += q_0[route] * math.log(ratio)

    index = math.exp(log_sum) * 100
    return round(index, 4)


def compute_daily(
    compute_date: str | date,
    session=None,
    lead_times: tuple[int, ...] = (1, 7, 15, 30, 45),
    price_agg: str = "median",
) -> dict:
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

    logger.info(f"Computing daily index for {compute_date}")

    # TODO: Implement with real DB queries
    # from db.models import FareQuote, Route, ApixDaily
    # from engine.weights import load_weights, get_base_period_prices
    # from sqlalchemy import func
    #
    # # Get prices per route for this date
    # prices_today = {}
    # for route in routes:
    #     median_fare = session.query(
    #         func.percentile_cont(0.5).within_group(FareQuote.total_fare)
    #     ).filter(
    #         FareQuote.route_id == route.id,
    #         FareQuote.scrape_date == compute_date,
    #         FareQuote.quality_flag == "ok"
    #     ).scalar()
    #     prices_today[route.route_code] = median_fare or 0.0
    #
    # # Load weights and base prices
    # weights = load_weights()
    # base_prices = get_base_period_prices(session)
    #
    # # Compute index
    # apix = laspeyres(prices_today, base_prices, weights)
    #
    # # Write to DB
    # apix_record = ApixDaily(
    #     date=compute_date,
    #     apix=apix,
    #     n_quotes=n_quotes,
    #     n_routes=len(prices_today),
    #     method="laspeyres",
    #     base_period=f"{base_start} to {base_end}",
    # )
    # session.merge(apix_record)
    # session.commit()

    # Placeholder: return mock value
    logger.warning("compute_daily: using placeholder values")
    return {
        "date": compute_date.isoformat(),
        "apix": 100.0,
        "apix_base_only": 100.0,
        "n_quotes": 0,
        "n_routes": 6,
        "method": "laspeyres",
        "base_period": "placeholder",
    }
