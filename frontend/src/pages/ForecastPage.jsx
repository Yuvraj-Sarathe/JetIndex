import { useForecast } from '../hooks/useForecast';
import ForecastChart from '../components/ForecastChart';

function ForecastPage() {
  const { data, loading, error } = useForecast(14);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">National Airfare Forecast</h2>
      
      {loading && (
        <div className="text-center py-12 text-slate-500">Loading forecast...</div>
      )}
      
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">
          Error loading forecast: {error}
        </div>
      )}
      
      {data && !loading && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
              <p className="text-sm text-slate-500">Current Index</p>
              <p className="text-2xl font-bold text-slate-900">{data.current_index}</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
              <p className="text-sm text-slate-500">Mean Forecast</p>
              <p className="text-2xl font-bold text-blue-600">{data.mean_forecast}</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
              <p className="text-sm text-slate-500">Transport Impact</p>
              <p className="text-2xl font-bold text-amber-600">{data.net_transport_bps} bps</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
              <p className="text-sm text-slate-500">Alert Level</p>
              <p className="text-lg font-semibold text-slate-700">{data.alert_level?.replace(/_/g, ' ')}</p>
            </div>
          </div>

          {/* Forecast Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
            <h3 className="text-lg font-medium text-slate-900 mb-4">
              {data.horizon_days}-Day Forward Forecast
            </h3>
            <ForecastChart data={data.steps} />
          </div>
        </>
      )}
    </div>
  );
}

export default ForecastPage;
