import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useElasticity } from '../hooks/useApix';

/**
 * ElasticityCurve — Fare vs lead time per route.
 */
function ElasticityCurve({ routeId }) {
  const { data, loading, error } = useElasticity(routeId);

  if (loading) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Lead-Time Elasticity Curve</h3>
        <p className="text-xs text-ink-muted">Analyzing booking advance curve...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Lead-Time Elasticity Curve</h3>
        <p className="text-xs text-rose-400">Error: {error}</p>
      </div>
    );
  }

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
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Lead-Time Elasticity Curve</h3>
        <p className="text-xs text-ink-muted">
          {routeId
            ? 'No elasticity data available for this route.'
            : 'Select a route to view lead-time elasticity.'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-white">Booking Lead-Time Elasticity</h3>
        <p className="text-xs text-ink-muted">Average fare progression from T+60 to T+0 departure</p>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#242424" />
          <XAxis
            dataKey="leadTime"
            name="Lead Time (days)"
            stroke="#888888"
            fontSize={11}
            tickLine={false}
            label={{ value: 'Days Prior to Departure', position: 'bottom', offset: -2, fill: '#888888', fontSize: 10 }}
          />
          <YAxis
            dataKey="totalFare"
            name="Fare (₹)"
            stroke="#888888"
            fontSize={11}
            tickLine={false}
            label={{ value: 'Fare (₹)', angle: -90, position: 'insideLeft', fill: '#888888', fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a1a',
              borderColor: '#2a2a2a',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.6)',
            }}
            formatter={(value, name) => [`₹${Number(value).toLocaleString()}`, name]}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          <Scatter
            name="All-In Fare"
            data={chartData}
            fill="#faff69"
            line={{ stroke: '#3b82f6', strokeWidth: 2 }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ElasticityCurve;