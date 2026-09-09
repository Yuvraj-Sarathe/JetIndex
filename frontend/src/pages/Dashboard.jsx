import { useState } from 'react';
import MetricCard from '../components/MetricCard';
import ApixTrend from '../components/ApixTrend';
import Heatmap from '../components/Heatmap';
import ElasticityCurve from '../components/ElasticityCurve';
import UnbundlingInspector from '../components/UnbundlingInspector';
import BacktestChart from '../components/BacktestChart';
import ScrapedVsDGCA from '../components/ScrapedVsDGCA';
import TimeRangeFilter from '../components/TimeRangeFilter';
import ExportButton from '../components/ExportButton';
import { useApixDaily } from '../hooks/useApix';
import { formatPercent } from '../utils/format';

/**
 * The API's ApixDaily rows carry pct_change_dod (24h) but no 7-day change
 * and no data-quality rating field anywhere in the schema/DB — so 7d Δ% is
 * derived here from the daily series itself rather than invented.
 */
function getChangeOverDays(series, days) {
  if (!series || series.length === 0) return null;
  const latest = series[series.length - 1];
  if (latest?.apix == null) return null;
  const targetTime = new Date(latest.date).getTime() - days * 86400000;

  let past = null;
  for (let i = series.length - 1; i >= 0; i--) {
    if (new Date(series[i].date).getTime() <= targetTime) {
      past = series[i];
      break;
    }
  }
  if (!past || !past.apix) return null;
  return ((latest.apix - past.apix) / past.apix) * 100;
}

function Dashboard() {
  const [timeRange, setTimeRange] = useState({ from: null, to: null });
  const { data: dailyData, loading, error } = useApixDaily(timeRange);

  const latestValue = dailyData && dailyData.length > 0
    ? dailyData[dailyData.length - 1]
    : null;

  const change7d = getChangeOverDays(dailyData, 7);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <TimeRangeFilter onChange={setTimeRange} />
        <ExportButton data={dailyData} filename="apix-daily" />
      </div>

      {/* Loading / Error states */}
      {loading && (
        <div className="text-center py-12 text-slate-500">Loading...</div>
      )}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">
          Error loading data: {error}
        </div>
      )}

      {/* Metrics row */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <MetricCard
            label="APIx Today"
            value={latestValue?.apix?.toFixed(2) ?? '—'}
            change={latestValue?.pct_change_dod}
          />
          <MetricCard
            label="7-Day Δ%"
            value={formatPercent(change7d)}
          />
          <MetricCard
            label="Routes Tracked"
            value={latestValue?.n_routes ?? '—'}
          />
          <MetricCard
            label="Quotes Processed"
            value={latestValue?.n_quotes ?? '—'}
          />
          <MetricCard
            label="Last Updated"
            value={latestValue?.date ?? '—'}
          />
        </div>
      )}

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ApixTrend data={dailyData} />
        <Heatmap />
        <ElasticityCurve />
        <BacktestChart />
        <ScrapedVsDGCA />
      </div>

      {/* Unbundling inspector */}
      <UnbundlingInspector />
    </div>
  );
}

export default Dashboard;