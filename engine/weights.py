"""DGCA passenger weight loading and normalisation."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def load_weights(csv_path: str = "config/dgca_weights.csv") -> dict[str, float]:
    """
    Load DGCA passenger weights from CSV and normalise to sum to 1.

    Returns:
        dict mapping route_code to normalised weight.
    """
    path = Path(csv_path)
    if not path.exists():
        logger.warning("DGCA weights file not found: {}, using equal weights", csv_path)
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

    logger.info("Loaded DGCA weights: {} routes, sum={:.4f}", len(weights), sum(weights.values()))
    return weights


def get_base_period_prices(session: Session | None = None, n_days: int = 7) -> dict[int, float]:
    """
    Get base period prices (first n_days of data) for each route.

    These are the P_i0 values in the Laspeyres formula.
    Base period = 100.
    Delegates to db.queries.get_base_period_prices.
    """
    from db import queries as db_queries
    from db.session import SessionLocal

    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        return db_queries.get_base_period_prices(session, n_days=n_days)
    finally:
        if owns_session:
            session.close()
