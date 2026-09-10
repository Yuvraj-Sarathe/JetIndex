import { useState, useEffect } from 'react';

/**
 * RouteComparator — Side-by-side multi-route comparison.
 */
const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

function RouteComparator() {
  const [routes, setRoutes] = useState([]);
  const [selectedRoutes, setSelectedRoutes] = useState(['DEL-BOM', 'DEL-BLR']);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available routes
    fetch(`${API_BASE}/routes`, {
      headers: { 'Authorization': `Bearer ${API_TOKEN}` },
    })
      .then(res => res.json())
      .then(data => {
        if (data.routes) {
          setRoutes(data.routes.map(r => r.route_code));
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedRoutes.length < 2) return;
    setLoading(true);
    const routesParam = selectedRoutes.join(',');
    fetch(`${API_BASE}/routes/compare?routes=${routesParam}`, {
      headers: { 'Authorization': `Bearer ${API_TOKEN}` },
    })
      .then(res => res.json())
      .then(data => {
        setRouteData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [selectedRoutes]);

  const toggleRoute = (code) => {
    if (selectedRoutes.includes(code)) {
      setSelectedRoutes(prev => prev.filter(r => r !== code));
    } else if (selectedRoutes.length < 5) {
      setSelectedRoutes(prev => [...prev, code]);
    }
  };

  return (
    <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-white">Multi-Route Pair Comparator</h3>
        <p className="text-xs text-ink-muted">Select up to 5 corridors for cross-route index dispersion analysis</p>
      </div>
      
      {/* Route Selector */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {routes.slice(0, 10).map(code => (
          <button
            key={code}
            onClick={() => toggleRoute(code)}
            className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
              selectedRoutes.includes(code)
                ? 'bg-accent-violet text-white shadow-sm border border-accent-violet'
                : 'bg-canvas border border-ink-border text-ink-muted hover:text-white hover:border-ink-borderLight'
            }`}
          >
            {code}
          </button>
        ))}
      </div>

      {/* Comparison Table */}
      {loading && <p className="text-xs text-ink-muted py-4">Recomputing corridor metrics...</p>}
      
      {routeData && !loading && (
        <div className="overflow-x-auto rounded-lg border border-ink-border/70">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="bg-canvas/80 border-b border-ink-border text-ink-muted uppercase tracking-wider text-[11px]">
                <th className="text-left py-2.5 px-3 font-semibold">Route</th>
                <th className="text-right py-2.5 px-3 font-semibold">DGCA Weight</th>
                <th className="text-right py-2.5 px-3 font-semibold">Base Benchmark</th>
                <th className="text-right py-2.5 px-3 font-semibold text-accent-lime">Current Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-border/30">
              {(routeData.routes || []).map((route) => (
                <tr key={route.route_code} className="hover:bg-card-hover/40 transition-colors">
                  <td className="py-2 px-3 font-sans font-medium text-white">{route.route_code}</td>
                  <td className="py-2 px-3 text-right text-ink-muted">{route.weight_pct}%</td>
                  <td className="py-2 px-3 text-right text-ink-muted">₹{route.base_fare_benchmark?.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right font-bold text-accent-lime">{route.latest_indexed_fare?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default RouteComparator;
