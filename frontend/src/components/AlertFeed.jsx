import { useAlerts } from '../hooks/useAlerts';

function severityColor(severity) {
  switch (severity) {
    case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-300';
    case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-300';
    case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    default: return 'bg-blue-100 text-blue-800 border-blue-300';
  }
}

function statusIcon(status) {
  if (status === 'ACTIVE') return '🔴';
  if (status === 'ACK') return '🟡';
  return '🟢';
}

export default function AlertFeed() {
  const { rules, liveAlerts, loading, error } = useAlerts();

  if (loading) return <div className="text-center py-8 text-slate-400">Loading alerts...</div>;
  if (error) return <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>;

  return (
    <div className="space-y-6">
      {/* Active Alerts */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Live Threat Feed</h3>
        {liveAlerts?.alerts?.length === 0 ? (
          <p className="text-slate-500 text-sm">No active alerts.</p>
        ) : (
          <div className="space-y-3">
            {liveAlerts?.alerts?.map((alert) => (
              <div key={alert.alert_id} className={`flex items-center justify-between p-3 rounded-lg border ${severityColor(alert.severity)}`}>
                <div className="flex items-center gap-3">
                  <span>{statusIcon(alert.status)}</span>
                  <div>
                    <p className="font-medium text-sm">{alert.title}</p>
                    <p className="text-xs opacity-75">{alert.alert_id}</p>
                  </div>
                </div>
                <span className="text-xs font-mono opacity-60">{alert.triggered_at?.split('T')[0]}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Rules */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Alert Rules</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4">Rule</th>
                <th className="pb-2 pr-4">Metric</th>
                <th className="pb-2 pr-4">Condition</th>
                <th className="pb-2 pr-4">Threshold</th>
                <th className="pb-2 pr-4">Severity</th>
                <th className="pb-2">Enabled</th>
              </tr>
            </thead>
            <tbody>
              {rules?.rules?.map((rule) => (
                <tr key={rule.rule_id} className="border-b border-slate-100">
                  <td className="py-2 pr-4 font-medium">{rule.rule_name}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{rule.metric_target}</td>
                  <td className="py-2 pr-4">{rule.condition}</td>
                  <td className="py-2 pr-4 font-mono">{rule.threshold}</td>
                  <td className="py-2 pr-4"><span className={`px-2 py-0.5 rounded text-xs font-medium ${severityColor(rule.severity)}`}>{rule.severity}</span></td>
                  <td className="py-2">{rule.is_enabled ? '✅' : '❌'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
