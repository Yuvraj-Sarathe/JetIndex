"""Quotes inspector endpoint — raw and clean quotes."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.security import require_token
from app.services.mock_service import get_mock_quotes

router = APIRouter()


@router.get("")
async def get_quotes(
    route_id: int | None = Query(None),
    route_date: date | None = Query(None),
    lead_time: int | None = Query(None),
    carrier: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return clean quotes with unbundled fare components."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_quotes(route_id, route_date, lead_time, carrier, limit)
