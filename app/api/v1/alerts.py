"""Alert Rules & Live Threat Feed API endpoints."""

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/rules")
def get_alert_rules(
    _token: str = Depends(require_token),
) -> dict:
    """Returns all configurable alert rule definitions."""
    if settings.MOCK_MODE:
        return {
            "count": 3,
            "data_tag": "MOCK_DATA",
            "rules": [
                {
                    "rule_id": "RULE-001",
                    "rule_name": "Critical Fare Spike",
                    "metric_target": "DEL-BOM.daily_pct_change",
                    "condition": ">=",
                    "threshold": 12.0,
                    "severity": "CRITICAL",
                    "is_enabled": True,
                },
                {
                    "rule_id": "RULE-002",
                    "rule_name": "Market Pressure Alert",
                    "metric_target": "composite_apix_pressure_score",
                    "condition": ">=",
                    "threshold": 85.0,
                    "severity": "CRITICAL",
                    "is_enabled": True,
                },
                {
                    "rule_id": "RULE-003",
                    "rule_name": "Data Staleness Warning",
                    "metric_target": "data_freshness_hours",
                    "condition": ">=",
                    "threshold": 48.0,
                    "severity": "HIGH",
                    "is_enabled": True,
                },
            ],
        }
    try:
        from engine.alerts.engine import get_all_active_rules

        rules = get_all_active_rules()
        return {"count": len(rules), "data_tag": "REAL_COMPUTED", "rules": rules}
    except Exception:
        return {"count": 0, "data_tag": "ERROR", "rules": []}


@router.get("/live")
def get_live_threat_feed(
    limit: int = Query(20, ge=1, le=100),
    _token: str = Depends(require_token),
) -> dict:
    """Returns live triggered alerts feed."""
    if settings.MOCK_MODE:
        return {
            "count": 2,
            "data_tag": "MOCK_DATA",
            "alerts": [
                {
                    "alert_id": "ALT-20260826-001",
                    "title": "CRITICAL: Fare Spike DETECTED on DEL-BOM",
                    "severity": "CRITICAL",
                    "status": "ACTIVE",
                    "triggered_at": "2026-08-26T10:15:00Z",
                },
                {
                    "alert_id": "ALT-20260826-002",
                    "title": "HIGH: Rapid Inflation Surge DETECTED on DEL-MAA",
                    "severity": "HIGH",
                    "status": "ACK",
                    "triggered_at": "2026-08-26T09:45:00Z",
                },
            ],
        }
    try:
        from engine.alerts.engine import get_recent_alerts

        alerts = get_recent_alerts(limit=limit)
        return {"count": len(alerts), "data_tag": "REAL_COMPUTED", "alerts": alerts}
    except Exception:
        return {"count": 0, "data_tag": "ERROR", "alerts": []}
