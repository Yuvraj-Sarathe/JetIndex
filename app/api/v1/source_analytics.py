"""Source Analytics - Carrier & OTA Analytics API."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/carriers")
def get_carrier_analytics(
    _token: str = Depends(require_token),
) -> dict:
    """Returns per-carrier pricing analytics and market share."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "carriers": [
                {"carrier_name": "IndiGo", "median_fare": 5200.0, "avg_fare": 5480.0, "market_share_pct": 42.0, "volatility_index": 18.5},
                {"carrier_name": "Vistara", "median_fare": 5850.0, "avg_fare": 6100.0, "market_share_pct": 21.0, "volatility_index": 22.3},
                {"carrier_name": "Air India", "median_fare": 5400.0, "avg_fare": 5650.0, "market_share_pct": 18.0, "volatility_index": 19.8},
            ],
        }
    try:
        from engine.analytics.source_analytics import SourceAnalyticsEngine
        engine = SourceAnalyticsEngine()
        result = engine.get_analytics()
        return {"data_tag": "REAL_COMPUTED", "carriers": result.get("carriers", [])}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}


@router.get("/otas")
def get_ota_analytics(
    _token: str = Depends(require_token),
) -> dict:
    """Returns per-OTA pricing analytics."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "otas": [
                {"source_portal": "Makemytrip", "median_fare": 5350.0, "market_share_pct": 35.0},
                {"source_portal": "Goibibo", "median_fare": 5280.0, "market_share_pct": 25.0},
                {"source_portal": "Airline Website", "median_fare": 5200.0, "market_share_pct": 30.0},
            ],
        }
    try:
        from engine.analytics.source_analytics import SourceAnalyticsEngine
        engine = SourceAnalyticsEngine()
        result = engine.get_analytics()
        return {"data_tag": "REAL_COMPUTED", "otas": result.get("otas", [])}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
