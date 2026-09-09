"""Temporal Dynamics - Seasonal & Booking Window Patterns API."""

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/temporal")
def get_temporal_dynamics(
    _token: str = Depends(require_token),
) -> dict:
    """Returns temporal patterns: day-of-week multipliers, advance yield curve, seasonal factors."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "day_of_week_multipliers": {
                "Monday": 1.05,
                "Tuesday": 0.98,
                "Wednesday": 0.96,
                "Thursday": 1.02,
                "Friday": 1.12,
                "Saturday": 1.08,
                "Sunday": 1.03,
            },
            "advance_yield_curve": {
                "T+1": 1.35,
                "T+7": 1.08,
                "T+15": 0.95,
                "T+30": 0.88,
                "T+45": 0.82,
            },
            "seasonal_factors": {"peak_factor": 1.15, "off_peak_factor": 0.92},
        }
    try:
        from engine.analytics.temporal import get_temporal_analytics

        return {"data_tag": "REAL_COMPUTED", **get_temporal_analytics()}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
