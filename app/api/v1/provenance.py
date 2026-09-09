"""Provenance Trace & Audit Trail API."""

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("/quote/{quote_id}")
def trace_quote(
    quote_id: str,
    _token: str = Depends(require_token),
) -> dict:
    """Traces a single quote through the full cleaning and aggregation lifecycle."""
    if settings.MOCK_MODE:
        return {
            "quote_id": quote_id,
            "data_tag": "MOCK_DATA",
            "provenance": {
                "route_code": "DEL-BOM", "carrier": "IndiGo", "total_fare": 5400.0,
                "cleaning_status": "CLEANED_VALID", "outlier_flag": 0,
                "sha256_hash": "a1b2c3...", "validation_status": "SCHEMA_VALIDATED",
            },
        }
    try:
        from engine.provenance.tracer import get_quote_trace
        record = get_quote_trace(quote_id)
        if record is None:
            return {"error": f"Quote {quote_id} not found", "data_tag": "NOT_FOUND"}
        from dataclasses import asdict
        return {"data_tag": "REAL_COMPUTED", "provenance": asdict(record)}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}


@router.get("/cell-drilldown")
def cell_drilldown(
    route_code: str = Query("DEL-BOM"),
    advance_window: str = Query("T+7"),
    calculation_date: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    _token: str = Depends(require_token),
) -> dict:
    """Drills down from an aggregate route-window index cell to all contributing underlying quotes."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "cell_hierarchy": {
                "calculation_date": calculation_date or "2026-08-26",
                "route_code": route_code.upper(),
                "advance_window": advance_window.upper(),
                "jevons_mean_fare": 5450.0,
                "base_benchmark_fare": 5200.0,
                "sample_size_evaluated": 3,
            },
            "quotes": [
                {"quote_id": "Q-001", "flight_number": "6E-234", "carrier": "IndiGo", "base_fare": 4500.0, "total_fare": 5400.0},
                {"quote_id": "Q-002", "flight_number": "UK-955", "carrier": "Vistara", "base_fare": 4800.0, "total_fare": 5850.0},
                {"quote_id": "Q-003", "flight_number": "AI-865", "carrier": "Air India", "base_fare": 4650.0, "total_fare": 5580.0},
            ],
        }
    try:
        from engine.provenance.tracer import get_cell_drilldown
        return get_cell_drilldown(
            calculation_date or "2026-08-26",
            route_code.upper(),
            advance_window.upper(),
            limit=limit,
        )
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
