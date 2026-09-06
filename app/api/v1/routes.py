"""Routes endpoints — basket info and heatmap data."""

from datetime import date

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from app.services.mock_service import get_mock_heatmap, get_mock_routes
from db.queries import get_active_routes as db_get_active_routes
from db.queries import get_heatmap_data as db_get_heatmap_data

router = APIRouter()


@router.get("")
def get_routes(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return the DGCA sector basket with weights."""
    if settings.MOCK_MODE:
        return get_mock_routes()
    rows = db_get_active_routes(db)
    return [
        {
            "route_code": r.route_code,
            "origin": r.origin,
            "destination": r.destination,
            "o_lat": r.o_lat,
            "o_lon": r.o_lon,
            "d_lat": r.d_lat,
            "d_lon": r.d_lon,
            "active": r.active,
        }
        for r in rows
    ]


@router.get("/heatmap")
def get_routes_heatmap(
    route_date: date | None = None,
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return per-route avg fare, volatility, and lat/lon for heatmap."""
    if settings.MOCK_MODE:
        return get_mock_heatmap(route_date)
    return db_get_heatmap_data(db, route_date)
