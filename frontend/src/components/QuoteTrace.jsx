import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

export default function QuoteTrace() {
  const [quoteId, setQuoteId] = useState('');
  const [routeCode, setRouteCode] = useState('DEL-BOM');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('quote'); // 'quote' or 'cell'

  const traceQuote = async () => {
    if (!quoteId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/provenance/quote/${quoteId}`, {
        headers: { 'Authorization': `Bearer ${API_TOKEN}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      setResult(await res.json());
    } catch (err) { setError(err.message); }
    setLoading(false);
  };

  const drillCell = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/provenance/cell-drilldown?route_code=${routeCode}&advance_window=T+7`, {
        headers: { 'Authorization': `Bearer ${API_TOKEN}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      setResult(await res.json());
    } catch (err) { setError(err.message); }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex gap-2 mb-4">
          <button onClick={() => setMode('quote')} className={`px-3 py-1.5 text-sm rounded-lg ${mode === 'quote' ? 'bg-blue-600 text-white' : 'bg-slate-100'}`}>Quote Trace</button>
          <button onClick={() => setMode('cell')} className={`px-3 py-1.5 text-sm rounded-lg ${mode === 'cell' ? 'bg-blue-600 text-white' : 'bg-slate-100'}`}>Cell Drilldown</button>
        </div>

        {mode === 'quote' ? (
          <div className="flex gap-2">
            <input value={quoteId} onChange={(e) => setQuoteId(e.target.value)} placeholder="Quote ID (e.g. Q-20260826-DEL-BOM-...)"
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm" />
            <button onClick={traceQuote} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">Trace</button>
          </div>
        ) : (
          <div className="flex gap-2">
            <input value={routeCode} onChange={(e) => setRouteCode(e.target.value)} placeholder="Route (e.g. DEL-BOM)"
              className="w-40 px-3 py-2 border border-slate-300 rounded-lg text-sm" />
            <button onClick={drillCell} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">Drill Down</button>
          </div>
        )}
      </div>

      {error && <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>}

      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">Provenance Result</h3>
          {result.provenance ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(result.provenance).map(([k, v]) => (
                <div key={k} className="p-2 bg-slate-50 rounded">
                  <p className="text-xs text-slate-500 font-mono">{k}</p>
                  <p className="text-sm font-medium text-slate-900 truncate">{String(v)}</p>
                </div>
              ))}
            </div>
          ) : result.cell_hierarchy ? (
            <div>
              <div className="grid grid-cols-3 gap-3 mb-4">
                {Object.entries(result.cell_hierarchy).map(([k, v]) => (
                  <div key={k} className="p-2 bg-slate-50 rounded">
                    <p className="text-xs text-slate-500 font-mono">{k}</p>
                    <p className="text-sm font-medium text-slate-900">{String(v)}</p>
                  </div>
                ))}
              </div>
              <p className="text-sm text-slate-600">{result.quotes?.length || 0} underlying quotes</p>
            </div>
          ) : (
            <pre className="text-xs text-slate-700 bg-slate-50 p-3 rounded overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
          )}
          <p className="text-xs text-slate-400 mt-3">Data Tag: {result.data_tag}</p>
        </div>
      )}
    </div>
  );
}
