"""Elasticity endpoint — fare by lead time."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from app.services.mock_service import get_mock_elasticity
from db.queries import get_elasticity_data as db_get_elasticity_data

router = APIRouter()


@router.get("")
def get_elasticity(
    route_id: int | None = Query(None),
    route_date: date | None = Query(None),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return lead-time elasticity matrix: fare vs lead time per route."""
    if settings.MOCK_MODE:
        return get_mock_elasticity(route_id, route_date)
    if route_id is None:
        return []
    return db_get_elasticity_data(db, route_id, route_date)
