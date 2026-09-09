"""Scenario Simulator - Policy What-If API."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


class ScenarioInput(BaseModel):
    scenario_name: str = Field(default="Custom Policy Shock")
    airfare_shock_pct: float = Field(default=10.0, ge=-50.0, le=100.0)
    demand_change_pct: float = Field(default=5.0, ge=-50.0, le=100.0)
    capacity_change_pct: float = Field(default=-3.0, ge=-50.0, le=100.0)
    atf_fuel_shock_pct: float = Field(default=12.0, ge=-50.0, le=150.0)
    seasonal_factor: float = Field(default=1.0, ge=0.5, le=2.0)


@router.post("/simulate")
def run_scenario_simulation(
    params: ScenarioInput,
    _token: str = Depends(require_token),
) -> dict:
    """Simulates macroeconomic policy shock scenarios through the airfare transmission mechanism."""
    if settings.MOCK_MODE:
        return {
            "scenario_id": "SIM-MOCK-001",
            "scenario_name": params.scenario_name,
            "data_tag": "SIMULATED",
            "baseline_airfare_index": 106.84,
            "projected_airfare_index": 107.91,
            "net_airfare_index_change_pct": 1.0,
            "projected_transport_subgroup_impact_bps": 3.85,
            "projected_headline_cpi_impact_bps": 0.13,
            "projected_pressure_level": "MODERATE",
            "policy_implication_brief": f"Under '{params.scenario_name}', index shifts by ~1.0%.",
        }
    try:
        from engine.scenario.simulator import PolicyScenarioSimulator, ScenarioInputParameters

        params_model = ScenarioInputParameters(
            scenario_name=params.scenario_name,
            airfare_shock_pct=params.airfare_shock_pct,
            demand_change_pct=params.demand_change_pct,
            capacity_change_pct=params.capacity_change_pct,
            atf_fuel_shock_pct=params.atf_fuel_shock_pct,
            seasonal_factor=params.seasonal_factor,
        )
        sim = PolicyScenarioSimulator()
        result = sim.run_simulation(params_model)
        from dataclasses import asdict

        return {"data_tag": "SIMULATED", **asdict(result)}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
