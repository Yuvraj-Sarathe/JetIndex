/**
 * SuperlativeMatrix — Comparison table for Laspeyres, Paasche, Fisher, Törnqvist, Walsh indices.
 */
function SuperlativeMatrix({ data }) {
  if (!data) {
    return <div className="text-center py-8 text-ink-muted font-mono text-xs">No superlative data</div>;
  }

  const indices = [
    { name: 'Laspeyres', value: data.laspeyres || 100, description: 'Fixed basket (base period weights)', bias: 'Overstates inflation' },
    { name: 'Paasche', value: data.paasche || 100, description: 'Current-period weights', bias: 'Understates inflation' },
    { name: 'Fisher Ideal', value: data.fisher || 100, description: 'Geometric mean of Laspeyres & Paasche', bias: 'Unbiased (ILO recommended)' },
    { name: 'Törnqvist', value: data.tornqvist || 100, description: 'Log-weighted superlative', bias: 'Unbiased' },
    { name: 'Walsh', value: data.walsh || 100, description: 'Geometric weight superlative', bias: 'Unbiased' },
  ];

  const substitutionBias = data.substitution_bias_points || (data.laspeyres - data.fisher) || 0;

  return (
    <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Superlative Index Comparison</h3>
          <p className="text-xs text-ink-muted">Axiomatic tests across Laspeyres, Fisher, Törnqvist, and Walsh formulas</p>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm font-mono text-xs">
          <thead>
            <tr className="border-b border-hairline text-ink-faint uppercase text-[11px]">
              <th className="text-left py-2.5 px-3 font-sans">Formula</th>
              <th className="text-right py-2.5 px-3">Computed Index</th>
              <th className="text-left py-2.5 px-3 hidden md:table-cell font-sans">Axiomatic Description</th>
              <th className="text-left py-2.5 px-3 hidden md:table-cell font-sans">Theoretical Bias</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {indices.map((idx) => {
              const isPublished = idx.name === 'Laspeyres';
              return (
                <tr key={idx.name} className={`hover:bg-card-hover transition-colors ${isPublished ? 'bg-primary/10' : ''}`}>
                  <td className="py-2.5 px-3 font-sans font-medium text-white flex items-center gap-2">
                    {idx.name}
                    {isPublished && (
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-primary text-black uppercase">
                        Published Standard
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-primary">{idx.value.toFixed(2)}</td>
                  <td className="py-2.5 px-3 text-ink-muted hidden md:table-cell font-sans">{idx.description}</td>
                  <td className="py-2.5 px-3 text-accent-rose hidden md:table-cell font-sans">{idx.bias}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Substitution Bias */}
      <div className="mt-4 p-3 bg-card-elevated border border-hairline rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-accent-blue font-medium text-xs">Substitution Bias:</span>
          <span className="font-mono text-white text-xs font-bold">{substitutionBias.toFixed(4)} points</span>
        </div>
        <p className="text-[11px] text-ink-faint">
          Laspeyres {substitutionBias > 0 ? 'overstates' : 'understates'} inflation relative to Fisher Ideal by {Math.abs(substitutionBias).toFixed(4)} index points
        </p>
      </div>
    </div>
  );
}

export default SuperlativeMatrix;
