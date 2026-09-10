import QuoteTrace from '../components/QuoteTrace';

export default function ProvenancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Quote Provenance & Cryptographic Audit Trail</h2>
        <p className="text-xs text-ink-muted">Trace individual flight quotes from airline endpoints to published index aggregation cells</p>
      </div>
      <QuoteTrace />
    </div>
  );
}
