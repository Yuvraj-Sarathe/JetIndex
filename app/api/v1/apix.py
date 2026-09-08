"""APIx index endpoints — daily, weekly, monthly, scraped-vs-dgca."""

from datetime import date

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from app.services.mock_service import (
    get_mock_apix_daily,
    get_mock_apix_monthly,
    get_mock_apix_weekly,
)
from db.queries import get_apix_daily as db_get_apix_daily
from db.queries import get_apix_monthly as db_get_apix_monthly
from db.queries import get_apix_weekly as db_get_apix_weekly
from db.queries import get_scraped_vs_dgca as db_get_scraped_vs_dgca

router = APIRouter()


@router.get("/daily")
def get_apix_daily(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return daily APIx index values."""
    if settings.MOCK_MODE:
        return get_mock_apix_daily(from_date, to_date)
    return db_get_apix_daily(db, from_date, to_date)


@router.get("/weekly")
def get_apix_weekly(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return weekly rolled-up APIx values."""
    if settings.MOCK_MODE:
        return get_mock_apix_weekly(from_date, to_date)
    return db_get_apix_weekly(db, from_date, to_date)


@router.get("/monthly")
def get_apix_monthly(
    from_date: date | None = None,
    to_date: date | None = None,
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Return monthly rolled-up APIx values."""
    if settings.MOCK_MODE:
        return get_mock_apix_monthly(from_date, to_date)
    return db_get_apix_monthly(db, from_date, to_date)


@router.get("/scraped-vs-dgca")
def get_scraped_vs_dgca(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> list[dict]:
    """Monthly comparison: avg scraped fare vs DGCA benchmark."""
    return db_get_scraped_vs_dgca(db)
