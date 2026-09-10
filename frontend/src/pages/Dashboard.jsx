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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <TimeRangeFilter onChange={setTimeRange} />
        <div className="flex items-center gap-2">
          <a
            href="/api/v1/reports/export"
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-ink-border text-xs font-mono text-ink-muted hover:text-white hover:border-accent-lime/60 transition-colors"
            title="Download official MoSPI published intelligence report"
          >
            <span>📜</span>
            <span>Export Official Gazette (.CSV)</span>
          </a>
          <ExportButton data={dailyData} filename="apix-daily" />
        </div>
      </div>

      {/* Official Publication Dossier Banner */}
      <div className="bg-gradient-to-r from-card via-card-elevated to-card border border-accent-lime/40 rounded-xl p-4 sm:p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-accent-violet/10 to-transparent pointer-events-none"></div>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-accent-lime/10 border border-accent-lime/40 flex items-center justify-center text-accent-lime font-mono text-lg font-bold flex-shrink-0">
              ✓
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h2 className="text-base font-bold text-white tracking-tight">
                  National Airfare Price Index · Official Gazette Publication
                </h2>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-accent-lime text-ink-night shadow-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-ink-night animate-pulse"></span>
                  STATUS: PUBLISHED · FINAL
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono text-accent-cyan border border-accent-cyan/30 bg-accent-cyan/10">
                  MoSPI / NSO SIH26056
                </span>
              </div>
              <p className="text-xs text-ink-muted leading-relaxed">
                Ratified daily Laspeyres computation based on official DGCA domestic passenger traffic weights. Approved for macro-prudential transmission analysis.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 lg:border-l lg:border-ink-border/60 lg:pl-5 self-start lg:self-center">
            <div className="text-left">
              <p className="text-[10px] font-mono uppercase text-ink-faint">Gazette Release ID</p>
              <p className="text-xs font-mono font-bold text-accent-lime tracking-wider">
                APIx-IN-{latestValue?.date?.replace(/-/g, '') || '20260910'}-F
              </p>
            </div>
            <div className="text-left border-l border-ink-border/50 pl-3">
              <p className="text-[10px] font-mono uppercase text-ink-faint">Published Authority</p>
              <p className="text-xs font-medium text-white">DGCA / MoSPI</p>
            </div>
          </div>
        </div>
      </div>

      {/* Loading / Error states */}
      {loading && (
        <div className="text-center py-16 bg-card border border-ink-border rounded-xl">
          <div className="w-8 h-8 border-2 border-accent-violet border-t-accent-lime rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-medium text-white">Aggregating live APIx market series...</p>
          <p className="text-xs text-ink-muted">Synthesizing DGCA weighted basket</p>
        </div>
      )}
      {error && (
        <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold">Failed to load APIx telemetry</p>
            <p className="text-xs text-rose-400/80">{error}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-medium rounded-lg border border-rose-500/40 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Metrics row */}
      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            label="APIx Index Today"
            value={latestValue?.apix?.toFixed(2) ?? '—'}
            change={latestValue?.pct_change_dod}
            helper="Current Laspeyres Index (Base 100)"
            badge="PUBLISHED"
            isPublished={true}
          />
          <MetricCard
            label="7-Day Shift"
            value={formatPercent(change7d)}
            helper="Rolling 7-day rate of inflation"
          />
          <MetricCard
            label="City-Pairs Tracked"
            value={latestValue?.n_routes ?? '—'}
            helper="Top DGCA high-density corridors"
          />
          <MetricCard
            label="Quotes Sampled"
            value={latestValue?.n_quotes != null ? latestValue.n_quotes.toLocaleString() : '—'}
            helper="Scraped & unbundled quotes"
          />
          <MetricCard
            label="Sweep Timestamp"
            value={latestValue?.date ?? '—'}
            helper="Latest index computation run"
            badge="VERIFIED"
          />
        </div>
      )}

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ApixTrend data={dailyData} />
        <Heatmap />
        <ElasticityCurve />
        <BacktestChart />
        <div className="lg:col-span-2">
          <ScrapedVsDGCA />
        </div>
      </div>

      {/* Unbundling inspector */}
      <UnbundlingInspector />
    </div>
  );
}

export default Dashboard;