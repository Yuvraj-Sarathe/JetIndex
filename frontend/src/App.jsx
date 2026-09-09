import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ForecastPage from './pages/ForecastPage';
import AnomaliesPage from './pages/AnomaliesPage';
import DataQualityPage from './pages/DataQualityPage';

const TABS = [
  { id: 'overview', label: 'Overview', component: Dashboard },
  { id: 'forecast', label: 'Forecast', component: ForecastPage },
  { id: 'anomalies', label: 'Anomalies', component: AnomaliesPage },
  { id: 'quality', label: 'Data Quality', component: DataQualityPage },
];

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  const ActiveComponent = TABS.find(t => t.id === activeTab)?.component || Dashboard;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">APIx</h1>
              <p className="text-sm text-slate-500">
                Real-time Airfare Price Index for India — SIH26056
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400">
                MoSPI / NSO · Smart Automation
              </p>
            </div>
          </div>
        </div>
        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;
