/**
 * AnomalyFeed — Live anomaly stream with severity badges.
 */
const SEVERITY_COLORS = {
  LOW: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  MEDIUM: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  HIGH: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
  CRITICAL: 'bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse',
};

const TYPE_ICONS = {
  PRICE_SPIKE: '📈',
  PRICE_DROP: '📉',
  HORIZON_INVERSION: '🔄',
  CORRIDOR_DIVERGENCE: '🔀',
  SOURCE_DISAGREEMENT: '⚠️',
};

function AnomalyFeed({ anomalies }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-8 text-center">
        <p className="text-ink-muted text-sm">No active volatility anomalies detected across 20 DGCA corridors.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {anomalies.map((anomaly, idx) => (
        <div
          key={anomaly.anomaly_id || idx}
          className="bg-card rounded-xl border border-ink-border p-4 hover:border-accent-violet/60 transition-all group"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl p-2 rounded-lg bg-card-elevated border border-ink-border/80">
                {TYPE_ICONS[anomaly.type] || '❓'}
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono font-bold text-white text-sm">{anomaly.route_code}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${SEVERITY_COLORS[anomaly.severity] || 'bg-canvas text-ink-muted'}`}>
                    {anomaly.severity}
                  </span>
                  <span className="text-xs font-mono text-accent-cyan uppercase tracking-wider">
                    {anomaly.type?.replace(/_/g, ' ')}
                  </span>
                </div>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">{anomaly.description}</p>
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-base font-mono font-bold text-accent-lime">₹{anomaly.detected_value?.toLocaleString()}</p>
              {anomaly.z_score && (
                <p className="text-[11px] font-mono text-ink-faint">z-score: {anomaly.z_score}</p>
              )}
            </div>
          </div>
          {anomaly.expected_range && (
            <div className="mt-2.5 pt-2.5 border-t border-ink-border/40 text-[11px] font-mono text-ink-faint flex items-center justify-between">
              <span>Expected Range: ₹{anomaly.expected_range[0]?.toLocaleString()} – ₹{anomaly.expected_range[1]?.toLocaleString()}</span>
              <span className="text-accent-violet">Statistical Bound: ±2.5σ</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default AnomalyFeed;
