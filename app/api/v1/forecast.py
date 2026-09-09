"""Forecast API endpoints — national and route-specific forecasts."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token
from engine.forecasting import generate_nowcast

router = APIRouter()


@router.get("/national")
def get_national_forecast(
    horizon_days: int = Query(14, ge=1, le=60, description="Forward horizon in days"),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """National airfare index forecast with 95% confidence intervals."""
    if settings.MOCK_MODE:
        return _mock_national_forecast(horizon_days)
    try:
        report = generate_nowcast(db, horizon_days=horizon_days)
        from dataclasses import asdict

        return asdict(report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/route/{route_code}")
def get_route_forecast(
    route_code: str,
    horizon_days: int = Query(14, ge=1, le=60),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Route-specific forward price forecast."""
    if settings.MOCK_MODE:
        return _mock_route_forecast(route_code, horizon_days)
    # For now, use national forecast as placeholder
    try:
        report = generate_nowcast(db, horizon_days=horizon_days)
        from dataclasses import asdict

        result = asdict(report)
        result["route_code"] = route_code.upper()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _mock_national_forecast(horizon_days: int) -> dict:
    """Mock national forecast data."""
    from datetime import date, timedelta

    today = date.today()
    steps = []
    base_index = 105.5
    for i in range(1, horizon_days + 1):
        forecast_date = today + timedelta(days=i)
        predicted = base_index + (i * 0.15)
        ci_width = 1.2 + (i * 0.08)
        steps.append(
            {
                "forecast_date": forecast_date.isoformat(),
                "horizon_days": i,
                "predicted_index": round(predicted, 2),
                "ci_lower_95": round(predicted - ci_width, 2),
                "ci_upper_95": round(predicted + ci_width, 2),
                "daily_change_pct": round(0.15, 4),
                "transport_bps": round(0.058, 4),
                "headline_bps": round(0.005, 4),
            }
        )
    return {
        "as_of_date": today.isoformat(),
        "current_index": base_index,
        "horizon_days": horizon_days,
        "mean_forecast": round(base_index + (horizon_days * 0.15 / 2), 2),
        "net_transport_bps": round(horizon_days * 0.058, 2),
        "net_headline_bps": round(horizon_days * 0.005, 4),
        "alert_level": "NEUTRAL_PRICE_STABILITY",
        "steps": steps,
        "feature_importances": {"lag_1": 0.35, "rolling_mean_7d": 0.25, "momentum_7d": 0.15},
    }


def _mock_route_forecast(route_code: str, horizon_days: int) -> dict:
    """Mock route-specific forecast data."""
    result = _mock_national_forecast(horizon_days)
    result["route_code"] = route_code.upper()
    return result
