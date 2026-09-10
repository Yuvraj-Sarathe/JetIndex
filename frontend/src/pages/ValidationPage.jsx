import ModelValidation from '../components/ModelValidation';

export default function ValidationPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Model Validation & Governance Center</h2>
        <p className="text-xs text-ink-muted">Benchmarking predictive paradigms against statutory civil aviation actuals</p>
      </div>
      <ModelValidation />
    </div>
  );
}
