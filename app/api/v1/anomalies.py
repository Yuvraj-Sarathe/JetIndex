"""Anomaly detection API endpoint."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("")
def get_anomalies(
    target_date: str | None = Query(None, description="Optional YYYY-MM-DD date"),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Detect unusual market behaviors: fare spikes, drops, corridor divergences."""
    if settings.MOCK_MODE:
        return _mock_anomalies(target_date)
    # Placeholder - would use actual anomaly detection engine
    return _mock_anomalies(target_date)


def _mock_anomalies(target_date: str | None) -> dict:
    """Mock anomaly data."""
    today = target_date or date.today().isoformat()
    anomalies = [
        {
            "anomaly_id": "ANO-001",
            "date": today,
            "route_code": "DEL-BOM",
            "type": "PRICE_SPIKE",
            "severity": "HIGH",
            "description": "T+1 fare 34% above 7-day rolling mean",
            "detected_value": 8950.0,
            "expected_range": [5800.0, 6800.0],
            "z_score": 3.8,
        },
        {
            "anomaly_id": "ANO-002",
            "date": today,
            "route_code": "BLR-CCU",
            "type": "HORIZON_INVERSION",
            "severity": "MEDIUM",
            "description": "T+30 fare higher than T+7 fare (inverted pricing)",
            "detected_value": 7200.0,
            "expected_range": [5000.0, 6000.0],
            "z_score": 2.4,
        },
        {
            "anomaly_id": "ANO-003",
            "date": today,
            "route_code": "BOM-GOI",
            "type": "PRICE_DROP",
            "severity": "LOW",
            "description": "Unusual 18% fare drop on Goa corridor",
            "detected_value": 2450.0,
            "expected_range": [2800.0, 3400.0],
            "z_score": -2.1,
        },
    ]
    return {
        "count": len(anomalies),
        "data_tag": "MOCK_DATA",
        "as_of_date": today,
        "anomalies": anomalies,
    }
