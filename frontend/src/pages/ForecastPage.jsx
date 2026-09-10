import { useForecast } from '../hooks/useForecast';
import ForecastChart from '../components/ForecastChart';

function ForecastPage() {
  const { data, loading, error } = useForecast(14);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">National Airfare Forward Forecast</h2>
          <p className="text-xs text-ink-muted">Gradient boosted time-series projection with 95% Bayesian confidence bounds</p>
        </div>
        {data && (
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-card border border-ink-border text-accent-lime">
            Horizon: T+{data.horizon_days} Days
          </span>
        )}
      </div>
      
      {loading && (
        <div className="text-center py-16 bg-card border border-ink-border rounded-xl">
          <div className="w-8 h-8 border-2 border-accent-violet border-t-accent-lime rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-medium text-white">Generating forward econometric projections...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">
          Error loading forecast: {error}
        </div>
      )}
      
      {data && !loading && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card border border-ink-border rounded-xl p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1">Current Index</p>
              <p className="text-3xl font-bold text-white font-mono tabular-nums">{data.current_index}</p>
              <p className="text-[11px] text-ink-faint mt-1">Base Laspeyres reading</p>
            </div>
            <div className="bg-card border border-ink-border rounded-xl p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1">Mean Forecast</p>
              <p className="text-3xl font-bold text-accent-lime font-mono tabular-nums">{data.mean_forecast}</p>
              <p className="text-[11px] text-ink-faint mt-1">Projected average across horizon</p>
            </div>
            <div className="bg-card border border-ink-border rounded-xl p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1">Transport CPI Impact</p>
              <p className="text-3xl font-bold text-accent-pink font-mono tabular-nums">{data.net_transport_bps} bps</p>
              <p className="text-[11px] text-ink-faint mt-1">Contribution to monthly basket</p>
            </div>
            <div className="bg-card border border-ink-border rounded-xl p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1">Policy Alert Level</p>
              <div className="mt-1 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-accent-lime"></span>
                <p className="text-xl font-bold text-white capitalize font-mono">{data.alert_level?.replace(/_/g, ' ') || 'Normal'}</p>
              </div>
              <p className="text-[11px] text-ink-faint mt-1">MoSPI volatility threshold</p>
            </div>
          </div>

          {/* Forecast Chart */}
          <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">
                {data.horizon_days}-Day Probabilistic Trajectory
              </h3>
              <p className="text-xs text-ink-muted">Shaded area represents the 95% confidence interval under simulated demand shocks</p>
            </div>
            <ForecastChart data={data.steps} />
          </div>
        </>
      )}
    </div>
  );
}

export default ForecastPage;
