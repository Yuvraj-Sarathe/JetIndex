"""
JetIndex - Pressure Score, CPI Decomposition & Heatmap API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# ===== Pressure Score Endpoints =====


class PressureScoreResponse(BaseModel):
    as_of_date: str
    pressure_score: float
    pressure_level: str
    previous_score: float
    score_change_24h: float
    components: dict[str, float]
    component_weights: dict[str, float]
    ranked_drivers: list[str]
    rbi_monetary_policy_alert: str
    data_tag: str
    generated_at: str


@router.get("/pressure-score", response_model=PressureScoreResponse)
async def get_pressure_score(target_date: str | None = Query(None)):
    """Get the Airfare Inflation Pressure Score (AIPS)."""
    from app.core.config import settings

    if settings.MOCK_MODE:
        return PressureScoreResponse(
            as_of_date=target_date or "2026-07-21",
            pressure_score=4.5,
            pressure_level="moderate",
            previous_score=4.2,
            score_change_24h=0.3,
            components={
                "passthrough_lag": 0.32,
                "fuel_impact": 0.18,
                "demand_surge": 0.12,
                "capacity_utilization": 0.15,
                "seasonal_adjustment": 0.08,
                "cross_route_substitution": 0.15,
            },
            component_weights={
                "passthrough_lag": 0.30,
                "fuel_impact": 0.25,
                "demand_surge": 0.20,
                "capacity_utilization": 0.10,
                "seasonal_adjustment": 0.10,
                "cross_route_substitution": 0.05,
            },
            ranked_drivers=["passthrough_lag", "fuel_impact", "demand_surge"],
            rbi_monetary_policy_alert="FAIR",
            data_tag="synthetic",
            generated_at="2026-07-21T12:00:00",
        )
    try:
        from engine.analytics.pressure_score import get_inflation_pressure_score

        report = get_inflation_pressure_score(target_date=target_date)
        return PressureScoreResponse(
            as_of_date=report.as_of_date,
            pressure_score=report.pressure_score,
            pressure_level=report.pressure_level,
            previous_score=report.previous_score,
            score_change_24h=report.score_change_24h,
            components=report.components,
            component_weights=report.component_weights,
            ranked_drivers=report.ranked_drivers,
            rbi_monetary_policy_alert=report.rbi_monetary_policy_alert,
            data_tag=report.data_tag,
            generated_at=report.generated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pressure score failed: {e}") from e


# ===== CPI Decomposition Endpoints =====


class RouteCPIContributionResponse(BaseModel):
    rank: int
    route_code: str
    corridor_name: str
    route_weight_pct: float
    price_movement_pct: float
    transport_subgroup_impact_bps: float
    headline_cpi_impact_bps: float
    share_of_total_inflation_pct: float
    cumulative_headline_bps: float
    contribution_direction: str


class CPIDecompositionResponse(BaseModel):
    calculation_date: str
    total_transport_impact_bps: float
    total_headline_cpi_impact_bps: float
    top_positive_contributors: list[RouteCPIContributionResponse]
    top_negative_contributors: list[RouteCPIContributionResponse]
    full_route_waterfall: list[RouteCPIContributionResponse]
    methodology_summary: str
    generated_at: str


@router.get("/cpi-decomposition", response_model=CPIDecompositionResponse)
async def get_cpi_decomposition(target_date: str | None = Query(None)):
    """Get CPI impact decomposition by route."""
    from app.core.config import settings

    if settings.MOCK_MODE:
        mock_route = RouteCPIContributionResponse(
            rank=1,
            route_code="DEL-BOM",
            corridor_name="Delhi-Mumbai",
            route_weight_pct=0.0817,
            price_movement_pct=3.2,
            transport_subgroup_impact_bps=0.26,
            headline_cpi_impact_bps=0.044,
            share_of_total_inflation_pct=3.58,
            cumulative_headline_bps=0.044,
            contribution_direction="positive",
        )
        return CPIDecompositionResponse(
            calculation_date=target_date or "2026-07-21",
            total_transport_impact_bps=1.23,
            total_headline_cpi_impact_bps=0.21,
            top_positive_contributors=[mock_route],
            top_negative_contributors=[mock_route],
            full_route_waterfall=[mock_route],
            methodology_summary="synthetic",
            generated_at="2026-07-21T12:00:00",
        )
    try:
        from engine.analytics.cpi_decomposition import get_cpi_decomposition

        report = get_cpi_decomposition(target_date=target_date)
        return CPIDecompositionResponse(
            calculation_date=report.calculation_date,
            total_transport_impact_bps=report.total_transport_impact_bps,
            total_headline_cpi_impact_bps=report.total_headline_cpi_impact_bps,
            top_positive_contributors=[
                RouteCPIContributionResponse(**r.__dict__) for r in report.top_positive_contributors
            ],
            top_negative_contributors=[
                RouteCPIContributionResponse(**r.__dict__) for r in report.top_negative_contributors
            ],
            full_route_waterfall=[RouteCPIContributionResponse(**r.__dict__) for r in report.full_route_waterfall],
            methodology_summary=report.methodology_summary,
            generated_at=report.generated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPI decomposition failed: {e}") from e


# ===== Heatmap Endpoints =====


class HeatmapCellResponse(BaseModel):
    route_code: str
    advance_window: str
    days_advance: int
    current_fare_inr: float
    base_benchmark_fare: float
    price_change_pct: float
    volatility_score: float
    status: str
    sample_size: int


class HeatmapRowResponse(BaseModel):
    route_code: str
    origin_city: str
    destination_city: str
    dgca_weight_pct: float
    corridor_average_fare: float
    composite_relative: float
    horizon_cells: dict[str, HeatmapCellResponse]


class HeatmapReportResponse(BaseModel):
    as_of_date: str
    total_routes: int
    total_horizons: int
    matrix_rows: list[HeatmapRowResponse]
    summary_surge_count: int
    summary_discount_count: int
    generated_at: str


@router.get("/heatmap", response_model=HeatmapReportResponse)
async def get_heatmap(
    target_date: str | None = Query(None),
    sort_by: str = Query("weight", pattern="^(weight|fare_desc|fare_asc|change)$"),
    route_filter: str | None = Query(None),
):
    """Get 20x5 airfare heatmap matrix."""
    from app.core.config import settings

    if settings.MOCK_MODE:
        mock_cell = HeatmapCellResponse(
            route_code="DEL-BOM",
            advance_window="T-7",
            days_advance=7,
            current_fare_inr=5195.0,
            base_benchmark_fare=4907.87,
            price_change_pct=3.2,
            volatility_score=0.12,
            status="normal",
            sample_size=50,
        )
        mock_row = HeatmapRowResponse(
            route_code="DEL-BOM",
            origin_city="Delhi",
            destination_city="Mumbai",
            dgca_weight_pct=8.17,
            corridor_average_fare=5195.0,
            composite_relative=1.0,
            horizon_cells={f"T-{d}": mock_cell for d in [1, 7, 15, 30, 45]},
        )
        return HeatmapReportResponse(
            as_of_date=target_date or "2026-07-21",
            total_routes=1,
            total_horizons=5,
            matrix_rows=[mock_row],
            summary_surge_count=0,
            summary_discount_count=0,
            generated_at="2026-07-21T12:00:00",
        )
    try:
        from engine.analytics.heatmap import get_airfare_heatmap

        report = get_airfare_heatmap(target_date=target_date, sort_by=sort_by, route_filter=route_filter)
        return HeatmapReportResponse(
            as_of_date=report.as_of_date,
            total_routes=report.total_routes,
            total_horizons=report.total_horizons,
            matrix_rows=[
                HeatmapRowResponse(
                    route_code=row.route_code,
                    origin_city=row.origin_city,
                    destination_city=row.destination_city,
                    dgca_weight_pct=row.dgca_weight_pct,
                    corridor_average_fare=row.corridor_average_fare,
                    composite_relative=row.composite_relative,
                    horizon_cells={k: HeatmapCellResponse(**v.__dict__) for k, v in row.horizon_cells.items()},
                )
                for row in report.matrix_rows
            ],
            summary_surge_count=report.summary_surge_count,
            summary_discount_count=report.summary_discount_count,
            generated_at=report.generated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {e}") from e
