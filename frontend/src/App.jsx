import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import ForecastPage from './pages/ForecastPage';
import AnomaliesPage from './pages/AnomaliesPage';
import DataQualityPage from './pages/DataQualityPage';
import AlertsPage from './pages/AlertsPage';
import ScenarioPage from './pages/ScenarioPage';
import ValidationPage from './pages/ValidationPage';
import DocsPage from './pages/DocsPage';

const TAB_CATEGORIES = [
  {
    category: 'Analytics',
    tabs: [
      { id: 'overview', label: 'Publishing Overview', component: Dashboard, shortcut: '1' },
      { id: 'anomalies', label: 'Spike Anomalies', component: AnomaliesPage, shortcut: '2' },
    ],
  },
  {
    category: 'Models',
    tabs: [
      { id: 'forecast', label: 'T+14 Forecast', component: ForecastPage, shortcut: '3' },
      { id: 'scenario', label: 'Scenario Simulator', component: ScenarioPage, shortcut: '4' },
      { id: 'validation', label: 'Model Validation', component: ValidationPage, shortcut: '5' },
    ],
  },
  {
    category: 'Governance',
    tabs: [
      { id: 'quality', label: 'Trust & Quality', component: DataQualityPage, shortcut: '6' },
      { id: 'alerts', label: 'Alerts', component: AlertsPage, shortcut: '7' },
    ],
  },
  {
    category: 'Reference',
    tabs: [
      { id: 'docs', label: 'Methodology & API', component: DocsPage, shortcut: '8' },
    ],
  },
];

function App() {
  const allTabs = TAB_CATEGORIES.flatMap((c) => c.tabs);

  const getInitialTab = () => {
    if (typeof window === 'undefined') return 'overview';
    const hash = window.location.hash.replace('#', '').trim();
    return allTabs.some((t) => t.id === hash) ? hash : 'overview';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab);

  const handleSelectTab = (tabId) => {
    setActiveTab(tabId);
    if (typeof window !== 'undefined') {
      window.location.hash = tabId;
    }
  };

  // Synchronize browser back/forward history with tab state
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '').trim();
      if (allTabs.some((t) => t.id === hash)) {
        setActiveTab(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [allTabs]);

  // Keyboard navigation shortcuts: 1-8 to switch views
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
        return;
      }
      const num = parseInt(e.key, 10);
      if (!isNaN(num) && num >= 1 && num <= allTabs.length) {
        e.preventDefault();
        handleSelectTab(allTabs[num - 1].id);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [allTabs]);

  const ActiveComponent = allTabs.find((t) => t.id === activeTab)?.component || Dashboard;

  return (
    <div className="min-h-screen bg-canvas text-white selection:bg-primary selection:text-black">
      {/* Top Authority Header */}
      <header className="bg-canvas/95 border-b border-hairline sticky top-0 z-40 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/40 flex items-center justify-center font-bold text-lg text-primary font-mono shadow-sm">
                ✈
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2 font-sans">
                    APIx
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-card-elevated text-primary border border-hairline font-semibold tracking-wider">
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
              <button
                onClick={() => handleSelectTab('docs')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-mono transition-all duration-150 shadow-sm ${
                  activeTab === 'docs'
                    ? 'bg-primary text-black font-semibold border-primary hover:bg-primary-active'
                    : 'bg-card-elevated border-hairline text-ink-muted hover:text-white hover:border-hairline-strong'
                }`}
                title="View Official APIx Documentation & Index Methodology [Shortcut: 8]"
              >
                <span>📖</span>
                <span className="font-semibold">Methodology & Docs</span>
              </button>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-card-elevated border border-primary/30 text-xs font-mono shadow-sm">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                <span className="text-primary text-[11px] font-bold tracking-wider">DAILY INDEX PUBLISHED</span>
              </div>
              <div className="hidden md:block text-right border-l border-hairline pl-3">
                <p className="text-[11px] font-medium text-white">MoSPI / NSO</p>
                <p className="text-[10px] text-primary font-mono font-semibold">Official Authority</p>
              </div>
            </div>
          </div>
        </div>

        {/* Categorized Tab Navigation */}
        <div className="border-t border-hairline bg-canvas/80 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
            <nav className="flex items-center flex-wrap gap-2.5 sm:gap-3 lg:justify-between" aria-label="Tabs">
              {TAB_CATEGORIES.map((group, groupIdx) => (
                <div key={group.category} className="flex items-center gap-1.5 shrink-0">
                  {groupIdx > 0 && (
                    <div className="h-4 w-px bg-hairline mr-1 hidden xl:block" aria-hidden="true" />
                  )}
                  <span className="text-[10px] font-mono uppercase font-bold text-ink-muted tracking-wider">
                    {group.category}:
                  </span>
                  <div className="flex items-center gap-1 bg-surface-card p-1 rounded-lg border border-hairline shadow-inner">
                    {group.tabs.map((tab) => {
                      const isActive = activeTab === tab.id;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => handleSelectTab(tab.id)}
                          title={`Press ${tab.shortcut} to view`}
                          className={`px-2.5 py-1.5 text-xs rounded-md transition-all duration-150 font-medium flex items-center gap-1.5 ${
                            isActive
                              ? 'bg-primary text-black font-bold shadow-sm'
                              : 'text-ink-muted hover:text-white hover:bg-card-hover'
                          }`}
                        >
                          <span>{tab.label}</span>
                          <span className={`text-[9px] font-mono px-1 py-0.2 rounded ${
                            isActive ? 'bg-black/15 text-black font-bold' : 'text-ink-faint'
                          }`}>
                            {tab.shortcut}
                          </span>
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
