import ScenarioSimulator from '../components/ScenarioSimulator';

export default function ScenarioPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Policy Scenario & Macro Shock Simulator</h2>
        <p className="text-xs text-ink-muted">Stress-test headline and transport CPI inflation against dynamic aviation shocks</p>
      </div>
      <ScenarioSimulator />
    </div>
  );
}
