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
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setMode('quote')}
            className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all ${
              mode === 'quote'
                ? 'bg-accent-violet text-white shadow-sm font-semibold'
                : 'bg-card-elevated text-ink-muted border border-ink-border hover:text-white'
            }`}
          >
            Quote Audit Trace
          </button>
          <button
            onClick={() => setMode('cell')}
            className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all ${
              mode === 'cell'
                ? 'bg-accent-violet text-white shadow-sm font-semibold'
                : 'bg-card-elevated text-ink-muted border border-ink-border hover:text-white'
            }`}
          >
            Corridor Cell Drilldown
          </button>
        </div>

        {mode === 'quote' ? (
          <div className="flex gap-2">
            <input
              value={quoteId}
              onChange={(e) => setQuoteId(e.target.value)}
              placeholder="Quote ID (e.g. Q-20260826-DEL-BOM-...)"
              className="flex-1 px-3 py-2 bg-canvas border border-ink-border rounded-lg text-sm font-mono text-white focus:outline-none focus:border-accent-lime transition-colors"
            />
            <button
              onClick={traceQuote}
              disabled={loading}
              className="px-4 py-2 bg-accent-violet hover:bg-accent-violet/90 text-white text-xs font-semibold uppercase tracking-wider rounded-lg disabled:opacity-50 transition-all shadow-sm"
            >
              {loading ? 'Tracing...' : 'Trace Quote'}
            </button>
          </div>
        ) : (
          <div className="flex gap-2">
            <input
              value={routeCode}
              onChange={(e) => setRouteCode(e.target.value)}
              placeholder="Route (e.g. DEL-BOM)"
              className="w-48 px-3 py-2 bg-canvas border border-ink-border rounded-lg text-sm font-mono text-white focus:outline-none focus:border-accent-lime transition-colors uppercase"
            />
            <button
              onClick={drillCell}
              disabled={loading}
              className="px-4 py-2 bg-accent-violet hover:bg-accent-violet/90 text-white text-xs font-semibold uppercase tracking-wider rounded-lg disabled:opacity-50 transition-all shadow-sm"
            >
              {loading ? 'Drilling...' : 'Drill Cell'}
            </button>
          </div>
        )}
      </div>

      {error && <div className="bg-card border border-rose-500/40 rounded-xl p-4 text-rose-300">{error}</div>}

      {result && (
        <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white">Cryptographic Audit Result</h3>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-accent-lime/15 text-accent-lime border border-accent-lime/40">
              VERIFIED RECORD
            </span>
          </div>
          {result.provenance ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(result.provenance).map(([k, v]) => (
                <div key={k} className="p-2.5 bg-card-elevated border border-ink-border/60 rounded-lg">
                  <p className="text-[10px] font-mono uppercase text-ink-faint">{k}</p>
                  <p className="text-xs font-mono font-medium text-white truncate mt-0.5">{String(v)}</p>
                </div>
              ))}
            </div>
          ) : result.cell_hierarchy ? (
            <div>
              <div className="grid grid-cols-3 gap-3 mb-4">
                {Object.entries(result.cell_hierarchy).map(([k, v]) => (
                  <div key={k} className="p-2.5 bg-card-elevated border border-ink-border/60 rounded-lg">
                    <p className="text-[10px] font-mono uppercase text-ink-faint">{k}</p>
                    <p className="text-xs font-mono font-medium text-accent-lime mt-0.5">{String(v)}</p>
                  </div>
                ))}
              </div>
              <p className="text-xs text-ink-muted">{result.quotes?.length || 0} underlying quotes</p>
            </div>
          ) : (
            <pre className="text-xs font-mono text-ink-muted bg-canvas border border-ink-border p-3 rounded-lg overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
          )}
          <p className="text-[11px] font-mono text-ink-faint">Data Tag: {result.data_tag}</p>
        </div>
      )}
    </div>
  );
}
