"""Backtest endpoint — APIx vs DGCA benchmark."""

from fastapi import APIRouter, Depends

from app.core.security import require_token
from app.services.mock_service import get_mock_backtest

router = APIRouter()


@router.get("")
async def get_backtest(
    _token: str = Depends(require_token),
) -> dict:
    """Return backtest results: APIx (rebased) vs DGCA monthly avg + summary stats."""
    # TODO: implement real engine backtest when MOCK_MODE=false
    return get_mock_backtest()
