import { useState, useEffect } from 'react';
import { getQuotes } from '../api/client';

/**
 * UnbundlingInspector — stacked bar showing base/udf/taxes/conv/other by carrier.
 */
function UnbundlingInspector() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getQuotes({ limit: 50 })
      .then(setQuotes)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Fare Unbundling</h3>
        <p className="text-slate-500">Loading...</p>
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
        <div className="overflow-x-auto">
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
      )}
    </div>
  );
}

export default UnbundlingInspector;
