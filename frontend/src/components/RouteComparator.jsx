import { useState, useEffect } from 'react';

/**
 * RouteComparator — Side-by-side multi-route comparison.
 */
function RouteComparator() {
  const [routes, setRoutes] = useState([]);
  const [selectedRoutes, setSelectedRoutes] = useState(['DEL-BOM', 'DEL-BLR']);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
  const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

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
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-medium text-slate-900 mb-4">Route Comparator</h3>
      
      {/* Route Selector */}
      <div className="flex flex-wrap gap-2 mb-4">
        {routes.slice(0, 10).map(code => (
          <button
            key={code}
            onClick={() => toggleRoute(code)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedRoutes.includes(code)
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {code}
          </button>
        ))}
      </div>

      {/* Comparison Table */}
      {loading && <p className="text-slate-500">Loading comparison...</p>}
      
      {routeData && !loading && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-3 font-medium text-slate-600">Route</th>
                <th className="text-right py-2 px-3 font-medium text-slate-600">Weight</th>
                <th className="text-right py-2 px-3 font-medium text-slate-600">Base Fare</th>
                <th className="text-right py-2 px-3 font-medium text-slate-600">Latest Index</th>
              </tr>
            </thead>
            <tbody>
              {(routeData.routes || []).map((route) => (
                <tr key={route.route_code} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-2 px-3 font-medium text-slate-900">{route.route_code}</td>
                  <td className="py-2 px-3 text-right text-slate-700">{route.weight_pct}%</td>
                  <td className="py-2 px-3 text-right text-slate-700">₹{route.base_fare_benchmark?.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right font-mono text-slate-700">{route.latest_indexed_fare?.toFixed(2)}</td>
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
