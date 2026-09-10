import { useState } from 'react';

const sections = [
  {
    id: 'overview',
    title: 'Project Overview',
    content: `JetIndex (APIx) is a Real-time Airfare Price Index platform built for Smart India Hackathon 2026. It monitors India's top 20 domestic air routes (DGCA top routes) and computes inflation-linked indices that feed into MoSPI's Consumer Price Index (CPI) Transport sub-group.

The platform scrapes live airfare data from airline portals and OTAs, computes Laspeyres/Fisher/Paasche indices, and provides policy-ready analytics for RBI Monetary Policy Committee and DGCA.`
  },
  {
    id: 'architecture',
    title: 'Architecture',
    content: `**Tech Stack:**
- Backend: FastAPI (Python 3.11+), Celery task queue, PostgreSQL/TimescaleDB
- Frontend: React + Vite + Tailwind CSS
- ML: scikit-learn (Ridge + GradientBoosting ensemble)
- Scraping: Playwright + curl_cffi for anti-bot bypass

**Core Modules:**
- \`engine/compute_national_index.py\` — Laspeyres, Fisher, Paasche index computation
- \`engine/forecasting.py\` — ML forecasting ensemble
- \`engine/backtest.py\` — DGCA backtest validation
- \`scrapers/\` — Airline/OTA scrapers with proxy rotation
- \`pipeline/\` — Quote cleaning, unbundling, deduplication`
  },
  {
    id: 'scrapers',
    title: 'Data Scrapers',
    content: `**Supported Airlines:**
- IndiGo (6E) — indigo.co.in
- Air India (AI) — airindia.com
- SpiceJet (SG) — spicejet.com
- Akasa Air (QP) — akasaair.com

**Supported OTAs:**
- MakeMyTrip — makemytrip.com
- EaseMyTrip — easemytrip.com
- ClearTrip — cleartrip.com

**Scraping Features:**
- Anti-bot bypass via curl_cffi impersonation
- Playwright fallback for JavaScript-heavy pages
- Session management with cookie persistence
- Proxy rotation support
- Request throttling (1-3s random delay)

**Mock Mode:**
When \`MOCK_MODE=true\`, the system serves pre-generated data from \`data/mock/\` instead of scraping live.`
  },
  {
    id: 'indices',
    title: 'Index Methodology',
    content: `**Indices Computed:**
- **Laspeyres Index** — Fixed basket (base period quantities), most stable
- **Paasche Index** — Current basket, reflects substitution
- **Fisher Index** — Geometric mean of Laspeyres × Paasche, ideal index
- **Spot T+1 Index** — Last-minute booking premium (emergency capacity)

**Advance Purchase Windows:**
- T+1 (Tomorrow), T+7, T+15, T+30, T+45

**Route Weights (DGCA Top 20):**
Top 20 domestic routes weighted by passenger volume (DEL-BOM: 14.8%, DEL-BLR: 12.5%, etc.)

**CPI Transmission:**
- Transport & Communication CPI Weight: 8.59%
- Airfare share within Transport: 3.85%
- Impact = ΔIndex × 0.0385 × 0.0859 bps`
  },
  {
    id: 'api',
    title: 'API Endpoints',
    content: `**Public Endpoints:**
- \`GET /api/v1/apix/daily\` — Daily index values
- \`GET /api/v1/apix/weekly\` — Weekly rollups
- \`GET /api/v1/apix/monthly\` — Monthly rollups
- \`GET /api/v1/apix/scraped-vs-dgca\` — Scraped vs DGCA benchmark
- \`GET /api/v1/routes\` — Route basket
- \`GET /api/v1/routes/heatmap\` — 20×5 heatmap
- \`GET /api/v1/elasticity\` — Price elasticity
- \`GET /api/v1/backtest\` — Backtest results
- \`GET /api/v1/anomalies\` — Detected anomalies

**ML Endpoints:**
- \`POST /api/v1/ml/train\` — Train forecasting model
- \`POST /api/v1/ml/nowcast\` — Multi-horizon forecast
- \`GET /api/v1/ml/model/status\` — Model status

**Analytics Endpoints:**
- \`GET /api/v1/analytics/pressure-score\` — Inflation pressure score
- \`GET /api/v1/analytics/cpi-decomposition\` — Route CPI waterfall
- \`GET /api/v1/analytics/heatmap\` — Detailed heatmap`
  },
  {
    id: 'environment',
    title: 'Environment Variables',
    content: `**Required (.env):**
\`\`\`
MOCK_MODE=true          # true = mock data, false = live scraping
API_TOKEN=your-token    # Bearer token for API auth
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
\`\`\`

**Optional:**
\`\`\`
PROXY_ENABLED=false     # Enable proxy rotation
PROXY_URL=              # Proxy URL
RAW_DATA_DIR=data/raw   # Raw scraped data storage
LOG_LEVEL=INFO          # Logging level
\`\`\`

**Docker Compose Services:**
- \`api\` — FastAPI server (port 8000)
- \`db\` — PostgreSQL + TimescaleDB
- \`redis\` — Celery broker
- \`worker\` — Celery worker
- \`beat\` — Celery beat scheduler`
  },
  {
    id: 'development',
    title: 'Development Setup',
    content: `**Local Development:**
\`\`\`bash
# Clone and setup
git clone https://github.com/Yuvraj-Sarathe/JetIndex.git
cd JetIndex
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt

# Run with mock data
cp .env .env.local  # Edit MOCK_MODE=true
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
\`\`\`

**Testing:**
\`\`\`bash
pytest tests/ -v           # Run all tests
pytest tests/test_engine/  # Engine tests only
ruff check .               # Lint
ruff format .              # Format
\`\`\``
  }
];

function DocsPage() {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200">
      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 border-r border-slate-200 p-4">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Documentation</h2>
          <nav className="space-y-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  activeSection === section.id
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {section.title}
              </button>
            ))}
          </nav>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-6">
          {sections
            .filter((s) => s.id === activeSection)
            .map((section) => (
              <div key={section.id}>
                <h2 className="text-2xl font-bold text-slate-900 mb-4">{section.title}</h2>
                <div className="prose prose-slate max-w-none">
                  {section.content.split('\n').map((line, i) => {
                    // Handle code blocks
                    if (line.startsWith('```')) {
                      return null;
                    }
                    // Handle code inline
                    if (line.includes('`') && !line.startsWith('#')) {
                      const parts = line.split('`');
                      return (
                        <p key={i} className="text-slate-700 mb-2">
                          {parts.map((part, j) =>
                            j % 2 === 1 ? (
                              <code key={j} className="bg-slate-100 px-1.5 py-0.5 rounded text-sm font-mono text-slate-800">
                                {part}
                              </code>
                            ) : (
                              part
                            )
                          )}
                        </p>
                      );
                    }
                    // Handle headings
                    if (line.startsWith('**') && line.endsWith('**')) {
                      return (
                        <h3 key={i} className="text-lg font-semibold text-slate-900 mt-6 mb-2">
                          {line.replace(/\*\*/g, '')}
                        </h3>
                      );
                    }
                    // Handle list items
                    if (line.startsWith('- ')) {
                      return (
                        <li key={i} className="text-slate-700 ml-4 mb-1">
                          {line.substring(2)}
                        </li>
                      );
                    }
                    // Empty lines
                    if (line.trim() === '') {
                      return <div key={i} className="h-2" />;
                    }
                    // Regular text
                    return (
                      <p key={i} className="text-slate-700 mb-2">
                        {line}
                      </p>
                    );
                  })}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

export default DocsPage;
