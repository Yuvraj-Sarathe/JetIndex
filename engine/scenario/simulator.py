"""
JetIndex - Quantitative Policy What-If Scenario Simulator
Models structural airfare shocks, fuel pass-through elasticity, and capacity bottlenecks.
Ported from VayuSutra-V4 with SQLAlchemy adaptation.
"""

import datetime
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from db.models import NationalIndex
from db.session import SessionLocal

logger = logging.getLogger("jetindex.scenario")


class ScenarioInputParameters(BaseModel):
    """Input parameters for macroeconomic policy scenario simulation."""

    scenario_name: str = Field(default="Custom Macro Shock Simulation", description="Descriptive scenario label")
    airfare_shock_pct: float = Field(
        default=10.0, ge=-50.0, le=100.0, description="Exogenous airline tariff shock in %"
    )
    demand_change_pct: float = Field(
        default=5.0, ge=-50.0, le=100.0, description="Passenger demand elasticity shift in %"
    )
    capacity_change_pct: float = Field(
        default=-3.0, ge=-50.0, le=100.0, description="Airline seat capacity constraint shift in %"
    )
    atf_fuel_shock_pct: float = Field(
        default=12.0, ge=-50.0, le=150.0, description="Aviation Turbine Fuel price shock in %"
    )
    booking_horizon_shock: str | None = Field(
        default=None, description="Optional target horizon: T+1, T+7, T+15, T+30, T+45"
    )
    seasonal_factor: float = Field(
        default=1.0, ge=0.5, le=2.0, description="Seasonal multiplier (e.g. 1.15 for festival peak)"
    )


@dataclass
class RouteScenarioImpact:
    route_code: str
    corridor_name: str
    route_weight_pct: float
    baseline_indexed_fare: float
    projected_indexed_fare: float
    projected_price_delta_pct: float
    marginal_transport_impact_bps: float
    marginal_headline_cpi_bps: float


@dataclass
class ScenarioSimulationResult:
    scenario_id: str
    scenario_name: str
    inputs: dict[str, Any]
    baseline_airfare_index: float
    projected_airfare_index: float
    net_airfare_index_change_pct: float
    projected_transport_subgroup_impact_bps: float
    projected_headline_cpi_impact_bps: float
    projected_inflation_pressure_score: float
    projected_pressure_level: str
    confidence_interval_95: dict[str, float]
    top_affected_corridors: list[RouteScenarioImpact]
    policy_implication_brief: str
    data_tag: str = "MODELLED / SIMULATED"
    simulated_at: str = ""


CPI_WEIGHTS = {
    "airfare_share_within_transport": 0.0385,
    "transport_and_communication_cpi_weight": 0.0859,
}

DGCA_ROUTES = {
    "DEL-BOM": ("New Delhi", "Mumbai", 0.1092, 4850.0),
    "DEL-BLR": ("New Delhi", "Bengaluru", 0.0805, 5200.0),
    "BOM-BLR": ("Mumbai", "Bengaluru", 0.0712, 4500.0),
    "DEL-MAA": ("New Delhi", "Chennai", 0.0543, 5100.0),
    "BOM-DEL": ("Mumbai", "New Delhi", 0.0498, 4850.0),
    "DEL-CCU": ("New Delhi", "Kolkata", 0.0467, 4900.0),
}


class PolicyScenarioSimulator:
    """Simulates macroeconomic shocks through the multi-layer airfare CPI transmission mechanism."""

    def run_simulation(self, params: ScenarioInputParameters) -> ScenarioSimulationResult:
        db = SessionLocal()
        now_iso = datetime.datetime.now(datetime.UTC).isoformat()
        scenario_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        try:
            latest = db.query(NationalIndex).order_by(NationalIndex.calculation_date.desc()).first()
            base_index = latest.laspeyres_index if latest else 106.84
        finally:
            db.close()

        # Econometric elasticity pass-through model
        fuel_pass_through_factor = 0.35 * 0.75
        fuel_contribution_pct = params.atf_fuel_shock_pct * fuel_pass_through_factor
        capacity_tightness_pct = (params.demand_change_pct - params.capacity_change_pct) * 0.45
        seasonal_shift_pct = (params.seasonal_factor - 1.0) * 100.0

        net_airfare_pct = params.airfare_shock_pct + fuel_contribution_pct + capacity_tightness_pct + seasonal_shift_pct

        projected_index = round(base_index * (1.0 + net_airfare_pct / 100.0), 2)
        effective_pct_change = round(((projected_index - base_index) / base_index) * 100.0, 2)

        # CPI Basis Point Transmission
        w_airfare = CPI_WEIGHTS["airfare_share_within_transport"]
        w_transport = CPI_WEIGHTS["transport_and_communication_cpi_weight"]
        trans_bps = round(effective_pct_change * w_airfare * 100.0, 2)
        head_bps = round(trans_bps * w_transport, 4)

        # Projected Pressure Score
        proj_pressure = min(100.0, max(5.0, 42.0 + effective_pct_change * 2.5 + abs(head_bps) * 5.0))
        proj_pressure = round(proj_pressure, 1)

        if proj_pressure >= 76.0:
            pressure_lvl = "CRITICAL"
        elif proj_pressure >= 51.0:
            pressure_lvl = "HIGH"
        elif proj_pressure >= 26.0:
            pressure_lvl = "MODERATE"
        else:
            pressure_lvl = "LOW"

        ci_lower = round(projected_index * 0.985, 2)
        ci_upper = round(projected_index * 1.015, 2)

        # Corridor Impacts
        affected_corridors: list[RouteScenarioImpact] = []
        for rc, (origin, dest, weight, bm) in DGCA_ROUTES.items():
            b_fare = bm * 1.068
            p_fare = round(b_fare * (1.0 + net_airfare_pct / 100.0), 2)
            c_trans = round(net_airfare_pct * weight * w_airfare * 100.0, 4)
            c_head = round(c_trans * w_transport, 6)

            affected_corridors.append(
                RouteScenarioImpact(
                    route_code=rc,
                    corridor_name=f"{origin} <-> {dest}",
                    route_weight_pct=round(weight * 100.0, 2),
                    baseline_indexed_fare=round(b_fare, 2),
                    projected_indexed_fare=p_fare,
                    projected_price_delta_pct=round(net_airfare_pct, 2),
                    marginal_transport_impact_bps=c_trans,
                    marginal_headline_cpi_bps=c_head,
                )
            )

        policy_brief = (
            f"Under scenario '{params.scenario_name}' (Airfare {params.airfare_shock_pct:+.1f}%, Fuel {params.atf_fuel_shock_pct:+.1f}%, "
            f"Demand {params.demand_change_pct:+.1f}%, Capacity {params.capacity_change_pct:+.1f}%), the National Airfare Price Index "
            f"is modeled to shift by {effective_pct_change:+.2f}% to {projected_index:.2f}. This transmits {trans_bps:+.2f} bps into "
            f"MoSPI Transport & Communication (Group 6.1.03) and {head_bps:+.4f} bps into Headline CPI (Pressure: {pressure_lvl})."
        )

        return ScenarioSimulationResult(
            scenario_id=scenario_id,
            scenario_name=params.scenario_name,
            inputs=params.model_dump(),
            baseline_airfare_index=base_index,
            projected_airfare_index=projected_index,
            net_airfare_index_change_pct=effective_pct_change,
            projected_transport_subgroup_impact_bps=trans_bps,
            projected_headline_cpi_impact_bps=head_bps,
            projected_inflation_pressure_score=proj_pressure,
            projected_pressure_level=pressure_lvl,
            confidence_interval_95={"lower_bound": ci_lower, "upper_bound": ci_upper},
            top_affected_corridors=affected_corridors,
            policy_implication_brief=policy_brief,
            data_tag="MODELLED / SIMULATED",
            simulated_at=now_iso,
        )


scenario_simulator = PolicyScenarioSimulator()


def simulate_policy_scenario(params: ScenarioInputParameters) -> ScenarioSimulationResult:
    return scenario_simulator.run_simulation(params)
