import { useTemporal } from '../hooks/useTemporal';

export default function TemporalPatterns() {
  const { data, loading, error } = useTemporal();

  if (loading) return <div className="text-center py-8 text-slate-400">Loading temporal data...</div>;
  if (error) return <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>;

  const dow = data?.day_of_week_dynamics || [];
  const horizon = data?.advance_booking_yield_curve || [];
  const seasonal = data?.seasonal_quarterly_factors || [];

  return (
    <div className="space-y-6">
      {/* Day of Week */}
      <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Day-of-Week Fare Dynamics</h3>
            <p className="text-xs text-ink-muted">Statistical demand multipliers relative to mid-week baseline</p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-card text-primary border border-hairline">
            Baseline: 1.00x
          </span>
        </div>
        <div className="grid grid-cols-7 gap-3 pt-4">
          {dow.map((d) => {
            const barHeight = Math.round(d.multiplier * 75);
            const isPeak = d.multiplier >= 1.15;
            return (
              <div key={d.day} className="flex flex-col items-center">
                <div className="text-xs font-mono font-bold text-white mb-1.5">{d.multiplier?.toFixed(2)}x</div>
                <div className="w-full bg-canvas/60 rounded-t h-24 flex items-end p-1">
                  <div
                    className={`w-full rounded-t transition-all ${
                      isPeak ? 'bg-accent-rose shadow-[0_0_12px_rgba(239,68,68,0.3)]' : d.multiplier < 1.0 ? 'bg-accent-emerald shadow-[0_0_12px_rgba(34,197,94,0.3)]' : 'bg-primary'
                    }`}
                    style={{ height: `${barHeight}px` }}
                  />
                </div>
                <p className="text-xs font-mono font-bold text-white mt-2 text-center uppercase">{d.day?.slice(0, 3)}</p>
                <p className={`text-[11px] font-mono text-center mt-0.5 ${d.avg_fare_delta_pct > 0 ? 'text-accent-rose' : 'text-accent-emerald'}`}>
                  {d.avg_fare_delta_pct > 0 ? '+' : ''}{d.avg_fare_delta_pct}%
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Advance Booking Yield Curve */}
      <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Advance Booking Yield Curve</h3>
            <p className="text-xs text-ink-muted">Empirical price progression by departure proximity window</p>
          </div>
        </div>
        <div className="space-y-3">
          {horizon.map((h) => (
            <div key={h.horizon} className="flex items-center gap-4 bg-card-elevated/40 border border-hairline p-2.5 rounded-xl">
              <span className="w-12 text-xs font-mono font-bold text-primary">{h.horizon}</span>
              <div className="flex-1 bg-canvas rounded-full h-5 overflow-hidden p-0.5 border border-hairline">
                <div
                  className="h-full rounded-full bg-primary flex items-center justify-end pr-2 transition-all"
                  style={{ width: `${Math.min(100, (h.average_multiplier / 3.0) * 100)}%` }}
                >
                  <span className="text-[10px] text-black font-mono font-bold">{h.average_multiplier?.toFixed(2)}x</span>
                </div>
              </div>
              <span className="text-xs text-ink-muted w-32 truncate">{h.name}</span>
              <span className="text-xs font-mono text-ink-faint w-20 text-right">σ {h.volatility_pct}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Seasonal Quarters */}
      <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Seasonal Quarterly Multipliers</h3>
            <p className="text-xs text-ink-muted">Quarterly seasonality factors across India&apos;s domestic aviation calendar</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {seasonal.map((s) => (
            <div key={s.quarter} className="p-4 rounded-xl bg-card-elevated border border-hairline">
              <div className="flex items-center justify-between">
                <p className="text-xs font-mono uppercase font-bold text-accent-blue">{s.quarter}</p>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  s.inflation_impact?.includes('Critical') ? 'bg-accent-rose/20 text-accent-rose' : s.inflation_impact?.includes('Elevated') ? 'bg-amber-500/20 text-amber-300' : 'bg-accent-emerald/20 text-accent-emerald'
                }`}>
                  {s.inflation_impact}
                </span>
              </div>
              <p className="text-xs text-ink-muted mt-1 truncate">{s.name}</p>
              <p className="text-2xl font-mono font-bold text-white mt-2">{s.seasonal_factor?.toFixed(2)}x</p>
              <p className="text-[11px] text-ink-faint mt-1 font-mono">Quarterly multiplier</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
