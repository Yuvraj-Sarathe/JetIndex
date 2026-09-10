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
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-xs text-ink-muted">Comparing live market prices against official statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-xs text-rose-400">Error: {error}</p>
      </div>
    );
  }

  const rows = data || [];

  if (rows.length === 0) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Scraped Fares vs DGCA Benchmark</h3>
        <p className="text-xs text-ink-muted">No comparison data available</p>
      </div>
    );
  }

  const chartData = rows
    .filter((r) => r.avg_scraped != null || r.avg_dgca != null)
    .map((r) => ({
      month: r.month,
      scraped: r.avg_scraped != null ? Number(r.avg_scraped) : null,
      dgca: r.avg_dgca != null ? Number(r.avg_dgca) : null,
    }));

  const overlapMonths = chartData.filter((d) => d.scraped != null && d.dgca != null).length;

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">Scraped Fares vs DGCA Benchmark</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/40 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse"></span>
              PUBLISHED BENCHMARK
            </span>
          </div>
          <p className="text-xs text-ink-muted">Parity check between automated quotes and official published DGCA reports</p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-canvas text-accent-lime border border-ink-border/60 self-start sm:self-auto font-medium">
          {overlapMonths} overlapping month{overlapMonths !== 1 ? 's' : ''}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#261c3d" />
          <XAxis dataKey="month" stroke="#786c91" fontSize={11} tickLine={false} />
          <YAxis stroke="#786c91" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f1633',
              borderColor: '#362d59',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
            }}
            formatter={(value, name) => [
              `₹${Number(value).toLocaleString()}`,
              name.includes('Published') ? `★ ${name}` : name,
            ]}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          <Line
            type="monotone"
            dataKey="scraped"
            stroke="#c2ef4e"
            strokeWidth={2}
            dot={{ r: 3, fill: '#c2ef4e' }}
            name="Scraped Market Avg"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="dgca"
            stroke="#4ecdc4"
            strokeWidth={2.5}
            dot={{ r: 4, fill: '#4ecdc4', stroke: '#150f23', strokeWidth: 1.5 }}
            activeDot={{ r: 6, fill: '#4ecdc4', stroke: '#ffffff', strokeWidth: 2 }}
            name="DGCA (Official Published)"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex items-center justify-between mt-3 text-[11px] font-mono">
        <span className="text-ink-faint">All values rendered in INR (₹) — direct benchmark comparison</span>
        <span className="text-accent-cyan font-medium flex items-center gap-1">
          <span className="w-2 h-0.5 bg-accent-cyan inline-block"></span> Published Series (DGCA Monthly)
        </span>
      </div>
    </div>
  );
}

export default ScrapedVsDGCA;
