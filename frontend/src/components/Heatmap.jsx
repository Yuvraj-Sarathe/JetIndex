import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import { useHeatmap } from '../hooks/useApix';

/**
 * Heatmap — Leaflet map showing routes colored by volatility.
 */
function Heatmap({ date }) {
  const { data, loading, error } = useHeatmap(date);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Route Heatmap</h3>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Route Heatmap</h3>
        <p className="text-rose-500">Error: {error}</p>
      </div>
    );
  }

  const routes = data || [];

  // Center on India
  const center = [20.5937, 78.9629];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Route Heatmap</h3>
      <div className="h-[300px] rounded-lg overflow-hidden">
        <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          {routes.map((route, idx) => {
            // Use API-provided coordinates, fall back to null
            const origin = route.o_lat != null && route.o_lon != null
              ? [route.o_lat, route.o_lon]
              : null;
            const dest = route.d_lat != null && route.d_lon != null
              ? [route.d_lat, route.d_lon]
              : null;
            if (!origin || !dest) return null;

            // The heatmap endpoint's destination field name differs between
            // MOCK_MODE ("dest") and the live DB query ("destination") — support both.
            const destLabel = route.dest ?? route.destination;

            // Color by volatility (lower = green, higher = red)
            const volatility = route.volatility || 0;
            const color = volatility > 0.1 ? '#f43f5e' : volatility > 0.05 ? '#f59e0b' : '#10b981';

            // index_contrib is only present in mock data today; fall back to a
            // flat weight rather than fabricating a number when it's absent.
            const weight = route.index_contrib != null ? Math.max(2, route.index_contrib * 3) : 3;

            return (
              <div key={route.route_id ?? route.route_code ?? idx}>
                <CircleMarker center={origin} radius={8} fillColor="#6366f1" fillOpacity={0.8} color="#4f46e5">
                  <Popup>{route.origin}</Popup>
                </CircleMarker>
                <CircleMarker center={dest} radius={8} fillColor="#6366f1" fillOpacity={0.8} color="#4f46e5">
                  <Popup>{destLabel}</Popup>
                </CircleMarker>
                <Polyline
                  positions={[origin, dest]}
                  pathOptions={{ color, weight, opacity: 0.7 }}
                >
                  <Popup>
                    <strong>{route.origin} → {destLabel}</strong><br />
                    Avg Fare: ₹{route.avg_fare?.toLocaleString()}<br />
                    Volatility: {(volatility * 100).toFixed(1)}%
                  </Popup>
                </Polyline>
              </div>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}

export default Heatmap;