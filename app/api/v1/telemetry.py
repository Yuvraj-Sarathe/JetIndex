"""Dashboard Telemetry & System Health API."""

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("")
def get_telemetry(
    _token: str = Depends(require_token),
) -> dict:
    """Returns dashboard telemetry: collection status, freshness, route movements."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "collection_status": {"last_run": "2026-08-26T08:00:00Z", "status": "SUCCESS", "quotes_scraped": 2480},
            "data_freshness": {"age_hours": 2.5},
            "top_route_movements": [
                {"route_code": "DEL-BOM", "movement_bps": 45.2},
                {"route_code": "DEL-BLR", "movement_bps": -12.8},
            ],
        }
    try:
        from engine.analytics.source_telemetry import get_source_telemetry
        return {"data_tag": "REAL_COMPUTED", **get_source_telemetry()}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
