import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

/**
 * ApixTrend — Recharts LineChart showing daily/weekly/monthly APIx trend.
 */
function ApixTrend({ data }) {
  const [granularity, setGranularity] = useState('daily');

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">APIx Trend</h3>
        <p className="text-slate-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">APIx Trend</h3>
        <div className="flex gap-1">
          {['daily', 'weekly', 'monthly'].map((g) => (
            <button
              key={g}
              onClick={() => setGranularity(g)}
              className={`px-3 py-1 text-xs rounded ${
                granularity === g
                  ? 'bg-indigo-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="apix"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            name="APIx"
          />
          {data[0]?.apix_base_only !== undefined && (
            <Line
              type="monotone"
              dataKey="apix_base_only"
              stroke="#94a3b8"
              strokeWidth={1}
              strokeDasharray="5 5"
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
