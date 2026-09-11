import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import { useHeatmap } from '../hooks/useApix';

/**
 * Heatmap — Leaflet map showing routes colored by volatility.
 */
function Heatmap({ date }) {
  const { data, loading, error } = useHeatmap(date);

  if (loading) {
    return (
      <div className="bg-card border border-ink-border rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Route Heatmap & Volatility</h3>
        <p className="text-xs text-ink-muted">Loading geospatial network...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-rose-500/30 rounded-xl p-5 shadow-sm">
        <h3 className="text-base font-semibold text-white mb-2">Route Heatmap & Volatility</h3>
        <p className="text-xs text-rose-400">Error: {error}</p>
      </div>
    );
  }

  const routes = data || [];
  const center = [20.5937, 78.9629];

  return (
    <div className="bg-card border border-hairline rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Route Volatility Radar</h3>
          <p className="text-xs text-ink-muted">Inter-city pair dispersion & price volatility</p>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1 text-ink-muted">
            <span className="w-2.5 h-2.5 rounded-full bg-[#4a4a4a]"></span> Low (&lt;5%)
          </span>
          <span className="flex items-center gap-1 text-ink-muted">
            <span className="w-2.5 h-2.5 rounded-full bg-primary"></span> Med (5-10%)
          </span>
          <span className="flex items-center gap-1 text-ink-muted">
            <span className="w-2.5 h-2.5 rounded-full bg-accent-rose"></span> High (&gt;10%)
          </span>
        </div>
      </div>
      <div className="h-[320px] rounded-lg overflow-hidden border border-hairline bg-canvas">
        <MapContainer
          center={center}
          zoom={4}
          scrollWheelZoom={false}
          style={{ height: '100%', width: '100%', background: '#0a0a0a' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            maxZoom={16}
          />
          {routes.map((route, idx) => {
            const origin = route.o_lat != null && route.o_lon != null
              ? [route.o_lat, route.o_lon]
              : null;
            const dest = route.d_lat != null && route.d_lon != null
              ? [route.d_lat, route.d_lon]
              : null;
            if (!origin || !dest) return null;

            const destLabel = route.dest ?? route.destination;
            const volatility = route.volatility || 0;
            const color = volatility > 0.1 ? '#ef4444' : volatility > 0.05 ? '#faff69' : '#4a4a4a';
            const opacity = volatility > 0.1 ? 0.95 : volatility > 0.05 ? 0.85 : 0.45;
            const weight = volatility > 0.1 ? 2.5 : volatility > 0.05 ? 2 : 1.2;

            return (
              <div key={route.route_id ?? route.route_code ?? idx}>
                <CircleMarker center={origin} radius={4} fillColor="#faff69" fillOpacity={1} color="#0a0a0a" weight={1}>
                  <Popup>{route.origin}</Popup>
                </CircleMarker>
                <CircleMarker center={dest} radius={4} fillColor="#faff69" fillOpacity={1} color="#0a0a0a" weight={1}>
                  <Popup>{destLabel}</Popup>
                </CircleMarker>
                <Polyline
                  positions={[origin, dest]}
                  pathOptions={{ color, weight, opacity }}
                >
                  <Popup>
                    <div className="text-xs font-sans text-slate-900">
                      <strong>{route.origin} → {destLabel}</strong><br />
                      Avg Fare: ₹{route.avg_fare?.toLocaleString()}<br />
                      Volatility: {(volatility * 100).toFixed(1)}%
                    </div>
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