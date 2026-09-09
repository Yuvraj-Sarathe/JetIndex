import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useElasticity } from '../hooks/useApix';

/**
 * ElasticityCurve — Fare vs lead time per route.
 */
function ElasticityCurve({ routeId }) {
  const { data, loading, error } = useElasticity(routeId);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Lead-Time Elasticity</h3>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Lead-Time Elasticity</h3>
        <p className="text-rose-500">Error: {error}</p>
      </div>
    );
  }

  // The live DB query (get_elasticity_data) returns median_fare/median_base_fare/n_quotes,
  // while MOCK_MODE data returns avg_total_fare/avg_base_fare/n. Support both without
  // inventing a field that isn't actually there.
  const chartData = (data || [])
    .map((d) => ({
      leadTime: d.lead_time,
      totalFare: d.avg_total_fare ?? d.median_fare,
      baseFare: d.avg_base_fare ?? d.median_base_fare,
      n: d.n ?? d.n_quotes,
    }))
    .filter((d) => d.totalFare != null);

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Lead-Time Elasticity</h3>
        <p className="text-slate-500">
          {routeId
            ? 'No elasticity data available for this route.'
            : 'Select a route to see fare vs. lead-time elasticity.'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Lead-Time Elasticity</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="leadTime"
            name="Lead Time (days)"
            stroke="#94a3b8"
            fontSize={12}
            label={{ value: 'Lead Time (days)', position: 'bottom', offset: -5 }}
          />
          <YAxis
            dataKey="totalFare"
            name="Fare (₹)"
            stroke="#94a3b8"
            fontSize={12}
            label={{ value: 'Fare (₹)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            formatter={(value, name) => [`₹${value.toLocaleString()}`, name]}
          />
          <Legend />
          <Scatter
            name="Total Fare"
            data={chartData}
            fill="#6366f1"
            line={{ stroke: '#6366f1', strokeWidth: 2 }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ElasticityCurve;