import { useAlerts } from '../hooks/useAlerts';

function severityColor(severity) {
  switch (severity) {
    case 'CRITICAL': return 'bg-rose-500/15 text-rose-300 border-rose-500/40';
    case 'HIGH': return 'bg-orange-500/15 text-orange-300 border-orange-500/40';
    case 'MEDIUM': return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
    default: return 'bg-accent-violet/15 text-accent-lime border-accent-violet/40';
  }
}

function statusIcon(status) {
  if (status === 'ACTIVE') return '🔴';
  if (status === 'ACK') return '🟡';
  return '🟢';
}

export default function AlertFeed() {
  const { rules, liveAlerts, loading, error } = useAlerts();

  if (loading) return (
    <div className="text-center py-16 bg-card border border-ink-border rounded-xl">
      <div className="w-8 h-8 border-2 border-accent-violet border-t-accent-lime rounded-full animate-spin mx-auto mb-3"></div>
      <p className="text-sm font-medium text-white">Connecting to real-time statutory alert engine...</p>
    </div>
  );
  if (error) return <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">{error}</div>;

  return (
    <div className="space-y-6">
      {/* Active Alerts */}
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-white">Live Policy & Threat Feed</h3>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/40 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-lime animate-pulse"></span>
            ACTIVE MONITORING
          </span>
        </div>
        {liveAlerts?.alerts?.length === 0 ? (
          <p className="text-ink-muted text-xs py-4">No active threshold breaches or policy alarms.</p>
        ) : (
          <div className="space-y-2.5">
            {liveAlerts?.alerts?.map((alert) => (
              <div key={alert.alert_id} className={`flex items-center justify-between p-3.5 rounded-xl border ${severityColor(alert.severity)} bg-card-elevated/40`}>
                <div className="flex items-center gap-3">
                  <span className="text-base">{statusIcon(alert.status)}</span>
                  <div>
                    <p className="font-medium text-sm text-white">{alert.title}</p>
                    <p className="text-[11px] font-mono text-ink-muted">{alert.alert_id}</p>
                  </div>
                </div>
                <span className="text-xs font-mono text-ink-faint">{alert.triggered_at?.split('T')[0]}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Rules */}
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Statutory Surveillance Rules</h3>
            <p className="text-xs text-ink-muted">Configured thresholds for headline inflation, corridor spreads, and scrape parity</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm font-mono text-xs">
            <thead>
              <tr className="border-b border-ink-border text-left uppercase text-[11px] tracking-wider text-ink-faint">
                <th className="pb-3 pr-4 font-sans">Rule Name</th>
                <th className="pb-3 pr-4">Metric Target</th>
                <th className="pb-3 pr-4">Condition</th>
                <th className="pb-3 pr-4">Threshold</th>
                <th className="pb-3 pr-4">Severity</th>
                <th className="pb-3">Enabled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-border/40">
              {rules?.rules?.map((rule) => (
                <tr key={rule.rule_id} className="hover:bg-card-hover transition-colors">
                  <td className="py-3 pr-4 font-sans font-medium text-white">{rule.rule_name}</td>
                  <td className="py-3 pr-4 text-accent-cyan">{rule.metric_target}</td>
                  <td className="py-3 pr-4 text-ink-muted">{rule.condition}</td>
                  <td className="py-3 pr-4 text-white font-bold">{rule.threshold}</td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${severityColor(rule.severity)}`}>
                      {rule.severity}
                    </span>
                  </td>
                  <td className="py-3 text-accent-lime font-bold">{rule.is_enabled ? '✓ ACTIVE' : '— OFF'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
