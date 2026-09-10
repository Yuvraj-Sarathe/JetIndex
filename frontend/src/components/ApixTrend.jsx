import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';

/**
 * ApixTrend — Recharts LineChart showing daily/weekly/monthly APIx trend.
 */
function ApixTrend({ data }) {
  const [granularity, setGranularity] = useState('daily');

  if (!data || data.length === 0) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">APIx Trend & Granularity</h3>
        <p className="text-xs text-ink-muted">No index data available for selected range</p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">APIx Price Index Trend</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/40 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-lime animate-pulse"></span>
              PUBLISHED DAILY SERIES
            </span>
          </div>
          <p className="text-xs text-ink-muted">DGCA Laspeyres weighted airfare index · Base 100 benchmark</p>
        </div>
        <div className="flex gap-1 bg-canvas/80 p-0.5 rounded-lg border border-ink-border/50 self-start sm:self-auto">
          {['daily', 'weekly', 'monthly'].map((g) => (
            <button
              key={g}
              onClick={() => setGranularity(g)}
              className={`px-2.5 py-1 text-xs rounded-md font-medium capitalize transition-all ${
                granularity === g
                  ? 'bg-accent-violet text-white shadow-sm font-semibold'
                  : 'text-ink-muted hover:text-white hover:bg-ink-border/40'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#261c3d" />
          <XAxis dataKey="date" stroke="#786c91" fontSize={11} tickLine={false} />
          <YAxis stroke="#786c91" fontSize={11} domain={['auto', 'auto']} tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f1633',
              borderColor: '#362d59',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
            }}
            itemStyle={{ color: '#ffffff' }}
            formatter={(value, name) => [`${Number(value).toFixed(2)} pts`, name]}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          <ReferenceLine
            y={100}
            stroke="#362d59"
            strokeDasharray="4 4"
            label={{ value: 'Base 100', position: 'insideTopLeft', fill: '#786c91', fontSize: 10 }}
          />
          <Line
            type="monotone"
            dataKey="apix"
            stroke="#c2ef4e"
            strokeWidth={2.5}
            dot={{ r: 2, fill: '#c2ef4e' }}
            activeDot={{ r: 5, fill: '#c2ef4e', stroke: '#ffffff', strokeWidth: 2 }}
            name="APIx (Published All-In)"
          />
          {data[0]?.apix_base_only !== undefined && (
            <Line
              type="monotone"
              dataKey="apix_base_only"
              stroke="#6a5fc1"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
              name="Base Fare Only"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ApixTrend;