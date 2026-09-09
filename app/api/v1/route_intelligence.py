"""Route Intelligence - 360-Degree Route Dossier API."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/{route_code}")
def get_route_dossier(
    route_code: str,
    _token: str = Depends(require_token),
) -> dict:
    """Returns complete intelligence dossier for a specific DGCA route corridor."""
    if settings.MOCK_MODE:
        return {
            "route_code": route_code.upper(),
            "data_tag": "MOCK_DATA",
            "corridor_intelligence": {
                "origin_city": "New Delhi", "destination_city": "Mumbai",
                "market_positioning": {"dgca_volume_weight_pct": 10.92},
                "advance_booking_windows": {
                    "T+1": {"window": "T+1", "current_jevons_fare": 6850.0, "base_benchmark_fare": 5200.0, "price_relative": 1.317},
                    "T+7": {"window": "T+7", "current_jevons_fare": 5450.0, "base_benchmark_fare": 5200.0, "price_relative": 1.048},
                    "T+30": {"window": "T+30", "current_jevons_fare": 4750.0, "base_benchmark_fare": 5200.0, "price_relative": 0.913},
                },
            },
        }
    try:
        from engine.analytics.route_intelligence import get_route_intelligence
        return get_route_intelligence(route_code.upper())
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
