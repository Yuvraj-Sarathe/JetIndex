"""APIx index endpoints — daily, weekly, monthly."""

from datetime import date

from fastapi import APIRouter, Depends

from app.core.security import require_token
from app.services.mock_service import (
    get_mock_apix_daily,
    get_mock_apix_monthly,
    get_mock_apix_weekly,
)

router = APIRouter()


@router.get("/daily")
async def get_apix_daily(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return daily APIx index values."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_apix_daily(from_date, to_date)


@router.get("/weekly")
async def get_apix_weekly(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return weekly rolled-up APIx values."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_apix_weekly(from_date, to_date)


@router.get("/monthly")
async def get_apix_monthly(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
) -> list[dict]:
    """Return monthly rolled-up APIx values."""
    # TODO: implement real DB query when MOCK_MODE=false
    return get_mock_apix_monthly(from_date, to_date)
