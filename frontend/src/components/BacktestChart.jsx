import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useBacktest } from '../hooks/useApix';

/**
 * BacktestChart — Implied fare (₹) from APIx vs DGCA monthly average (₹).
 * Both lines in the same currency units so the visual comparison is meaningful.
 * Summary stats (MAPE/RMSE/r) shown as numeric badges.
 */
function BacktestChart() {
  const { data, loading, error } = useBacktest();

  if (loading) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">DGCA Backtest Validation</h3>
        <p className="text-xs text-ink-muted">Validating APIx against official DGCA city-pair actuals...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">DGCA Backtest Validation</h3>
        <p className="text-xs text-rose-400">Error: {error}</p>
      </div>
    );
  }

  const monthly = data?.monthly || [];
  const summary = data?.summary || {};

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">DGCA Official Backtest</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/40 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse"></span>
              PUBLISHED ACTUALS
            </span>
          </div>
          <p className="text-xs text-ink-muted">Historical alignment against official published civil aviation statistics</p>
        </div>
        {summary.mape !== undefined && (
          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/30 self-start sm:self-auto">
            MAPE: {summary.mape.toFixed(1)}%
          </span>
        )}
      </div>

      {monthly.length === 0 ? (
        <p className="text-xs text-ink-muted">No backtest records available</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthly}>
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
              dataKey="implied_fare"
              stroke="#c2ef4e"
              strokeWidth={2}
              dot={{ r: 3, fill: '#c2ef4e' }}
              name="APIx Implied Fare"
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="dgca_avg_fare"
              stroke="#4ecdc4"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#4ecdc4', stroke: '#150f23', strokeWidth: 1.5 }}
              activeDot={{ r: 6, fill: '#4ecdc4', stroke: '#ffffff', strokeWidth: 2 }}
              name="DGCA (Official Published)"
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      <div className="mt-4 flex flex-wrap gap-2.5">
        {summary.mape !== undefined && (
          <div className="bg-canvas/70 border border-ink-border/80 rounded-lg px-3 py-1.5 text-xs font-mono">
            <span className="text-ink-muted">Mean Absolute Error: </span>
            <span className="text-white font-semibold">{summary.mape?.toFixed(2)}%</span>
          </div>
        )}
        {summary.rmse !== undefined && (
          <div className="bg-canvas/70 border border-ink-border/80 rounded-lg px-3 py-1.5 text-xs font-mono">
            <span className="text-ink-muted">RMSE: </span>
            <span className="text-white font-semibold">₹{summary.rmse?.toFixed(0)}</span>
          </div>
        )}
        {summary.corr !== undefined && (
          <div className="bg-canvas/70 border border-ink-border/80 rounded-lg px-3 py-1.5 text-xs font-mono">
            <span className="text-ink-muted">Pearson r: </span>
            <span className="text-accent-lime font-semibold">{summary.corr?.toFixed(4)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default BacktestChart;
