import { useState } from 'react';
import { useScenario } from '../hooks/useScenario';

const PRESETS = [
  { name: 'Fuel Price Shock (+20% ATF)', airfare_shock_pct: 0, demand_change_pct: 0, capacity_change_pct: 0, atf_fuel_shock_pct: 20, seasonal_factor: 1.0 },
  { name: 'Demand Surge (+15% festival)', airfare_shock_pct: 0, demand_change_pct: 15, capacity_change_pct: 0, atf_fuel_shock_pct: 0, seasonal_factor: 1.15 },
  { name: 'Capacity Cut (-10%)', airfare_shock_pct: 0, demand_change_pct: 5, capacity_change_pct: -10, atf_fuel_shock_pct: 0, seasonal_factor: 1.0 },
  { name: 'Combined Crisis', airfare_shock_pct: 12, demand_change_pct: 8, capacity_change_pct: -5, atf_fuel_shock_pct: 18, seasonal_factor: 1.2 },
];

export default function ScenarioSimulator() {
  const { result, loading, error, runSimulation } = useScenario();
  const [params, setParams] = useState({
    scenario_name: 'Custom Policy Shock',
    airfare_shock_pct: 10,
    demand_change_pct: 5,
    capacity_change_pct: -3,
    atf_fuel_shock_pct: 12,
    seasonal_factor: 1.0,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    runSimulation(params);
  };

  const applyPreset = (preset) => {
    setParams({ ...params, ...preset, scenario_name: preset.name });
  };

  return (
    <div className="space-y-6">
      {/* Presets */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Scenarios</h3>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button key={p.name} onClick={() => applyPreset(p)}
              className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors">
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Custom Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[
            { key: 'airfare_shock_pct', label: 'Airfare Shock (%)', min: -50, max: 100 },
            { key: 'demand_change_pct', label: 'Demand Change (%)', min: -50, max: 100 },
            { key: 'capacity_change_pct', label: 'Capacity Change (%)', min: -50, max: 100 },
            { key: 'atf_fuel_shock_pct', label: 'ATF Fuel Shock (%)', min: -50, max: 150 },
            { key: 'seasonal_factor', label: 'Seasonal Factor', min: 0.5, max: 2.0 },
          ].map(({ key, label, min, max }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
              <input type="number" value={params[key]} min={min} max={max} step="0.1"
                onChange={(e) => setParams({ ...params, [key]: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          ))}
        </div>
        <button type="submit" disabled={loading}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium">
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </form>

      {error && <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Simulation Results</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { label: 'Baseline Index', value: result.baseline_airfare_index?.toFixed(2) },
              { label: 'Projected Index', value: result.projected_airfare_index?.toFixed(2) },
              { label: 'Net Change', value: `${result.net_airfare_index_change_pct >= 0 ? '+' : ''}${result.net_airfare_index_change_pct?.toFixed(2)}%` },
              { label: 'Pressure Level', value: result.projected_pressure_level },
            ].map(({ label, value }) => (
              <div key={label} className="text-center p-3 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-lg font-bold text-slate-900">{value}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-blue-600">Transport CPI Impact</p>
              <p className="text-lg font-bold text-blue-900">{result.projected_transport_subgroup_impact_bps?.toFixed(2)} bps</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-xs text-purple-600">Headline CPI Impact</p>
              <p className="text-lg font-bold text-purple-900">{result.projected_headline_cpi_impact_bps?.toFixed(4)} bps</p>
            </div>
          </div>
          {result.policy_implication_brief && (
            <div className="p-4 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-700 leading-relaxed">{result.policy_implication_brief}</p>
            </div>
          )}
          <p className="text-xs text-slate-400 mt-3">Data Tag: {result.data_tag}</p>
        </div>
      )}
    </div>
  );
}
