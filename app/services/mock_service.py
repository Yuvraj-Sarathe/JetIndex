"""Mock service — serves data from data/mock/ when MOCK_MODE=true."""

import json
from datetime import date
from pathlib import Path

MOCK_DIR = Path(__file__).resolve().parents[2] / "data" / "mock"


def _load_mock(filename: str) -> list | dict:
    """Load a mock JSON file from data/mock/."""
    filepath = MOCK_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath) as f:
        return json.load(f)


def get_mock_apix_daily(
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Return daily APIx mock data, optionally filtered by date range."""
    data = _load_mock("apix_daily.json")
    if isinstance(data, list):
        if from_date:
            data = [d for d in data if d.get("date", "") >= from_date.isoformat()]
        if to_date:
            data = [d for d in data if d.get("date", "") <= to_date.isoformat()]
    return data if isinstance(data, list) else []


def get_mock_apix_weekly(
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Return weekly rolled-up APIx mock data."""
    # TODO: aggregate daily data or serve from mock file
    return get_mock_apix_daily(from_date, to_date)


def get_mock_apix_monthly(
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Return monthly rolled-up APIx mock data."""
    # TODO: aggregate daily data or serve from mock file
    return get_mock_apix_daily(from_date, to_date)


def get_mock_routes() -> list[dict]:
    """Return the route basket mock data."""
    data = _load_mock("heatmap.json")
    if isinstance(data, list):
        return data
    return []


def get_mock_heatmap(route_date: date | None = None) -> list[dict]:
    """Return heatmap mock data."""
    data = _load_mock("heatmap.json")
    if isinstance(data, list):
        if route_date:
            # Filter by date if present in data
            pass  # mock data doesn't have date field, return all
        return data
    return []


def get_mock_elasticity(
    route_id: int | None = None,
    route_date: date | None = None,
) -> list[dict]:
    """Return elasticity mock data."""
    data = _load_mock("elasticity.json")
    if isinstance(data, list):
        return data
    return []


def get_mock_quotes(
    route_id: int | None = None,
    route_date: date | None = None,
    lead_time: int | None = None,
    carrier: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Return clean quotes mock data."""
    data = _load_mock("fare_quotes.json")
    if isinstance(data, list):
        result = data[:limit]
        return result
    return []


def get_mock_backtest() -> dict:
    """Return backtest mock data with summary."""
    data = _load_mock("backtest.json")
    if isinstance(data, dict):
        return data
    return {"monthly": [], "summary": {"mape": 0.0, "rmse": 0.0, "corr": 0.0}}


def get_mock_scraped_vs_dgca() -> list[dict]:
    """Return scraped vs DGCA comparison mock data."""
    data = _load_mock("scraped_vs_dgca.json")
    if isinstance(data, list):
        return data
    return []
