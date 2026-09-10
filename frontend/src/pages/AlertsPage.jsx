import AlertFeed from '../components/AlertFeed';

export default function AlertsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Alerts & Threat Feed Surveillance</h2>
        <p className="text-xs text-ink-muted">Automated real-time notification engine for route volatility and price spikes</p>
      </div>
      <AlertFeed />
    </div>
  );
}
