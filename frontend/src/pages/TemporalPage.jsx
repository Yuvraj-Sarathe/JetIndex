import TemporalPatterns from '../components/TemporalPatterns';

export default function TemporalPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Temporal Dynamics & Yield Analysis</h2>
        <p className="text-xs text-ink-muted">Day-of-week, seasonal, and departure proximity curves across domestic routes</p>
      </div>
      <TemporalPatterns />
    </div>
  );
}
