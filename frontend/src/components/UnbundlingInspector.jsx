import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getQuotes } from '../api/client';

const CARRIER_NAMES = {
  '6E': 'IndiGo',
  'AI': 'Air India',
  'QP': 'Akasa Air',
  'SG': 'SpiceJet',
  'UK': 'Vistara',
  'IX': 'Air India Express',
  'G8': 'Go First',
  'I5': 'AIX Connect',
};

// Refined, feasible financial & aviation color palette
const COMPONENT_CONFIG = {
  base_fare: {
    label: 'Base Fare',
    color: '#4f46e5', // Deep Indigo
    desc: 'Core airline inventory tariff',
  },
  udf: {
    label: 'Airport UDF',
    color: '#0284c7', // Sky Blue
    desc: 'Airport User Development Fee',
  },
  taxes: {
    label: 'Statutory Taxes',
    color: '#f59e0b', // Warm Amber Gold
    desc: 'GST and government regulatory levies',
  },
  convenience_fee: {
    label: 'Convenience Fee',
    color: '#f43f5e', // Coral Rose
    desc: 'Online ticketing & payment processing',
  },
  other_fees: {
    label: 'Other Surcharges',
    color: '#8b5cf6', // Muted Violet
    desc: 'Fuel, baggage & miscellaneous ancillaries',
  },
};

/**
 * Custom Tooltip for stacked unbundling bars
 */
function CustomUnbundlingTooltip({ active, payload, label, viewMode }) {
  if (!active || !payload || !payload.length) return null;

  const carrierName = CARRIER_NAMES[label] || label;
  const total = payload.reduce((sum, item) => sum + (Number(item.value) || 0), 0);

  return (
    <div className="bg-[#18112b]/95 backdrop-blur-md border border-[#3b3260] rounded-xl p-3.5 shadow-2xl min-w-[240px] text-xs">
      <div className="flex items-center justify-between border-b border-ink-border/50 pb-2 mb-2.5">
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold text-white bg-white/10 px-1.5 py-0.5 rounded text-[11px]">
            {label}
          </span>
          <span className="font-semibold text-white">{carrierName}</span>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Avg Total</span>
          <span className="font-mono font-bold text-white text-sm">
            {viewMode === 'percent' ? '100%' : `₹${Math.round(total).toLocaleString('en-IN')}`}
          </span>
        </div>
      </div>

      <div className="space-y-1.5">
        {payload.slice().reverse().map((entry) => {
          const cfg = COMPONENT_CONFIG[entry.dataKey] || { label: entry.name, color: entry.color };
          const val = Number(entry.value) || 0;
          const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0.0';

          return (
            <div key={entry.dataKey} className="flex items-center justify-between gap-3 py-0.5">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-sm shrink-0"
                  style={{ backgroundColor: cfg.color }}
                />
                <span className="text-ink-muted">{cfg.label}</span>
              </div>
              <div className="font-mono text-right flex items-center gap-2">
                <span className="text-white font-medium">
                  {viewMode === 'percent' ? `${val.toFixed(1)}%` : `₹${Math.round(val).toLocaleString('en-IN')}`}
                </span>
                {viewMode !== 'percent' && (
                  <span className="text-[10px] text-ink-muted w-10 text-right">
                    ({pct}%)
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * UnbundlingInspector — stacked bar + table showing base/udf/taxes/conv/other by carrier.
 * Redesigned with sleek, thinner bars, feasible palette, share toggle, and breakdown summary.
 */
function UnbundlingInspector() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('rupees'); // 'rupees' | 'percent'

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getQuotes({ limit: 50 })
      .then((res) => {
        if (!cancelled) setQuotes(res || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Carrier Fare Unbundling Inspector</h3>
        <p className="text-xs text-ink-muted">Decomposing carrier ancillary breakdowns...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Carrier Fare Unbundling Inspector</h3>
        <p className="text-xs text-rose-400">Error: {error}</p>
      </div>
    );
  }

  // Aggregate by carrier
  const byCarrier = {};
  quotes.forEach((q) => {
    if (!byCarrier[q.carrier]) {
      byCarrier[q.carrier] = { base_fare: 0, udf: 0, taxes: 0, convenience_fee: 0, other_fees: 0, count: 0 };
    }
    byCarrier[q.carrier].base_fare += q.base_fare || 0;
    byCarrier[q.carrier].udf += q.udf || 0;
    byCarrier[q.carrier].taxes += q.taxes || 0;
    byCarrier[q.carrier].convenience_fee += q.convenience_fee || 0;
    byCarrier[q.carrier].other_fees += q.other_fees || 0;
    byCarrier[q.carrier].count += 1;
  });

  // Average per carrier & normalized share calculation
  const carriers = Object.entries(byCarrier).map(([carrier, totals]) => {
    const base = totals.base_fare / totals.count;
    const udf = totals.udf / totals.count;
    const taxes = totals.taxes / totals.count;
    const conv = totals.convenience_fee / totals.count;
    const other = totals.other_fees / totals.count;
    const total = base + udf + taxes + conv + other;

    return {
      carrier,
      carrierName: CARRIER_NAMES[carrier] || carrier,
      base_fare: base,
      udf,
      taxes,
      convenience_fee: conv,
      other_fees: other,
      total,
      // Normalized % shares for 'percent' mode
      base_fare_pct: total > 0 ? (base / total) * 100 : 0,
      udf_pct: total > 0 ? (udf / total) * 100 : 0,
      taxes_pct: total > 0 ? (taxes / total) * 100 : 0,
      convenience_fee_pct: total > 0 ? (conv / total) * 100 : 0,
      other_fees_pct: total > 0 ? (other / total) * 100 : 0,
      ancillary_pct: total > 0 ? ((total - base) / total) * 100 : 0,
      count: totals.count,
    };
  });

  // Calculate market-wide averages
  const overall = carriers.reduce(
    (acc, c) => {
      acc.total += c.total;
      acc.base += c.base_fare;
      acc.ancillaries += (c.total - c.base_fare);
      return acc;
    },
    { total: 0, base: 0, ancillaries: 0 }
  );

  const avgBaseRatio = overall.total > 0 ? ((overall.base / overall.total) * 100).toFixed(1) : 0;
  const avgAncillaryRatio = overall.total > 0 ? ((overall.ancillaries / overall.total) * 100).toFixed(1) : 0;

  // Chart data based on selected mode
  const chartData = carriers.map((c) => {
    if (viewMode === 'percent') {
      return {
        carrier: c.carrier,
        base_fare: Number(c.base_fare_pct.toFixed(1)),
        udf: Number(c.udf_pct.toFixed(1)),
        taxes: Number(c.taxes_pct.toFixed(1)),
        convenience_fee: Number(c.convenience_fee_pct.toFixed(1)),
        other_fees: Number(c.other_fees_pct.toFixed(1)),
      };
    }
    return {
      carrier: c.carrier,
      base_fare: Math.round(c.base_fare),
      udf: Math.round(c.udf),
      taxes: Math.round(c.taxes),
      convenience_fee: Math.round(c.convenience_fee),
      other_fees: Math.round(c.other_fees),
    };
  });

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      {/* Header section with view toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-base font-semibold text-white">Carrier Fare Unbundling Inspector</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-violet/15 text-accent-violet border border-accent-violet/40">
              DGCA REVENUE DECOMPOSITION
            </span>
          </div>
          <p className="text-xs text-ink-muted mt-0.5">
            Audit of base passenger tariff versus statutory levies, airport fees, and ancillary surcharges
          </p>
        </div>

        {/* View mode toggle */}
        <div className="flex items-center gap-1 bg-canvas/80 p-0.5 rounded-lg border border-ink-border/50 self-start sm:self-auto shrink-0">
          <button
            onClick={() => setViewMode('rupees')}
            className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${
              viewMode === 'rupees'
                ? 'bg-accent-violet text-white shadow-sm font-semibold'
                : 'text-ink-muted hover:text-white hover:bg-ink-border/40'
            }`}
          >
            Absolute (₹)
          </button>
          <button
            onClick={() => setViewMode('percent')}
            className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${
              viewMode === 'percent'
                ? 'bg-accent-violet text-white shadow-sm font-semibold'
                : 'text-ink-muted hover:text-white hover:bg-ink-border/40'
            }`}
          >
            Share (%)
          </button>
        </div>
      </div>

      {carriers.length === 0 ? (
        <p className="text-xs text-ink-muted">No quote breakdowns available</p>
      ) : (
        <>
          {/* Main Visual Layout: Chart (Sleek & Thin) + Executive Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Chart Area */}
            <div className="lg:col-span-7 xl:col-span-8 bg-canvas/40 border border-ink-border/40 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
                  {viewMode === 'percent' ? 'Stacked Fare Breakdown (100% Normalized)' : 'Stacked Fare Breakdown (₹ Amount)'}
                </span>
                <span className="text-[11px] font-mono text-ink-faint">
                  {carriers.length} carriers evaluated
                </span>
              </div>

              <div className="h-[270px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    barSize={32}
                    margin={{ top: 12, right: 16, left: 0, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#261c3d" vertical={false} />
                    <XAxis
                      dataKey="carrier"
                      stroke="#786c91"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(code) => `${code} · ${CARRIER_NAMES[code] || ''}`}
                    />
                    <YAxis
                      stroke="#786c91"
                      fontSize={11}
                      tickLine={false}
                      domain={viewMode === 'percent' ? [0, 100] : ['auto', 'auto']}
                      tickFormatter={(v) => (viewMode === 'percent' ? `${v}%` : `₹${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`)}
                    />
                    <Tooltip
                      content={<CustomUnbundlingTooltip viewMode={viewMode} />}
                      cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
                    />
                    <Bar
                      dataKey="base_fare"
                      stackId="fare"
                      name={COMPONENT_CONFIG.base_fare.label}
                      fill={COMPONENT_CONFIG.base_fare.color}
                    />
                    <Bar
                      dataKey="udf"
                      stackId="fare"
                      name={COMPONENT_CONFIG.udf.label}
                      fill={COMPONENT_CONFIG.udf.color}
                    />
                    <Bar
                      dataKey="taxes"
                      stackId="fare"
                      name={COMPONENT_CONFIG.taxes.label}
                      fill={COMPONENT_CONFIG.taxes.color}
                    />
                    <Bar
                      dataKey="convenience_fee"
                      stackId="fare"
                      name={COMPONENT_CONFIG.convenience_fee.label}
                      fill={COMPONENT_CONFIG.convenience_fee.color}
                    />
                    <Bar
                      dataKey="other_fees"
                      stackId="fare"
                      name={COMPONENT_CONFIG.other_fees.label}
                      fill={COMPONENT_CONFIG.other_fees.color}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Color legend */}
              <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 mt-3 pt-3 border-t border-ink-border/30 text-[11px]">
                {Object.entries(COMPONENT_CONFIG).map(([key, item]) => (
                  <div key={key} className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-ink-muted">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary Insights Panel */}
            <div className="lg:col-span-5 xl:col-span-4 flex flex-col gap-3">
              {/* Market Averages Snapshot */}
              <div className="bg-canvas/60 border border-ink-border/50 rounded-xl p-4">
                <span className="text-[10px] font-mono uppercase tracking-wider text-ink-muted block mb-1">
                  Market Unbundling Ratio
                </span>
                <div className="flex items-baseline justify-between mb-2">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xl font-bold font-mono text-white">{avgBaseRatio}%</span>
                    <span className="text-xs text-ink-muted">Base Fare</span>
                  </div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xl font-bold font-mono text-amber-400">{avgAncillaryRatio}%</span>
                    <span className="text-xs text-ink-muted">Ancillaries & Taxes</span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-2 rounded-full overflow-hidden flex bg-canvas">
                  <div className="h-full bg-indigo-600 transition-all duration-500" style={{ width: `${avgBaseRatio}%` }} />
                  <div className="h-full bg-amber-500 transition-all duration-500" style={{ width: `${avgAncillaryRatio}%` }} />
                </div>
              </div>

              {/* Carrier Breakdown Cards */}
              <div className="space-y-2">
                {carriers.map((c) => (
                  <div
                    key={c.carrier}
                    className="bg-card border border-ink-border/60 hover:border-accent-violet/40 transition-all rounded-lg p-3 flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-canvas/80 border border-ink-border flex items-center justify-center font-mono font-bold text-xs text-white shrink-0">
                        {c.carrier}
                      </div>
                      <div className="truncate">
                        <div className="font-semibold text-xs text-white truncate">
                          {c.carrierName}
                        </div>
                        <div className="text-[10px] text-ink-muted font-mono">
                          {c.count} quotes · Base {c.base_fare_pct.toFixed(0)}%
                        </div>
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="font-mono font-bold text-xs text-accent-lime">
                        ₹{Math.round(c.total).toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] font-mono text-amber-400">
                        +₹{Math.round(c.total - c.base_fare).toLocaleString('en-IN')} fees
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Detailed Audit Table */}
          <div className="overflow-x-auto mt-6 rounded-lg border border-ink-border/70">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="bg-canvas/80 border-b border-ink-border text-ink-muted uppercase tracking-wider text-[11px]">
                  <th className="text-left py-2.5 px-3 font-semibold font-sans">Carrier</th>
                  <th className="text-right py-2.5 px-3 font-semibold">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-sm bg-indigo-600" />
                      Base Fare
                    </span>
                  </th>
                  <th className="text-right py-2.5 px-3 font-semibold">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-sm bg-sky-600" />
                      UDF
                    </span>
                  </th>
                  <th className="text-right py-2.5 px-3 font-semibold">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-sm bg-amber-500" />
                      Taxes
                    </span>
                  </th>
                  <th className="text-right py-2.5 px-3 font-semibold">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-sm bg-rose-500" />
                      Convenience
                    </span>
                  </th>
                  <th className="text-right py-2.5 px-3 font-semibold">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-sm bg-purple-500" />
                      Other Fees
                    </span>
                  </th>
                  <th className="text-right py-2.5 px-3 font-semibold text-accent-lime">
                    Avg Total
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-border/30">
                {carriers.map((c) => (
                  <tr key={c.carrier} className="hover:bg-card-hover/40 transition-colors">
                    <td className="py-2.5 px-3 font-sans font-medium text-white">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-accent-violet bg-canvas px-1.5 py-0.5 rounded border border-ink-border/60">
                          {c.carrier}
                        </span>
                        <span>{c.carrierName}</span>
                      </div>
                    </td>
                    <td className="text-right py-2.5 px-3 text-ink-muted">
                      {viewMode === 'percent'
                        ? `${c.base_fare_pct.toFixed(1)}%`
                        : `₹${Math.round(c.base_fare).toLocaleString('en-IN')}`}
                    </td>
                    <td className="text-right py-2.5 px-3 text-ink-muted">
                      {viewMode === 'percent'
                        ? `${c.udf_pct.toFixed(1)}%`
                        : `₹${Math.round(c.udf).toLocaleString('en-IN')}`}
                    </td>
                    <td className="text-right py-2.5 px-3 text-ink-muted">
                      {viewMode === 'percent'
                        ? `${c.taxes_pct.toFixed(1)}%`
                        : `₹${Math.round(c.taxes).toLocaleString('en-IN')}`}
                    </td>
                    <td className="text-right py-2.5 px-3 text-ink-muted">
                      {viewMode === 'percent'
                        ? `${c.convenience_fee_pct.toFixed(1)}%`
                        : `₹${Math.round(c.convenience_fee).toLocaleString('en-IN')}`}
                    </td>
                    <td className="text-right py-2.5 px-3 text-ink-muted">
                      {viewMode === 'percent'
                        ? `${c.other_fees_pct.toFixed(1)}%`
                        : `₹${Math.round(c.other_fees).toLocaleString('en-IN')}`}
                    </td>
                    <td className="text-right py-2.5 px-3 font-bold text-accent-lime">
                      {viewMode === 'percent'
                        ? '100.0%'
                        : `₹${Math.round(c.total).toLocaleString('en-IN')}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default UnbundlingInspector;