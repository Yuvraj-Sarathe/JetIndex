import { useAnomalies } from '../hooks/useAnomalies';
import AnomalyFeed from '../components/AnomalyFeed';

function AnomaliesPage() {
  const { data, loading, error } = useAnomalies();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Market Anomalies</h2>
      
      {loading && (
        <div className="text-center py-12 text-slate-500">Loading anomalies...</div>
      )}
      
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">
          Error loading anomalies: {error}
        </div>
      )}
      
      {data && !loading && (
        <>
          {/* Summary */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <p className="text-sm text-slate-500">
              Detected <span className="font-semibold text-slate-900">{data.count}</span> anomalies
              {data.as_of_date && ` as of ${data.as_of_date}`}
            </p>
          </div>

          {/* Anomaly Feed */}
          <AnomalyFeed anomalies={data.anomalies} />
        </>
      )}
    </div>
  );
}

export default AnomaliesPage;
