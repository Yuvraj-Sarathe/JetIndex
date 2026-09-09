import { useDataQuality } from '../hooks/useDataQuality';
import DataTrustCard from '../components/DataTrustCard';

function DataQualityPage() {
  const { data, loading, error } = useDataQuality();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Data Quality Center</h2>
      
      {loading && (
        <div className="text-center py-12 text-slate-500">Loading data quality...</div>
      )}
      
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">
          Error loading data quality: {error}
        </div>
      )}
      
      {data && !loading && (
        <DataTrustCard data={data} />
      )}
    </div>
  );
}

export default DataQualityPage;
