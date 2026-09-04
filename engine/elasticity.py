"""Lead-time elasticity matrix — fare vs lead time per route."""

from loguru import logger


def compute_elasticity(session, route_id: int | None = None, route_date=None) -> list[dict]:
    """
    Compute lead-time elasticity matrix.

    For each route × lead_time, compute median total_fare.
    Elasticity = d ln(P) / d ln(lead_time) via linear regression.

    Returns list of dicts with route_id, lead_time, avg_total_fare, avg_base_fare, n.
    """
    # TODO: Implement with real DB query
    # from db.models import FareQuote
    # from sqlalchemy import func
    #
    # query = session.query(
    #     FareQuote.route_id,
    #     FareQuote.lead_time,
    #     func.percentile_cont(0.5).within_group(FareQuote.total_fare).label("avg_total_fare"),
    #     func.percentile_cont(0.5).within_group(FareQuote.base_fare).label("avg_base_fare"),
    #     func.count().label("n"),
    # ).filter(FareQuote.quality_flag == "ok")
    #
    # if route_id:
    #     query = query.filter(FareQuote.route_id == route_id)
    # if route_date:
    #     query = query.filter(FareQuote.scrape_date == route_date)
    #
    # results = query.group_by(FareQuote.route_id, FareQuote.lead_time).all()
    # return [
    #     {"route_id": r.route_id, "lead_time": r.lead_time,
    #      "avg_total_fare": r.avg_total_fare, "avg_base_fare": r.avg_base_fare,
    #      "n": r.n}
    #     for r in results
    # ]

    logger.warning("compute_elasticity: using placeholder values")
    return [
        {"lead_time": lt, "avg_total_fare": 5000 + (45 - lt) * 50, "avg_base_fare": 4000 + (45 - lt) * 40, "n": 10}
        for lt in [1, 7, 15, 30, 45]
    ]


def compute_elasticity_coefficient(fares: list[float], lead_times: list[int]) -> float | None:
    """
    Compute elasticity coefficient using log-log regression.

    elasticity = d ln(P) / d ln(lead_time)

    Negative elasticity means fares decrease as lead time increases (advance purchase discount).
    """
    import math

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
    except Exception as e:
        logger.error(f"Elasticity computation failed: {e}")
        return None
