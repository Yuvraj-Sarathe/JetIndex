"""Routes endpoints — basket info and heatmap data."""

from datetime import date

from fastapi import APIRouter, Depends

from app.core.security import require_token
from app.services.mock_service import get_mock_heatmap, get_mock_routes

router = APIRouter()


@router.get("")
async def get_routes(
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return the DGCA sector basket with weights."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_routes()


@router.get("/heatmap")
async def get_routes_heatmap(
    route_date: date | None = None,
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return per-route avg fare, volatility, and lat/lon for heatmap."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_heatmap(route_date)
