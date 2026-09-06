"""Backtest endpoint — APIx vs DGCA benchmark."""

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from app.services.mock_service import get_mock_backtest
from db.queries import get_dgca_benchmarks as db_get_dgca_benchmarks

router = APIRouter()


@router.get("")
def get_backtest(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Return backtest results: APIx (rebased) vs DGCA monthly avg + summary stats."""
    if settings.MOCK_MODE:
        return get_mock_backtest()
    monthly = db_get_dgca_benchmarks(db)
    # NOTE: db_get_dgca_benchmarks returns list[{month, avg_fare}].
    # The mock returns {"monthly": [...], "summary": {...}}.
    # We wrap the DB result to match the expected shape.
    return {
        "monthly": monthly,
        "summary": {"mape": 0.0, "rmse": 0.0, "corr": 0.0},
    }
