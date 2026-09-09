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
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Fare Unbundling</h3>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Fare Unbundling</h3>
        <p className="text-rose-500">Error: {error}</p>
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
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Fare Unbundling</h3>

      {carriers.length === 0 ? (
        <p className="text-slate-500">No quotes available</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={carriers} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="carrier" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(v) => `₹${v}`} />
              <Tooltip formatter={(value) => `₹${Number(value).toFixed(0)}`} />
              <Legend />
              <Bar dataKey="base_fare" stackId="fare" name="Base Fare" fill="#6366f1" />
              <Bar dataKey="udf" stackId="fare" name="UDF" fill="#8b5cf6" />
              <Bar dataKey="taxes" stackId="fare" name="Taxes" fill="#f59e0b" />
              <Bar dataKey="convenience_fee" stackId="fare" name="Convenience" fill="#10b981" />
              <Bar dataKey="other_fees" stackId="fare" name="Other" fill="#94a3b8" />
            </BarChart>
          </ResponsiveContainer>

          <div className="overflow-x-auto mt-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 px-3 text-slate-600">Carrier</th>
                  <th className="text-right py-2 px-3 text-slate-600">Base Fare</th>
                  <th className="text-right py-2 px-3 text-slate-600">UDF</th>
                  <th className="text-right py-2 px-3 text-slate-600">Taxes</th>
                  <th className="text-right py-2 px-3 text-slate-600">Convenience</th>
                  <th className="text-right py-2 px-3 text-slate-600">Other</th>
                  <th className="text-right py-2 px-3 text-slate-600">Avg Total</th>
                </tr>
              </thead>
              <tbody>
                {carriers.map((c) => {
                  const total = c.base_fare + c.udf + c.taxes + c.convenience_fee + c.other_fees;
                  return (
                    <tr key={c.carrier} className="border-b border-slate-100">
                      <td className="py-2 px-3 font-medium">{c.carrier}</td>
                      <td className="text-right py-2 px-3">₹{c.base_fare.toFixed(0)}</td>
                      <td className="text-right py-2 px-3">₹{c.udf.toFixed(0)}</td>
                      <td className="text-right py-2 px-3">₹{c.taxes.toFixed(0)}</td>
                      <td className="text-right py-2 px-3">₹{c.convenience_fee.toFixed(0)}</td>
                      <td className="text-right py-2 px-3">₹{c.other_fees.toFixed(0)}</td>
                      <td className="text-right py-2 px-3 font-semibold">₹{total.toFixed(0)}</td>
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