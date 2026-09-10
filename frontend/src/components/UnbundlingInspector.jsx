import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getQuotes } from '../api/client';

/**
 * UnbundlingInspector — stacked bar + table showing base/udf/taxes/conv/other by carrier.
 *
 * Note: the API's QuoteResponse only exposes a single combined `taxes` field
 * (no separate GST/PSF/ASF breakdown exists in FareQuote / the DB schema), so
 * "Taxes" is shown as one component rather than split into sub-taxes.
 */
function UnbundlingInspector() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        <h3 className="text-base font-semibold text-white mb-2">Fare Unbundling Decomposition</h3>
        <p className="text-xs text-ink-muted">Decomposing carrier ancillary breakdowns...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Fare Unbundling Decomposition</h3>
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

  // Average per carrier
  const carriers = Object.entries(byCarrier).map(([carrier, totals]) => ({
    carrier,
    base_fare: totals.base_fare / totals.count,
    udf: totals.udf / totals.count,
    taxes: totals.taxes / totals.count,
    convenience_fee: totals.convenience_fee / totals.count,
    other_fees: totals.other_fees / totals.count,
    count: totals.count,
  }));

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-white">Carrier Fare Unbundling Inspector</h3>
        <p className="text-xs text-ink-muted">Stacked breakdown of base tariff, UDF, statutory taxes, and convenience charges</p>
      </div>

      {carriers.length === 0 ? (
        <p className="text-xs text-ink-muted">No quote breakdowns available</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={carriers} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#261c3d" />
              <XAxis dataKey="carrier" stroke="#786c91" fontSize={11} tickLine={false} />
              <YAxis stroke="#786c91" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${v}`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f1633',
                  borderColor: '#362d59',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '12px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
                }}
                formatter={(value) => `₹${Number(value).toFixed(0)}`}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="base_fare" stackId="fare" name="Base Fare" fill="#6a5fc1" />
              <Bar dataKey="udf" stackId="fare" name="UDF" fill="#4ecdc4" />
              <Bar dataKey="taxes" stackId="fare" name="Taxes" fill="#c2ef4e" />
              <Bar dataKey="convenience_fee" stackId="fare" name="Convenience" fill="#fa7faa" />
              <Bar dataKey="other_fees" stackId="fare" name="Other Fees" fill="#786c91" />
            </BarChart>
          </ResponsiveContainer>

          <div className="overflow-x-auto mt-5 rounded-lg border border-ink-border/70">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="bg-canvas/80 border-b border-ink-border text-ink-muted uppercase tracking-wider text-[11px]">
                  <th className="text-left py-2.5 px-3 font-semibold">Carrier</th>
                  <th className="text-right py-2.5 px-3 font-semibold">Base Fare</th>
                  <th className="text-right py-2.5 px-3 font-semibold">UDF</th>
                  <th className="text-right py-2.5 px-3 font-semibold">Taxes</th>
                  <th className="text-right py-2.5 px-3 font-semibold">Convenience</th>
                  <th className="text-right py-2.5 px-3 font-semibold">Other</th>
                  <th className="text-right py-2.5 px-3 font-semibold text-accent-lime">Avg Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-border/30">
                {carriers.map((c) => {
                  const total = c.base_fare + c.udf + c.taxes + c.convenience_fee + c.other_fees;
                  return (
                    <tr key={c.carrier} className="hover:bg-card-hover/40 transition-colors">
                      <td className="py-2 px-3 font-sans font-medium text-white">{c.carrier}</td>
                      <td className="text-right py-2 px-3 text-ink-muted">₹{c.base_fare.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 text-ink-muted">₹{c.udf.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 text-ink-muted">₹{c.taxes.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 text-ink-muted">₹{c.convenience_fee.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 text-ink-muted">₹{c.other_fees.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 font-bold text-accent-lime">₹{total.toFixed(0)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default UnbundlingInspector;