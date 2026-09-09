import { useValidation } from '../hooks/useValidation';

export default function ModelValidation() {
  const { data, loading, error } = useValidation();

  if (loading) return <div className="text-center py-8 text-slate-400">Loading validation report...</div>;
  if (error) return <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>;

  const models = data?.models_comparison_leaderboard || [];
  const errorDist = data?.error_distribution || {};
  const mandates = data?.statutory_mandates || {};

  return (
    <div className="space-y-6">
      {/* Mandates */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-3">Statutory Mandates</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-green-50 rounded-lg text-center">
            <p className="text-xs text-green-600">Pearson R</p>
            <p className="text-sm font-mono font-bold text-green-900">≥ 0.8500</p>
          </div>
          <div className="p-3 bg-green-50 rounded-lg text-center">
            <p className="text-xs text-green-600">MAPE</p>
            <p className="text-sm font-mono font-bold text-green-900">≤ 4.00%</p>
          </div>
          <div className="p-3 bg-green-50 rounded-lg text-center">
            <p className="text-xs text-green-600">R² Score</p>
            <p className="text-sm font-mono font-bold text-green-900">≥ 0.7500</p>
          </div>
          <div className="p-3 bg-green-50 rounded-lg text-center">
            <p className="text-xs text-green-600">Overall</p>
            <p className="text-sm font-bold text-green-900">{mandates.overall_validation_result?.replace(/_/g, ' ')}</p>
          </div>
        </div>
      </div>

      {/* Models Leaderboard */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Model Leaderboard</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4">Model</th>
                <th className="pb-2 pr-4">Pearson R</th>
                <th className="pb-2 pr-4">MAPE %</th>
                <th className="pb-2 pr-4">R²</th>
                <th className="pb-2 pr-4">RMSE</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m, i) => (
                <tr key={i} className={`border-b border-slate-100 ${m.benchmark_status === 'PRIMARY_STATUTORY_CHAMPION' ? 'bg-green-50' : ''}`}>
                  <td className="py-2 pr-4 font-medium">{m.model_paradigm}</td>
                  <td className="py-2 pr-4 font-mono">{m.pearson_r?.toFixed(4)}</td>
                  <td className="py-2 pr-4 font-mono">{m.mape_pct?.toFixed(3)}</td>
                  <td className="py-2 pr-4 font-mono">{m.r2_score?.toFixed(4)}</td>
                  <td className="py-2 pr-4 font-mono">{m.rmse?.toFixed(3)}</td>
                  <td className="py-2"><span className="px-2 py-0.5 text-xs rounded bg-slate-100">{m.benchmark_status?.replace(/_/g, ' ')}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Error Distribution */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-3">Error Distribution</h3>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {[
            { label: 'Mean Residual', value: errorDist.mean_residual },
            { label: 'Std Residual', value: errorDist.std_residual },
            { label: 'Median', value: errorDist.median_residual },
            { label: 'Skewness', value: errorDist.skewness },
            { label: 'Kurtosis', value: errorDist.kurtosis },
            { label: '95% Bound', value: errorDist.quantile_95_error_bound },
          ].map(({ label, value }) => (
            <div key={label} className="text-center p-2 bg-slate-50 rounded">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="text-sm font-mono font-bold text-slate-900">{value}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-green-600 mt-3">{errorDist.normality_test_status?.replace(/_/g, ' ')}</p>
      </div>
    </div>
  );
}
