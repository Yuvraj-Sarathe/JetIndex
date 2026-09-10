import { useAnomalies } from '../hooks/useAnomalies';
import AnomalyFeed from '../components/AnomalyFeed';

function AnomaliesPage() {
  const { data, loading, error } = useAnomalies();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Market Spike Anomalies & Surveillance</h2>
          <p className="text-xs text-ink-muted">Algorithmic divergence detection across price spikes, yield inversions, and route corridors</p>
        </div>
        {data && (
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-card border border-ink-border text-accent-pink">
            {data.count} Active Anomal{data.count === 1 ? 'y' : 'ies'}
          </span>
        )}
      </div>
      
      {loading && (
        <div className="text-center py-16 bg-card border border-ink-border rounded-xl">
          <div className="w-8 h-8 border-2 border-accent-violet border-t-accent-lime rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-medium text-white">Scanning cross-corridor telemetry for statistical outliers...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">
          Error loading anomalies: {error}
        </div>
      )}
      
      {data && !loading && (
        <>
          {/* Summary */}
          <div className="bg-card border border-ink-border rounded-xl p-4 flex items-center justify-between">
            <p className="text-xs text-ink-muted">
              Active corridor surveillance state: <span className="font-semibold text-white font-mono">{data.count} anomalies detected</span>
              {data.as_of_date && ` as of published sweep date ${data.as_of_date}`}
            </p>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-accent-violet/20 text-accent-lime border border-accent-violet/40">
              Confidence: 99.5%
            </span>
          </div>

          {/* Anomaly Feed */}
          <AnomalyFeed anomalies={data.anomalies} />
        </>
      )}
    </div>
  );
}

export default AnomaliesPage;
