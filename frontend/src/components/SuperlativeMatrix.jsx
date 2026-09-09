/**
 * SuperlativeMatrix — Comparison table for Laspeyres, Paasche, Fisher, Törnqvist, Walsh indices.
 */
function SuperlativeMatrix({ data }) {
  if (!data) {
    return <div className="text-center py-8 text-slate-500">No superlative data</div>;
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
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-medium text-slate-900 mb-4">Superlative Index Comparison</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-2 px-3 font-medium text-slate-600">Index</th>
              <th className="text-right py-2 px-3 font-medium text-slate-600">Value</th>
              <th className="text-left py-2 px-3 font-medium text-slate-600 hidden md:table-cell">Description</th>
              <th className="text-left py-2 px-3 font-medium text-slate-600 hidden md:table-cell">Bias</th>
            </tr>
          </thead>
          <tbody>
            {indices.map((idx) => (
              <tr key={idx.name} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="py-2 px-3 font-medium text-slate-900">{idx.name}</td>
                <td className="py-2 px-3 text-right font-mono text-slate-700">{idx.value.toFixed(2)}</td>
                <td className="py-2 px-3 text-slate-500 hidden md:table-cell">{idx.description}</td>
                <td className="py-2 px-3 text-slate-500 hidden md:table-cell">{idx.bias}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Substitution Bias */}
      <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="text-amber-600 font-medium">Substitution Bias:</span>
          <span className="font-mono text-amber-700">{substitutionBias.toFixed(4)} points</span>
        </div>
        <p className="text-xs text-amber-600 mt-1">
          Laspeyres {substitutionBias > 0 ? 'overstates' : 'understates'} inflation relative to Fisher Ideal by {Math.abs(substitutionBias).toFixed(4)} index points
        </p>
      </div>
    </div>
  );
}

export default SuperlativeMatrix;
