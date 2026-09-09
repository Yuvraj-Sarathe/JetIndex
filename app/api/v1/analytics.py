"""Analytics API endpoints — pressure score, CPI decomposition, CPI impact."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/pressure")
def get_pressure_score(
    target_date: str | None = Query(None),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Airfare Inflation Pressure Score (AIPS) — 0-100 composite for RBI MPC."""
    if settings.MOCK_MODE:
        return _mock_pressure_score()
    from engine.analytics import compute_pressure_score

    report = compute_pressure_score(db, target_date=target_date)
    from dataclasses import asdict

    return asdict(report)


@router.get("/cpi-decomposition")
def get_cpi_decomposition(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Route-level CPI contribution waterfall."""
    if settings.MOCK_MODE:
        return _mock_cpi_decomposition()
    from engine.analytics import compute_cpi_decomposition

    report = compute_cpi_decomposition(db)
    from dataclasses import asdict

    return asdict(report)


@router.get("/cpi-impact")
def get_cpi_impact(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Macro CPI transmission sensitivity matrix."""
    if settings.MOCK_MODE:
        return _mock_cpi_impact()
    # Would compute actual shock scenarios
    return _mock_cpi_impact()


def _mock_pressure_score() -> dict:
    """Mock pressure score data."""
    return {
        "as_of_date": date.today().isoformat(),
        "score": 62.5,
        "level": "MODERATE",
        "previous_score": 58.3,
        "delta_24h": 4.2,
        "components": {
            "airfare_acceleration": 65.0,
            "volatility_dispersion": 55.0,
            "route_breadth_increases": 60.0,
            "spot_t1_pressure": 70.0,
            "urgent_t7_pressure": 55.0,
            "cpi_transmission_impact": 68.0,
        },
        "ranked_drivers": [
            "Last-minute Spot T+1 capacity crunch: 22%",
            "Direct CPI Transport group pass-through: 22%",
            "Airfare 7d acceleration momentum: 26%",
        ],
        "alert": "MODERATE_INFLATIONARY_PRESSURE",
        "data_tag": "MOCK_DATA",
    }


def _mock_cpi_decomposition() -> dict:
    """Mock CPI decomposition data."""
    return {
        "as_of_date": date.today().isoformat(),
        "total_transport_bps": 0.85,
        "total_headline_bps": 0.073,
        "route_contributions": [
            {"route_code": "DEL-BOM", "dgca_weight_pct": 10.92, "transport_bps": 0.093, "headline_bps": 0.008},
            {"route_code": "DEL-BLR", "dgca_weight_pct": 8.05, "transport_bps": 0.068, "headline_bps": 0.006},
            {"route_code": "BOM-BLR", "dgca_weight_pct": 5.84, "transport_bps": 0.050, "headline_bps": 0.004},
        ],
        "data_tag": "MOCK_DATA",
    }


def _mock_cpi_impact() -> dict:
    """Mock CPI impact data."""
    return {
        "current_airfare_index": 105.5,
        "weights_structure": {
            "cpi_transport_and_communication_weight": 0.0859,
            "airfare_share_in_transport": 0.0385,
            "effective_headline_weight": 0.003307,
        },
        "sensitivity_stress_matrix": [
            {
                "airfare_swing_pct": -20.0,
                "transport_subgroup_impact_bps": -7.7,
                "headline_cpi_impact_bps": -0.6614,
                "monetary_policy_significance": "High",
            },
            {
                "airfare_swing_pct": -10.0,
                "transport_subgroup_impact_bps": -3.85,
                "headline_cpi_impact_bps": -0.3307,
                "monetary_policy_significance": "Moderate",
            },
            {
                "airfare_swing_pct": 10.0,
                "transport_subgroup_impact_bps": 3.85,
                "headline_cpi_impact_bps": 0.3307,
                "monetary_policy_significance": "Moderate",
            },
            {
                "airfare_swing_pct": 20.0,
                "transport_subgroup_impact_bps": 7.7,
                "headline_cpi_impact_bps": 0.6614,
                "monetary_policy_significance": "High",
            },
            {
                "airfare_swing_pct": 30.0,
                "transport_subgroup_impact_bps": 11.55,
                "headline_cpi_impact_bps": 0.9921,
                "monetary_policy_significance": "High",
            },
        ],
        "data_tag": "MOCK_DATA",
    }
