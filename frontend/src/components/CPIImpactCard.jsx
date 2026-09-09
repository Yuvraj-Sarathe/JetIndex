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
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-medium text-slate-900 mb-4">CPI Transmission Matrix</h3>
      
      {/* Current Index */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-600">Current Airfare Index</p>
        <p className="text-2xl font-bold text-blue-700">{data.current_airfare_index}</p>
      </div>

      {/* Weights Structure */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-slate-700 mb-2">CPI Weight Structure</h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-slate-500">Transport & Comm</p>
            <p className="font-medium text-slate-900">{(weights.cpi_transport_and_communication_weight * 100).toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-slate-500">Airfare in Transport</p>
            <p className="font-medium text-slate-900">{(weights.airfare_share_in_transport * 100).toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-slate-500">Effective Headline</p>
            <p className="font-medium text-slate-900">{(weights.effective_headline_weight * 100).toFixed(4)}%</p>
          </div>
        </div>
      </div>

      {/* Shock Scenarios */}
      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-2">Sensitivity Stress Matrix</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-2 font-medium text-slate-600">Airfare Swing</th>
                <th className="text-right py-2 px-2 font-medium text-slate-600">Transport (bps)</th>
                <th className="text-right py-2 px-2 font-medium text-slate-600">Headline (bps)</th>
                <th className="text-left py-2 px-2 font-medium text-slate-600 hidden md:table-cell">Significance</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((s, i) => (
                <tr key={i} className="border-b border-slate-100">
                  <td className="py-2 px-2 font-mono">{s.airfare_swing_pct > 0 ? '+' : ''}{s.airfare_swing_pct}%</td>
                  <td className="py-2 px-2 text-right font-mono">{s.transport_subgroup_impact_bps > 0 ? '+' : ''}{s.transport_subgroup_impact_bps}</td>
                  <td className="py-2 px-2 text-right font-mono">{s.headline_cpi_impact_bps > 0 ? '+' : ''}{s.headline_cpi_impact_bps}</td>
                  <td className="py-2 px-2 hidden md:table-cell">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      s.monetary_policy_significance === 'High' ? 'bg-red-100 text-red-700' :
                      s.monetary_policy_significance === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
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
