/**
 * CPIImpactCard — Bps transmission visualization.
 */
function CPIImpactCard({ data }) {
  if (!data) {
    return <div className="text-center py-8 text-slate-500">No CPI impact data</div>;
  }

  const weights = data.weights_structure || {};
  const scenarios = data.sensitivity_stress_matrix || [];

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">CPI Transmission Matrix</h3>
          <p className="text-xs text-ink-muted">Sensitivity analysis of airfare inflation passthrough to headline CPI</p>
        </div>
      </div>
      
      {/* Current Index */}
      <div className="mb-5 p-3.5 bg-card-elevated border border-ink-border/80 rounded-xl flex items-center justify-between">
        <div>
          <p className="text-xs font-mono uppercase text-ink-muted">Current Published Airfare Index</p>
          <p className="text-2xl font-mono font-bold text-accent-lime mt-0.5">{data.current_airfare_index}</p>
        </div>
        <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/40">
          MoSPI BASKET
        </span>
      </div>

      {/* Weights Structure */}
      <div className="mb-6">
        <h4 className="text-xs font-mono uppercase text-ink-faint mb-2.5">Official CPI Weight Structure</h4>
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-canvas/60 border border-ink-border/60 rounded-lg">
            <p className="text-ink-muted">Transport & Comm</p>
            <p className="font-mono font-bold text-white text-sm mt-0.5">{(weights.cpi_transport_and_communication_weight * 100).toFixed(2)}%</p>
          </div>
          <div className="p-3 bg-canvas/60 border border-ink-border/60 rounded-lg">
            <p className="text-ink-muted">Airfare in Transport</p>
            <p className="font-mono font-bold text-white text-sm mt-0.5">{(weights.airfare_share_in_transport * 100).toFixed(2)}%</p>
          </div>
          <div className="p-3 bg-canvas/60 border border-ink-border/60 rounded-lg">
            <p className="text-ink-muted">Effective Headline</p>
            <p className="font-mono font-bold text-accent-lime text-sm mt-0.5">{(weights.effective_headline_weight * 100).toFixed(4)}%</p>
          </div>
        </div>
      </div>

      {/* Shock Scenarios */}
      <div>
        <h4 className="text-xs font-mono uppercase text-ink-faint mb-2.5">Sensitivity Stress Matrix</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm font-mono text-xs">
            <thead>
              <tr className="border-b border-ink-border text-left uppercase text-[11px] text-ink-faint">
                <th className="py-2.5 px-2">Airfare Swing</th>
                <th className="text-right py-2.5 px-2">Transport (bps)</th>
                <th className="text-right py-2.5 px-2">Headline (bps)</th>
                <th className="py-2.5 px-2 hidden md:table-cell">Policy Significance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-border/40">
              {scenarios.map((s, i) => (
                <tr key={i} className="hover:bg-card-hover transition-colors">
                  <td className="py-2.5 px-2 font-bold text-white">{s.airfare_swing_pct > 0 ? '+' : ''}{s.airfare_swing_pct}%</td>
                  <td className="py-2.5 px-2 text-right text-accent-cyan font-bold">{s.transport_subgroup_impact_bps > 0 ? '+' : ''}{s.transport_subgroup_impact_bps}</td>
                  <td className="py-2.5 px-2 text-right text-accent-pink font-bold">{s.headline_cpi_impact_bps > 0 ? '+' : ''}{s.headline_cpi_impact_bps}</td>
                  <td className="py-2.5 px-2 hidden md:table-cell">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                      s.monetary_policy_significance === 'High' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                      s.monetary_policy_significance === 'Moderate' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                      'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {s.monetary_policy_significance}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default CPIImpactCard;
