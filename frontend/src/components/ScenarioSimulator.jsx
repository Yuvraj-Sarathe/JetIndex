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
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-3">Policy Shock Presets</h3>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.name}
              onClick={() => applyPreset(p)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-card-elevated border border-ink-border text-ink-muted hover:text-white hover:border-accent-lime/60 transition-all font-medium"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-4">Macro Shock Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[
            { key: 'airfare_shock_pct', label: 'Airfare Shock (%)', min: -50, max: 100 },
            { key: 'demand_change_pct', label: 'Demand Change (%)', min: -50, max: 100 },
            { key: 'capacity_change_pct', label: 'Capacity Change (%)', min: -50, max: 100 },
            { key: 'atf_fuel_shock_pct', label: 'ATF Fuel Shock (%)', min: -50, max: 150 },
            { key: 'seasonal_factor', label: 'Seasonal Multiplier', min: 0.5, max: 2.0 },
          ].map(({ key, label, min, max }) => (
            <div key={key}>
              <label className="block text-xs font-mono uppercase text-ink-muted mb-1.5">{label}</label>
              <input
                type="number"
                value={params[key]}
                min={min}
                max={max}
                step="0.1"
                onChange={(e) => setParams({ ...params, [key]: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-canvas border border-ink-border rounded-lg text-sm font-mono text-white focus:outline-none focus:border-accent-lime focus:ring-1 focus:ring-accent-lime transition-colors"
              />
            </div>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="mt-5 px-5 py-2.5 bg-accent-violet hover:bg-accent-violet/90 text-white rounded-lg text-xs font-semibold uppercase tracking-wider transition-all disabled:opacity-50 flex items-center gap-2 shadow-sm"
        >
          <span>⚡</span>
          <span>{loading ? 'Simulating Dynamic Shocks...' : 'Simulate Policy Impact'}</span>
        </button>
      </form>

      {error && <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">{error}</div>}

      {/* Results */}
      {result && (
        <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white">Dynamic Policy Shock Projections</h3>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/40">
              SIMULATION ENGINE
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'Baseline Index', value: result.baseline_airfare_index?.toFixed(2), unit: 'pts' },
              { label: 'Projected Index', value: result.projected_airfare_index?.toFixed(2), unit: 'pts' },
              { label: 'Net Index Swing', value: `${result.net_airfare_index_change_pct >= 0 ? '+' : ''}${result.net_airfare_index_change_pct?.toFixed(2)}%`, unit: '' },
              { label: 'Surveillance Level', value: result.projected_pressure_level, unit: '' },
            ].map(({ label, value, unit }) => (
              <div key={label} className="p-3 bg-card-elevated border border-ink-border/70 rounded-xl text-center">
                <p className="text-[11px] font-mono uppercase text-ink-muted">{label}</p>
                <p className="text-lg font-mono font-bold text-accent-lime mt-0.5">{value} <span className="text-xs text-ink-faint font-normal">{unit}</span></p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="p-3.5 bg-card-elevated border border-ink-border/80 rounded-xl">
              <p className="text-xs font-mono uppercase text-accent-cyan">Transport CPI Transmission</p>
              <p className="text-2xl font-mono font-bold text-white mt-1">{result.projected_transport_subgroup_impact_bps?.toFixed(2)} bps</p>
              <p className="text-[11px] text-ink-faint mt-0.5">Contribution to official monthly transport CPI subgroup</p>
            </div>
            <div className="p-3.5 bg-card-elevated border border-ink-border/80 rounded-xl">
              <p className="text-xs font-mono uppercase text-accent-pink">Headline CPI Transmission</p>
              <p className="text-2xl font-mono font-bold text-white mt-1">{result.projected_headline_cpi_impact_bps?.toFixed(4)} bps</p>
              <p className="text-[11px] text-ink-faint mt-0.5">Direct headline basket passthrough</p>
            </div>
          </div>
          {result.policy_implication_brief && (
            <div className="p-4 bg-canvas/80 border border-ink-border/60 rounded-xl text-xs text-ink-muted leading-relaxed font-sans">
              <p className="text-[11px] font-mono uppercase text-accent-lime mb-1">Executive Policy Implication</p>
              {result.policy_implication_brief}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
