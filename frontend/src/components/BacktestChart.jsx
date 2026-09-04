import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useBacktest } from '../hooks/useApix';

/**
 * BacktestChart — APIx (rebased) vs DGCA monthly average.
 */
function BacktestChart() {
  const { data, loading, error } = useBacktest();

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Backtest: APIx vs DGCA</h3>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Backtest: APIx vs DGCA</h3>
        <p className="text-rose-500">Error: {error}</p>
      </div>
    );
  }

  const monthly = data?.monthly || [];
  const summary = data?.summary || {};

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Backtest: APIx vs DGCA</h3>
        {summary.mape !== undefined && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
            MAPE: {summary.mape.toFixed(1)}%
          </span>
        )}
      </div>

      {monthly.length === 0 ? (
        <p className="text-slate-500">No backtest data available</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthly}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="apix_rebased"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="APIx (rebased)"
            />
            <Line
              type="monotone"
              dataKey="dgca_avg_fare"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="DGCA Avg Fare"
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      {summary.corr !== undefined && (
        <div className="mt-4 flex gap-4 text-sm text-slate-600">
          <span>RMSE: {summary.rmse?.toFixed(2)}</span>
          <span>Correlation: {summary.corr?.toFixed(4)}</span>
        </div>
      )}
    </div>
  );
}

export default BacktestChart;
