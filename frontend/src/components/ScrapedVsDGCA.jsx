import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useScrapedVsDGCA } from '../hooks/useApix';

/**
 * ScrapedVsDGCA — line chart comparing our scraped avg fare vs DGCA monthly avg.
 * Both lines are in rupees (same units), making the comparison visually meaningful.
 */
function ScrapedVsDGCA() {
  const { data, loading, error } = useScrapedVsDGCA();

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-rose-500">Error: {error}</p>
      </div>
    );
  }

  const rows = data || [];

  if (rows.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-slate-500">No comparison data available</p>
      </div>
    );
  }

  // Build chart data — only months where at least one series has data
  const chartData = rows
    .filter((r) => r.avg_scraped != null || r.avg_dgca != null)
    .map((r) => ({
      month: r.month,
      scraped: r.avg_scraped != null ? Number(r.avg_scraped) : null,
      dgca: r.avg_dgca != null ? Number(r.avg_dgca) : null,
    }));

  // Count overlap months (both present)
  const overlapMonths = chartData.filter((d) => d.scraped != null && d.dgca != null).length;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Scraped Fares vs DGCA Benchmark</h3>
        <span className="text-xs text-slate-400">
          {overlapMonths} overlapping month{overlapMonths !== 1 ? 's' : ''}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
          <Tooltip formatter={(value) => [`₹${Number(value).toLocaleString()}`, undefined]} />
          <Legend />
          <Line
            type="monotone"
            dataKey="scraped"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Our Scraped Avg Fare"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="dgca"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="DGCA Monthly Avg"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-400 mt-2">
        Both series in ₹ — direct comparison of actual fare levels
      </p>
    </div>
  );
}

export default ScrapedVsDGCA;
