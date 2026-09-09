"""Cross-Portal Source Consensus API."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/consensus")
def get_source_consensus(
    route_code: str = Query("DEL-BOM"),
    _token: str = Depends(require_token),
) -> dict:
    """Returns cross-portal dispersion analysis and consensus scores."""
    if settings.MOCK_MODE:
        return {
            "route_code": route_code.upper(),
            "data_tag": "MOCK_DATA",
            "consensus_score": 95.0,
            "dispersion_pct": 2.1,
            "high_disagreement": False,
            "source_breakdown": [
                {"source_portal": "Makemytrip", "median_fare": 5350.0, "market_share_pct": 35.0},
                {"source_portal": "Goibibo", "median_fare": 5280.0, "market_share_pct": 25.0},
                {"source_portal": "Airline Website", "median_fare": 5200.0, "market_share_pct": 30.0},
            ],
        }
    try:
        from engine.analytics.source_consensus import SourceConsensusEngine
        engine = SourceConsensusEngine()
        result = engine.get_consensus_for_route(route_code.upper())
        return result
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
