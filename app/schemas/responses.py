"""API response Pydantic models."""

from datetime import date, datetime

from pydantic import BaseModel


class ApixDailyResponse(BaseModel):
    """Single daily APIx index value."""

    date: date
    apix: float
    pct_change_dod: float | None = None
    n_quotes: int


class RouteResponse(BaseModel):
    """Route basket entry with weight."""

    id: int
    route_code: str
    origin: str
    destination: str
    o_lat: float
    o_lon: float
    d_lat: float
    d_lon: float
    weight: float
    active: bool


class HeatmapResponse(BaseModel):
    """Per-route heatmap data."""

    route_id: int
    origin: str
    dest: str
    o_lat: float
    o_lon: float
    d_lat: float
    d_lon: float
    avg_fare: float
    volatility: float
    index_contrib: float


class ElasticityResponse(BaseModel):
    """Lead-time elasticity entry."""

    lead_time: int
    avg_total_fare: float
    avg_base_fare: float
    n: int


class QuoteResponse(BaseModel):
    """Clean quote with unbundled fare components."""

    route_code: str
    carrier: str
    flight_no: str
    depart_date: date
    lead_time: int
    fare_class: str | None
    base_fare: float
    udf: float
    taxes: float
    convenience_fee: float
    other_fees: float
    total_fare: float
    source: str
    scraped_at: datetime


class BacktestSummary(BaseModel):
    """Backtest summary statistics."""

    mape: float
    rmse: float
    corr: float


class BacktestResponse(BaseModel):
    """Full backtest response with monthly data and summary."""

    monthly: list[dict]
    summary: BacktestSummary
