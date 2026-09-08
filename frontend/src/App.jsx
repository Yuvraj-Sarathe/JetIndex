import Dashboard from './pages/Dashboard';

function App() {
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
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
