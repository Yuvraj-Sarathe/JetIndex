import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ForecastPage from './pages/ForecastPage';
import AnomaliesPage from './pages/AnomaliesPage';
import DataQualityPage from './pages/DataQualityPage';
import AlertsPage from './pages/AlertsPage';
import ScenarioPage from './pages/ScenarioPage';
import ProvenancePage from './pages/ProvenancePage';
import ValidationPage from './pages/ValidationPage';
import TemporalPage from './pages/TemporalPage';

const TAB_CATEGORIES = [
  {
    category: 'Market Analytics',
    tabs: [
      { id: 'overview', label: 'Publishing Overview', component: Dashboard },
      { id: 'temporal', label: 'Temporal & Lead-Time', component: TemporalPage },
      { id: 'anomalies', label: 'Spike Anomalies', component: AnomaliesPage },
    ],
  },
  {
    category: 'Econometric Models',
    tabs: [
      { id: 'forecast', label: 'T+14 Forecast', component: ForecastPage },
      { id: 'scenario', label: 'Scenario Simulator', component: ScenarioPage },
      { id: 'validation', label: 'Model Validation', component: ValidationPage },
    ],
  },
  {
    category: 'Data Governance',
    tabs: [
      { id: 'quality', label: 'Trust & Quality', component: DataQualityPage },
      { id: 'provenance', label: 'Quote Provenance', component: ProvenancePage },
      { id: 'alerts', label: 'Alerts', component: AlertsPage },
    ],
  },
];

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  const allTabs = TAB_CATEGORIES.flatMap((c) => c.tabs);
  const ActiveComponent = allTabs.find((t) => t.id === activeTab)?.component || Dashboard;

  return (
    <div className="min-h-screen bg-canvas text-white selection:bg-accent-lime selection:text-ink-night">
      {/* Top Authority Header */}
      <header className="bg-card border-b border-ink-border sticky top-0 z-40 backdrop-blur-md bg-opacity-95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-accent-violet/20 border border-accent-violet flex items-center justify-center font-bold text-lg text-accent-lime font-mono shadow-sm">
                ✈
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2 font-sans">
                    APIx
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-accent-violet/30 text-accent-lime border border-accent-violet/60 font-semibold tracking-wider">
                      SIH26056
                    </span>
                  </h1>
                </div>
                <p className="text-xs text-ink-muted">
                  Real-time Airfare Price Index for India · DGCA-Weighted Laspeyres Engine
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 self-end sm:self-auto">
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-card-elevated border border-accent-lime/40 text-xs font-mono shadow-sm">
                <span className="w-2 h-2 rounded-full bg-accent-lime animate-pulse"></span>
                <span className="text-accent-lime text-[11px] font-bold">DAILY INDEX PUBLISHED</span>
              </div>
              <div className="hidden md:block text-right border-l border-ink-border pl-3">
                <p className="text-[11px] font-medium text-white">MoSPI / NSO</p>
                <p className="text-[10px] text-accent-cyan font-mono font-semibold">Official Authority</p>
              </div>
            </div>
          </div>
        </div>

        {/* Categorized Tab Navigation */}
        <div className="border-t border-ink-border/60 bg-canvas/40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2 overflow-x-auto">
            <nav className="flex items-center gap-6 min-w-max" aria-label="Tabs">
              {TAB_CATEGORIES.map((group) => (
                <div key={group.category} className="flex items-center gap-1.5">
                  <span className="text-[10px] uppercase font-semibold text-ink-faint tracking-wider pr-1">
                    {group.category}:
                  </span>
                  <div className="flex items-center gap-1 bg-card/60 p-1 rounded-lg border border-ink-border/40">
                    {group.tabs.map((tab) => {
                      const isActive = activeTab === tab.id;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`px-3 py-1 text-xs rounded-md transition-all font-medium ${
                            isActive
                              ? 'bg-accent-violet text-white shadow-sm font-semibold'
                              : 'text-ink-muted hover:text-white hover:bg-card-hover'
                          }`}
                        >
                          {tab.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Surface */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;
