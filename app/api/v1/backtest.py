"""Backtest endpoint — APIx vs DGCA benchmark."""

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from app.services.mock_service import get_mock_backtest

router = APIRouter()


@router.get("")
def get_backtest(
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Return backtest results: APIx (rebased) vs DGCA monthly avg + summary stats."""
    if settings.MOCK_MODE:
        return get_mock_backtest()
    from engine.backtest import run_backtest

    result = run_backtest(db)
    return result
