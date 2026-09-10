/**
 * MetricCard — displays a single headline metric with optional change indicator.
 */
function MetricCard({ label, value, change, helper, badge, isPublished }) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <div className={`bg-card border rounded-xl p-4 transition-all duration-200 group relative overflow-hidden ${
      isPublished 
        ? 'border-primary/40 bg-card shadow-[0_0_20px_rgba(250,255,105,0.06)]' 
        : 'border-hairline hover:border-hairline-strong'
    }`}>
      {isPublished && (
        <div className="absolute top-0 right-0 w-16 h-16 pointer-events-none overflow-hidden">
          <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-primary animate-ping"></div>
        </div>
      )}
      <div className="flex items-start justify-between mb-1.5 gap-2 min-h-[20px]">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-muted group-hover:text-white transition-colors leading-tight">
          {label}
        </p>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {badge && (
            <span className="text-[9px] font-mono uppercase font-bold px-1.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/30 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              {badge}
            </span>
          )}
          {helper && (
            <span className="text-[10px] text-ink-faint border border-hairline rounded px-1 cursor-help hover:text-white hover:border-hairline-strong" title={helper}>
              ?
            </span>
          )}
        </div>
      </div>
      <p className={`text-2xl lg:text-3xl font-bold font-mono tabular-nums tracking-tight ${isPublished ? 'text-primary' : 'text-white'}`}>
        {value}
      </p>
      {change !== undefined && change !== null ? (
        <div className="mt-2 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center text-xs font-mono font-medium px-2 py-0.5 rounded-md ${
              isPositive
                ? 'bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/20'
                : isNegative
                ? 'bg-accent-rose/15 text-accent-rose border border-accent-rose/20'
                : 'bg-card-elevated text-ink-muted border border-hairline'
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
