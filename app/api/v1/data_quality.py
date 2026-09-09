"""Data quality API endpoint — 7-dimension trust score."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("")
def get_data_quality(
    target_date: str | None = Query(None, description="Optional YYYY-MM-DD date"),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Returns composite Data Trust Score (0-100) and 7 quality dimensions."""
    if settings.MOCK_MODE:
        return _mock_data_quality(target_date)
    # Use actual engine
    from engine.analytics import compute_trust_score
    report = compute_trust_score(db)
    from dataclasses import asdict
    return asdict(report)


def _mock_data_quality(target_date: str | None) -> dict:
    """Mock data quality report."""
    return {
        "as_of_date": target_date or date.today().isoformat(),
        "overall_score": 82.5,
        "freshness": 85.0,
        "completeness": 90.0,
        "route_coverage": 78.0,
        "source_health": 85.0,
        "duplicate_rate": 5.0,
        "outlier_rate": 3.0,
        "validation_success": 95.0,
        "rating": "A",
        "data_tag": "MOCK_DATA",
    }
