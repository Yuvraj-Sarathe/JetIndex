/**
 * AnomalyFeed — Live anomaly stream with severity badges.
 */
const SEVERITY_COLORS = {
  LOW: 'bg-green-100 text-green-800',
  MEDIUM: 'bg-yellow-100 text-yellow-800',
  HIGH: 'bg-orange-100 text-orange-800',
  CRITICAL: 'bg-red-100 text-red-800',
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
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8 text-center">
        <p className="text-slate-500">No anomalies detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {anomalies.map((anomaly, idx) => (
        <div
          key={anomaly.anomaly_id || idx}
          className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{TYPE_ICONS[anomaly.type] || '❓'}</span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-900">{anomaly.route_code}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_COLORS[anomaly.severity] || 'bg-gray-100 text-gray-800'}`}>
                    {anomaly.severity}
                  </span>
                  <span className="text-xs text-slate-500">{anomaly.type?.replace(/_/g, ' ')}</span>
                </div>
                <p className="text-sm text-slate-600 mt-1">{anomaly.description}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">₹{anomaly.detected_value?.toLocaleString()}</p>
              {anomaly.z_score && (
                <p className="text-xs text-slate-500">z-score: {anomaly.z_score}</p>
              )}
            </div>
          </div>
          {anomaly.expected_range && (
            <div className="mt-2 text-xs text-slate-500">
              Expected: ₹{anomaly.expected_range[0]?.toLocaleString()} – ₹{anomaly.expected_range[1]?.toLocaleString()}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default AnomalyFeed;
