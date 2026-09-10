/**
 * MetricCard — displays a single headline metric with optional change indicator.
 */
function MetricCard({ label, value, change, helper, badge, isPublished }) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <div className={`bg-card border rounded-xl p-4 transition-all duration-200 group relative overflow-hidden ${
      isPublished 
        ? 'border-accent-lime/50 bg-gradient-to-br from-card to-card-elevated shadow-[0_0_20px_rgba(194,239,78,0.08)]' 
        : 'border-ink-border hover:border-accent-violet/60'
    }`}>
      {isPublished && (
        <div className="absolute top-0 right-0 w-16 h-16 pointer-events-none overflow-hidden">
          <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-accent-lime animate-ping"></div>
        </div>
      )}
      <div className="flex items-center justify-between mb-1.5 gap-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted group-hover:text-white transition-colors truncate">
          {label}
        </p>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {badge && (
            <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full bg-accent-lime/15 text-accent-lime border border-accent-lime/40 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-lime"></span>
              {badge}
            </span>
          )}
          {helper && (
            <span className="text-[10px] text-ink-faint border border-ink-border rounded px-1 cursor-help" title={helper}>
              ?
            </span>
          )}
        </div>
      </div>
      <p className="text-2xl lg:text-3xl font-bold text-white font-mono tabular-nums tracking-tight">
        {value}
      </p>
      {change !== undefined && change !== null ? (
        <div className="mt-2 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center text-xs font-mono font-medium px-2 py-0.5 rounded-md ${
              isPositive
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                : isNegative
                ? 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
                : 'bg-ink-border/50 text-ink-muted'
            }`}
          >
            {isPositive ? '↑ +' : isNegative ? '↓ -' : '— '}{Math.abs(change).toFixed(2)}%
          </span>
          <span className="text-[11px] text-ink-faint">vs 24h</span>
        </div>
      ) : helper ? (
        <p className="text-[11px] text-ink-faint mt-2 truncate">{helper}</p>
      ) : null}
    </div>
  );
}

export default MetricCard;
