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

    import statistics
    from collections import defaultdict

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
            logger.info(f"No fare data for exact date {compute_date}, trying ±3 day window")
            from datetime import timedelta

            for offset in range(1, 4):
                for sign in (1, -1):
                    alt_date = compute_date + timedelta(days=sign * offset)
                    fare_rows = db_queries.get_median_fares_by_route(
                        session=session,
                        scrape_date=alt_date,
                        lead_times=lead_times,
                    )
                    if fare_rows:
                        logger.info(f"Found fare data for {alt_date} ({len(fare_rows)} route×lead_time groups)")
                        break
                if fare_rows:
                    break

        logger.info(f"compute_daily: got {len(fare_rows)} route×lead_time groups for {compute_date}")

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
            f"compute_daily: {len(prices_today)} routes with prices, "
            f"{len(weights)} routes with weights, "
            f"{len(base_prices)} routes with base prices"
        )

        # 4. Compute Laspeyres index
        if prices_today and base_prices and weights:
            apix = laspeyres(prices_today, base_prices, weights)
            apix_base_only = laspeyres(prices_base_today, base_prices, weights) if prices_base_today else apix
        else:
            logger.warning(
                f"compute_daily: Insufficient data for {compute_date} "
                f"(prices={len(prices_today)}, base={len(base_prices)}, weights={len(weights)}). Defaulting to 100.0"
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
