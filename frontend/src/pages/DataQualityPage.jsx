import { useDataQuality } from '../hooks/useDataQuality';
import DataTrustCard from '../components/DataTrustCard';

function DataQualityPage() {
  const { data, loading, error } = useDataQuality();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Data Quality & Trust Governance</h2>
          <p className="text-xs text-ink-muted">7-dimension integrity evaluation across ingestion pipelines and scrapers</p>
        </div>
      </div>
      
      {loading && (
        <div className="text-center py-16 bg-card border border-ink-border rounded-xl">
          <div className="w-8 h-8 border-2 border-accent-violet border-t-accent-lime rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-medium text-white">Auditing ingestion freshness and outlier rates...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">
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
