/**
 * DataTrustCard — 0-100 gauge with 7-dimension breakdown.
 */
const DIMENSION_LABELS = {
  freshness: 'Freshness',
  completeness: 'Completeness',
  route_coverage: 'Route Coverage',
  source_health: 'Source Health',
  duplicate_rate: 'Duplicate Prevention',
  outlier_rate: 'Outlier Cleanliness',
  validation_success: 'Validation Success',
};

const DIMENSION_KEYS = ['freshness', 'completeness', 'route_coverage', 'source_health', 'duplicate_rate', 'outlier_rate', 'validation_success'];

function getRatingColor(rating) {
  switch (rating) {
    case 'A+': return '#10b981';
    case 'A': return '#22c55e';
    case 'B': return '#eab308';
    case 'C': return '#f97316';
    case 'D': return '#ef4444';
    default: return '#94a3b8';
  }
}

function getScoreColor(score) {
  if (score >= 90) return '#10b981';
  if (score >= 80) return '#22c55e';
  if (score >= 70) return '#eab308';
  if (score >= 60) return '#f97316';
  return '#ef4444';
}

function DataTrustCard({ data }) {
  if (!data) {
    return <div className="text-center py-8 text-slate-500">No data quality data</div>;
  }

  const score = data.overall_score || 0;
  const rating = data.rating || 'N/A';
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Gauge */}
        <div className="flex flex-col items-center">
          <svg width="140" height="140" viewBox="0 0 120 120">
            {/* Background circle */}
            <circle
              cx="60"
              cy="60"
              r="45"
              fill="none"
              stroke="#e2e8f0"
              strokeWidth="10"
            />
            {/* Score arc */}
            <circle
              cx="60"
              cy="60"
              r="45"
              fill="none"
              stroke={getScoreColor(score)}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              transform="rotate(-90 60 60)"
            />
            {/* Score text */}
            <text x="60" y="55" textAnchor="middle" fontSize="24" fontWeight="bold" fill="#1e293b">
              {score.toFixed(1)}
            </text>
            <text x="60" y="72" textAnchor="middle" fontSize="12" fill="#64748b">
              {rating}
            </text>
          </svg>
          <p className="mt-2 text-sm font-medium text-slate-700">Data Trust Score</p>
        </div>

        {/* Dimension bars */}
        <div className="flex-1 space-y-3">
          {DIMENSION_KEYS.map((key) => {
            const value = data[key] || 0;
            // For duplicate_rate and outlier_rate, lower is better
            const displayValue = (key === 'duplicate_rate' || key === 'outlier_rate')
              ? Math.max(0, 100 - value)
              : value;
            
            return (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">{DIMENSION_LABELS[key]}</span>
                  <span className="font-medium text-slate-900">{displayValue.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${displayValue}%`,
                      backgroundColor: getScoreColor(displayValue),
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {data.as_of_date && (
        <p className="mt-4 text-xs text-slate-400 text-right">As of {data.as_of_date}</p>
      )}
    </div>
  );
}

export default DataTrustCard;
