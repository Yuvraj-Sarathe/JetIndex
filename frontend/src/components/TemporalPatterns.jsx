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
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Day-of-Week Demand Pattern</h3>
        <div className="grid grid-cols-7 gap-2">
          {dow.map((d) => {
            const barHeight = Math.round(d.multiplier * 80);
            const isPeak = d.multiplier >= 1.15;
            return (
              <div key={d.day} className="flex flex-col items-center">
                <div className="text-xs font-mono mb-1">{d.multiplier?.toFixed(2)}x</div>
                <div className={`w-full rounded-t ${isPeak ? 'bg-red-400' : d.multiplier < 1.0 ? 'bg-green-400' : 'bg-blue-400'}`}
                  style={{ height: `${barHeight}px` }} />
                <p className="text-xs text-slate-600 mt-1 text-center">{d.day?.slice(0, 3)}</p>
                <p className="text-[10px] text-slate-400 text-center leading-tight">{d.avg_fare_delta_pct > 0 ? '+' : ''}{d.avg_fare_delta_pct}%</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Advance Booking Yield Curve */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Advance Booking Yield Curve</h3>
        <div className="space-y-3">
          {horizon.map((h) => (
            <div key={h.horizon} className="flex items-center gap-4">
              <span className="w-12 text-sm font-mono font-bold text-slate-900">{h.horizon}</span>
              <div className="flex-1 bg-slate-100 rounded-full h-6 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-end pr-2"
                  style={{ width: `${Math.min(100, (h.average_multiplier / 3.0) * 100)}%` }}>
                  <span className="text-xs text-white font-mono font-bold">{h.average_multiplier?.toFixed(2)}x</span>
                </div>
              </div>
              <span className="text-xs text-slate-500 w-32">{h.name}</span>
              <span className="text-xs text-slate-400 w-20 text-right">σ {h.volatility_pct}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Seasonal Quarters */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Seasonal Quarterly Factors</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {seasonal.map((s) => (
            <div key={s.quarter} className="p-4 rounded-lg border border-slate-200">
              <p className="text-sm font-medium text-slate-900">{s.quarter}</p>
              <p className="text-xs text-slate-500 mb-2">{s.name}</p>
              <p className="text-2xl font-bold text-slate-900">{s.seasonal_factor?.toFixed(2)}x</p>
              <p className={`text-xs mt-1 ${s.inflation_impact?.includes('Critical') ? 'text-red-600' : s.inflation_impact?.includes('Elevated') ? 'text-orange-600' : 'text-green-600'}`}>
                {s.inflation_impact}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
