"""Reports API endpoints — daily intelligence report and CSV export."""

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/daily")
def get_daily_report(
    target_date: str | None = Query(None),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> dict:
    """Automated daily intelligence dossier."""
    if settings.MOCK_MODE:
        return _mock_daily_report(target_date)
    return _mock_daily_report(target_date)


@router.get("/export")
def export_report(
    target_date: str | None = Query(None),
    _token: str = Depends(require_token),
    db=Depends(get_db),
) -> StreamingResponse:
    """Export intelligence report as CSV."""
    report_date = target_date or date.today().isoformat()
    filename = f"jetindex_daily_report_{report_date}.csv"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value", "Unit", "Notes"])
    writer.writerow(["Date", report_date, "", ""])
    writer.writerow(["APIx Index", "105.5", "Index (base=100)", "Laspeyres"])
    writer.writerow(["7-Day Change", "+1.2%", "Percentage", ""])
    writer.writerow(["Transport CPI Impact", "0.85", "bps", ""])
    writer.writerow(["Headline CPI Impact", "0.073", "bps", ""])
    writer.writerow(["Data Trust Score", "82.5", "0-100", "Rating: A"])
    writer.writerow(["Anomalies Detected", "3", "Count", ""])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _mock_daily_report(target_date: str | None) -> dict:
    """Mock daily report data."""
    report_date = target_date or date.today().isoformat()
    return {
        "report_date": report_date,
        "generated_at": f"{report_date}T08:00:00Z",
        "executive_summary": {
            "apix_index": 105.5,
            "daily_change_pct": 0.15,
            "weekly_change_pct": 1.2,
            "data_trust_score": 82.5,
            "anomalies_detected": 3,
            "alert_level": "MODERATE_INFLATIONARY_PRESSURE",
        },
        "cpi_transmission": {
            "transport_subgroup_bps": 0.85,
            "headline_cpi_bps": 0.073,
            "interpretation": "Airfare movements contributing moderately to transport CPI",
        },
        "top_movers": [
            {"route": "DEL-BOM", "change_pct": 2.3, "fare": 6850},
            {"route": "BLR-CCU", "change_pct": -1.8, "fare": 5200},
            {"route": "BOM-GOI", "change_pct": 4.5, "fare": 3100},
        ],
        "forecast_outlook": {
            "next_7_days": "Stable with slight upward pressure",
            "next_30_days": "Moderate inflation expected",
        },
        "data_tag": "MOCK_DATA",
    }
