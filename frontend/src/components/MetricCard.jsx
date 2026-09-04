/**
 * MetricCard — displays a single headline metric with optional change indicator.
 */
function MetricCard({ label, value, change }) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
      <p className="text-sm text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      {change !== undefined && change !== null && (
        <p className={`text-sm mt-1 ${isPositive ? 'text-emerald-500' : isNegative ? 'text-rose-500' : 'text-slate-400'}`}>
          {isPositive ? '↑' : isNegative ? '↓' : '—'} {Math.abs(change).toFixed(2)}%
        </p>
      )}
    </div>
  );
}

export default MetricCard;
