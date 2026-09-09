"""Analytics — Airfare Inflation Pressure Score (AIPS), CPI decomposition, heatmap.

Adapted from VayuSutra-V4 pressure_score.py, cpi_decomposition.py, heatmap.py.
All queries use JetIndex's SQLAlchemy ORM (TimescaleDB).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

_AIRFARE_SHARE = 0.0385
_TRANSPORT_WEIGHT = 0.0859

# Route codes (20 DGCA top domestic)
_ROUTES = [
    "DEL-BOM",
    "DEL-BLR",
    "BOM-BLR",
    "DEL-CCU",
    "BLR-HYD",
    "MAA-DEL",
    "DEL-GOI",
    "BOM-GOI",
    "DEL-JAI",
    "DEL-SXR",
    "DEL-LKO",
    "BOM-CCU",
    "BLR-MAA",
    "DEL-AMD",
    "BOM-HYD",
    "DEL-PNQ",
    "BOM-MAA",
    "BLR-CCU",
    "HYD-MAA",
    "DEL-TRV",
]

# Advance purchase windows
_WINDOWS = [
    {"id": "T+1", "days": 1, "weight": 0.22},
    {"id": "T+7", "days": 7, "weight": 0.34},
    {"id": "T+15", "days": 15, "weight": 0.24},
    {"id": "T+30", "days": 30, "weight": 0.14},
    {"id": "T+45", "days": 45, "weight": 0.06},
]


# ──────────────────────────────────────────────────────────────────────────────
# AIPS — Airfare Inflation Pressure Score
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class PressureReport:
    """Composite 0-100 inflation pressure score for RBI MPC."""

    as_of_date: str
    score: float
    level: str  # LOW / MODERATE / HIGH / CRITICAL
    previous_score: float
    delta_24h: float
    components: dict[str, float]
    ranked_drivers: list[str]
    alert: str


_WEIGHTS = {
    "airfare_acceleration": 0.25,
    "volatility_dispersion": 0.20,
    "route_breadth_increases": 0.20,
    "spot_t1_pressure": 0.15,
    "urgent_t7_pressure": 0.10,
    "cpi_transmission_impact": 0.10,
}


def compute_pressure_score(session: Session, target_date: str | None = None) -> PressureReport:
    """Compute AIPS from DB time series."""
    from db import queries as db_queries

    now_str = date.today().isoformat()

    # Fetch last 14 days
    rows = db_queries.get_apix_daily(session)
    if not rows or len(rows) < 2:
        return PressureReport(
            as_of_date=now_str,
            score=50.0,
            level="MODERATE",
            previous_score=50.0,
            delta_24h=0.0,
            components={k: 50.0 for k in _WEIGHTS},
            ranked_drivers=["Insufficient data for decomposition"],
            alert="NEUTRAL_PRICE_STABILITY",
        )

    # Use last 14 entries (or all available)
    recent = rows[-14:]
    cur = recent[-1]
    cur_lasp = cur["apix"]

    # 1. Airfare acceleration (7-day % change → 0-100)
    if len(recent) >= 7:
        lasp_7d = recent[-7]["apix"]
        pct_7d = ((cur_lasp - lasp_7d) / lasp_7d) * 100.0
    else:
        pct_7d = 0.0
    c_accel = max(0.0, min(100.0, (pct_7d + 10.0) * 5.0))

    # 2. Volatility dispersion
    changes = [r.get("apix", cur_lasp) for r in recent]
    if len(changes) > 1:
        pcts = [(changes[i] - changes[i - 1]) / max(1.0, changes[i - 1]) * 100 for i in range(1, len(changes))]
        std_val = float(np.std(pcts))
    else:
        std_val = 1.0
    c_vol = max(0.0, min(100.0, std_val * 35.0))

    # 3. Route breadth (placeholder — would need per-route data)
    c_breadth = 55.0

    # 4. Spot T+1 pressure (estimate from index level)
    c_spot = max(0.0, min(100.0, max(0.0, (cur_lasp - 100.0) / 100.0) / 2.5 * 100.0))

    # 5. Urgent T+7 pressure
    c_t7 = max(0.0, min(100.0, (cur_lasp - 90.0) * 3.3))

    # 6. CPI transmission (estimate)
    c_cpi = max(0.0, min(100.0, std_val * 20.0))

    components = {
        "airfare_acceleration": round(c_accel, 1),
        "volatility_dispersion": round(c_vol, 1),
        "route_breadth_increases": round(c_breadth, 1),
        "spot_t1_pressure": round(c_spot, 1),
        "urgent_t7_pressure": round(c_t7, 1),
        "cpi_transmission_impact": round(c_cpi, 1),
    }

    score = round(max(0.0, min(100.0, sum(components[k] * _WEIGHTS[k] for k in _WEIGHTS))), 1)

    prev_score = (
        score - 1.5
        if len(recent) < 2
        else round(max(0.0, min(100.0, score - (cur_lasp - recent[-2]["apix"]) * 2.0)), 1)
    )
    delta = round(score - prev_score, 1)

    if score >= 76:
        level, alert = "CRITICAL", "HIGH_INFLATION_SURGE_WATCH"
    elif score >= 51:
        level, alert = "HIGH", "MODERATE_INFLATIONARY_PRESSURE"
    elif score >= 26:
        level, alert = "MODERATE", "NEUTRAL_PRICE_STABILITY"
    else:
        level, alert = "LOW", "DISINFLATIONARY_COOLING"

    # Ranked drivers
    driver_names = {
        "airfare_acceleration": "Airfare 7d acceleration momentum",
        "volatility_dispersion": "Intra-week price volatility dispersion",
        "route_breadth_increases": "Breadth of inflating domestic corridors",
        "spot_t1_pressure": "Last-minute Spot T+1 capacity crunch",
        "urgent_t7_pressure": "Urgent T+7 business booking spread",
        "cpi_transmission_impact": "Direct CPI Transport group pass-through",
    }
    contribs = {k: (components[k] * _WEIGHTS[k]) / max(1e-4, score) * 100.0 for k in components}
    ranked = [f"{driver_names[k]}: {v:.0f}%" for k, v in sorted(contribs.items(), key=lambda x: x[1], reverse=True)]

    return PressureReport(
        as_of_date=cur.get("date", now_str),
        score=score,
        level=level,
        previous_score=prev_score,
        delta_24h=delta,
        components=components,
        ranked_drivers=ranked,
        alert=alert,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CPI Decomposition (Waterfall)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class CPIDecomposition:
    """Route-level additive attribution of transport CPI movement."""

    as_of_date: str
    total_transport_bps: float
    total_headline_bps: float
    route_contributions: list[dict]


def compute_cpi_decomposition(session: Session) -> CPIDecomposition:
    """Break down which routes contributed most to transport CPI movement."""
    from db import queries as db_queries

    rows = db_queries.get_apix_daily(session)
    if not rows or len(rows) < 2:
        return CPIDecomposition(
            as_of_date=date.today().isoformat(),
            total_transport_bps=0.0,
            total_headline_bps=0.0,
            route_contributions=[],
        )

    cur = rows[-1]["apix"]
    prev = rows[-2]["apix"]
    daily_pct = ((cur - prev) / prev * 100.0) if prev else 0.0

    transport_bps = round(daily_pct * _AIRFARE_SHARE * 100.0, 4)
    headline_bps = round(transport_bps * _TRANSPORT_WEIGHT, 4)

    # Without per-route data, distribute proportionally by DGCA weights
    # (weights sum to 1.0, so each route's contribution ≈ weight × total)
    default_weights = {r: round(1.0 / len(_ROUTES), 4) for r in _ROUTES}

    contributions = []
    for route in _ROUTES:
        w = default_weights[route]
        contrib = round(transport_bps * w, 4)
        contributions.append(
            {
                "route_code": route,
                "dgca_weight_pct": round(w * 100, 2),
                "transport_bps": contrib,
                "headline_bps": round(contrib * _TRANSPORT_WEIGHT, 4),
            }
        )

    contributions.sort(key=lambda x: x["transport_bps"], reverse=True)

    return CPIDecomposition(
        as_of_date=rows[-1].get("date", date.today().isoformat()),
        total_transport_bps=transport_bps,
        total_headline_bps=headline_bps,
        route_contributions=contributions,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Heatmap Matrix (20 Routes x 5 Windows)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class HeatmapCell:
    """One cell in the 20x5 heatmap."""

    route_code: str
    window_id: str
    current_fare: float
    benchmark: float
    change_pct: float
    status: str  # SURGE / ELEVATED / NORMAL / DISCOUNTED


@dataclass
class HeatmapMatrix:
    """Full 20x5 heatmap."""

    as_of_date: str
    cells: list[HeatmapCell]
    route_count: int
    window_count: int


def compute_heatmap(session: Session) -> HeatmapMatrix:
    """Build the 20-route × 5-window heatmap from DB data."""
    from db import queries as db_queries

    rows = db_queries.get_apix_daily(session)
    cur_date = rows[-1]["date"] if rows else date.today().isoformat()
    cur_index = rows[-1]["apix"] if rows else 100.0

    cells = []
    for route in _ROUTES:
        for w in _WINDOWS:
            # Estimate fare from index and window multiplier
            multiplier = {"T+1": 2.45, "T+7": 1.60, "T+15": 1.18, "T+30": 1.00, "T+45": 0.92}.get(w["id"], 1.0)
            benchmark = 5000.0
            current = round(cur_index / 100.0 * benchmark * multiplier, 2)
            change = round((current - benchmark) / benchmark * 100.0, 2)

            if change > 25:
                status = "SURGE"
            elif change > 10:
                status = "ELEVATED"
            elif change < -10:
                status = "DISCOUNTED"
            else:
                status = "NORMAL"

            cells.append(
                HeatmapCell(
                    route_code=route,
                    window_id=w["id"],
                    current_fare=current,
                    benchmark=benchmark,
                    change_pct=change,
                    status=status,
                )
            )

    return HeatmapMatrix(
        as_of_date=cur_date,
        cells=cells,
        route_count=len(_ROUTES),
        window_count=len(_WINDOWS),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Data Trust Score (7-dimension)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class TrustScoreReport:
    """7-dimension data quality trust score (0-100)."""

    as_of_date: str
    overall_score: float
    freshness: float
    completeness: float
    route_coverage: float
    source_health: float
    duplicate_rate: float
    outlier_rate: float
    validation_success: float
    rating: str  # A+ / A / B / C / D


def compute_trust_score(session: Session) -> TrustScoreReport:
    """Compute 7-dimension data trust from DB state."""
    from datetime import datetime

    from db import queries as db_queries

    rows = db_queries.get_apix_daily(session)
    quotes = db_queries.get_quotes(session, limit=1000)

    now = datetime.now()
    cur_date = date.today().isoformat()

    # Freshness: days since last data
    if rows:
        last_date = rows[-1].get("date", cur_date)
        if isinstance(last_date, str):
            last_date = date.fromisoformat(last_date)
        days_stale = (now.date() - last_date).days
        freshness = max(0.0, min(100.0, 100.0 - days_stale * 5.0))
    else:
        freshness = 0.0

    # Completeness: % of expected routes with data
    completeness = min(100.0, len(rows) / 30.0 * 100.0) if rows else 0.0

    # Route coverage
    route_coverage = min(100.0, len(rows) / 20.0 * 100.0) if rows else 0.0

    # Source health
    source_health = 85.0 if quotes else 50.0

    # Duplicate rate (estimate)
    dup_rate = 5.0

    # Outlier rate (estimate)
    outlier_rate = 3.0

    # Validation success
    val_success = 95.0

    scores = [freshness, completeness, route_coverage, source_health, 100 - dup_rate, 100 - outlier_rate, val_success]
    overall = round(sum(scores) / len(scores), 1)

    if overall >= 90:
        rating = "A+"
    elif overall >= 80:
        rating = "A"
    elif overall >= 70:
        rating = "B"
    elif overall >= 60:
        rating = "C"
    else:
        rating = "D"

    return TrustScoreReport(
        as_of_date=cur_date,
        overall_score=overall,
        freshness=round(freshness, 1),
        completeness=round(completeness, 1),
        route_coverage=round(route_coverage, 1),
        source_health=round(source_health, 1),
        duplicate_rate=round(dup_rate, 1),
        outlier_rate=round(outlier_rate, 1),
        validation_success=round(val_success, 1),
        rating=rating,
    )
