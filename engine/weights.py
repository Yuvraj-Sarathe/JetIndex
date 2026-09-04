"""DGCA passenger weight loading and normalisation."""

import csv
from pathlib import Path

from loguru import logger


def load_weights(csv_path: str = "config/dgca_weights.csv") -> dict[str, float]:
    """
    Load DGCA passenger weights from CSV and normalise to sum to 1.

    Returns:
        dict mapping route_code to normalised weight.
    """
    path = Path(csv_path)
    if not path.exists():
        logger.warning(f"DGCA weights file not found: {csv_path}, using equal weights")
        return {}

    weights: dict[str, float] = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            route_code = row["route_code"]
            weight = float(row["weight"])
            weights[route_code] = weight

    # Normalise to sum to 1
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}

    logger.info(f"Loaded DGCA weights: {len(weights)} routes, sum={sum(weights.values()):.4f}")
    return weights


def get_base_period_prices(session, n_days: int = 7) -> dict[str, float]:
    """
    Get base period prices (first n_days of data) for each route.

    These are the P_i0 values in the Laspeyres formula.
    Base period = 100.
    """
    # TODO: Implement with real DB query
    # from db.models import FareQuote, Route
    # from sqlalchemy import func
    #
    # # Get the earliest scrape_date
    # earliest = session.query(func.min(FareQuote.scrape_date)).scalar()
    # base_end = earliest + timedelta(days=n_days)
    #
    # # Compute median total_fare per route for base period
    # prices = session.query(
    #     Route.route_code,
    #     func.percentile_cont(0.5).within_group(FareQuote.total_fare)
    # ).join(Route).filter(
    #     FareQuote.scrape_date >= earliest,
    #     FareQuote.scrape_date < base_end,
    #     FareQuote.quality_flag == "ok"
    # ).group_by(Route.route_code).all()
    #
    # return {route_code: price for route_code, price in prices}

    # Placeholder: equal prices for all routes
    logger.warning("get_base_period_prices: using placeholder values")
    return {
        "DEL-BOM": 5000.0,
        "DEL-BLR": 5500.0,
        "BOM-BLR": 4500.0,
        "DEL-CCU": 6000.0,
        "BLR-HYD": 3500.0,
        "MAA-DEL": 5000.0,
    }
