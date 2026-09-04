"""Elasticity endpoint — fare by lead time."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.security import require_token
from app.services.mock_service import get_mock_elasticity

router = APIRouter()


@router.get("")
async def get_elasticity(
    route_id: int | None = Query(None),
    route_date: date | None = Query(None),
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return lead-time elasticity matrix: fare vs lead time per route."""
    # TODO: implement real engine query when MOCK_MODE=false
    return get_mock_elasticity(route_id, route_date)
