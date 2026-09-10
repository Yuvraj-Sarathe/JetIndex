import { useState } from 'react';

const SECTIONS = [
  {
    id: 'overview',
    icon: '🏛️',
    title: 'Executive Overview',
    badge: 'SIH26056',
    summary: 'Macroeconomic problem statement, institutional mandate, and system objectives.',
  },
  {
    id: 'methodology',
    icon: '📐',
    title: 'Index Math & Axioms',
    badge: 'ILO 2020',
    summary: 'Laspeyres, Fisher Ideal, Paasche, Jevons micro-aggregation, and axiomatic tests.',
  },
  {
    id: 'basket',
    icon: '✈️',
    title: 'DGCA Route Basket',
    badge: '20 Corridors',
    summary: 'Top 20 domestic city-pairs weighted by official DGCA scheduled passenger traffic.',
  },
  {
    id: 'unbundling',
    icon: '🔍',
    title: 'Fare Unbundling Model',
    badge: '5 Components',
    summary: 'Taxonomy for decomposing composite airline tariffs into pure fare and statutory levies.',
  },
  {
    id: 'transmission',
    icon: '⚡',
    title: 'CPI Transmission Framework',
    badge: 'MoSPI / RBI',
    summary: 'Basis points (bps) transmission formula to Transport & Communication CPI subgroup.',
  },
  {
    id: 'scrapers',
    icon: '🛡️',
    title: 'Scraping & Governance',
    badge: 'Stealth Engine',
    summary: 'Non-disruptive TLS fingerprinting, rate limiting, and ethical scraping standards.',
  },
  {
    id: 'api',
    icon: '🔌',
    title: 'API Specification',
    badge: 'v1 REST + WS',
    summary: 'Complete endpoint inventory for econometric series, models, and real-time streams.',
  },
  {
    id: 'deployment',
    icon: '⚙️',
    title: 'Deployment & Setup',
    badge: 'Docker',
    summary: 'Local environment setup, TimescaleDB hypertable migrations, and testing suite.',
  },
];

const ROUTE_BASKET = [
  { code: 'DEL-BOM', origin: 'Delhi (DEL)', dest: 'Mumbai (BOM)', weight: '10.92%', share: 'Tier-1 Trunk', distance: '1,148 km' },
  { code: 'DEL-BLR', origin: 'Delhi (DEL)', dest: 'Bengaluru (BLR)', weight: '8.45%', share: 'Tier-1 Trunk', distance: '1,740 km' },
  { code: 'BOM-BLR', origin: 'Mumbai (BOM)', dest: 'Bengaluru (BLR)', weight: '7.15%', share: 'Tier-1 Trunk', distance: '842 km' },
  { code: 'DEL-CCU', origin: 'Delhi (DEL)', dest: 'Kolkata (CCU)', weight: '5.82%', share: 'Metropolitan', distance: '1,305 km' },
  { code: 'DEL-HYD', origin: 'Delhi (DEL)', dest: 'Hyderabad (HYD)', weight: '5.41%', share: 'Metropolitan', distance: '1,253 km' },
  { code: 'BOM-GOI', origin: 'Mumbai (BOM)', dest: 'Goa (GOI)', weight: '4.95%', share: 'Leisure / High Yield', distance: '435 km' },
  { code: 'DEL-MAA', origin: 'Delhi (DEL)', dest: 'Chennai (MAA)', weight: '4.78%', share: 'Metropolitan', distance: '1,760 km' },
  { code: 'BLR-HYD', origin: 'Bengaluru (BLR)', dest: 'Hyderabad (HYD)', weight: '4.22%', share: 'Regional Tech', distance: '500 km' },
  { code: 'BOM-CCU', origin: 'Mumbai (BOM)', dest: 'Kolkata (CCU)', weight: '3.91%', share: 'Metropolitan', distance: '1,658 km' },
  { code: 'DEL-PNQ', origin: 'Delhi (DEL)', dest: 'Pune (PNQ)', weight: '3.75%', share: 'Business Corridor', distance: '1,173 km' },
  { code: 'DEL-AMD', origin: 'Delhi (DEL)', dest: 'Ahmedabad (AMD)', weight: '3.62%', share: 'Commercial', distance: '775 km' },
  { code: 'BOM-HYD', origin: 'Mumbai (BOM)', dest: 'Hyderabad (HYD)', weight: '3.44%', share: 'Metropolitan', distance: '622 km' },
  { code: 'BOM-MAA', origin: 'Mumbai (BOM)', dest: 'Chennai (MAA)', weight: '3.31%', share: 'Metropolitan', distance: '1,033 km' },
  { code: 'BLR-CCU', origin: 'Bengaluru (BLR)', dest: 'Kolkata (CCU)', weight: '3.10%', share: 'Metropolitan', distance: '1,560 km' },
  { code: 'DEL-SXR', origin: 'Delhi (DEL)', dest: 'Srinagar (SXR)', weight: '2.98%', share: 'Tourism / Seasonal', distance: '650 km' },
  { code: 'DEL-LKO', origin: 'Delhi (DEL)', dest: 'Lucknow (LKO)', weight: '2.84%', share: 'Tier-2 Capital', distance: '420 km' },
  { code: 'DEL-JAI', origin: 'Delhi (DEL)', dest: 'Jaipur (JAI)', weight: '2.65%', share: 'Short Haul', distance: '240 km' },
  { code: 'DEL-TRV', origin: 'Delhi (DEL)', dest: 'Thiruvananthapuram', weight: '2.55%', share: 'Long Haul', distance: '2,220 km' },
  { code: 'BLR-MAA', origin: 'Bengaluru (BLR)', dest: 'Chennai (MAA)', weight: '2.48%', share: 'Regional Hub', distance: '290 km' },
  { code: 'HYD-MAA', origin: 'Hyderabad (HYD)', dest: 'Chennai (MAA)', weight: '2.37%', share: 'Regional Hub', distance: '510 km' },
];

const API_ENDPOINTS = [
  {
    category: 'National Price Indices',
    items: [
      { method: 'GET', path: '/api/v1/apix/daily', desc: 'Daily official Laspeyres, Fisher, and base-only index values with 24h DOD % change.' },
      { method: 'GET', path: '/api/v1/apix/weekly', desc: 'Weekly rolled-up index aggregates for smoothing short-term high-frequency noise.' },
      { method: 'GET', path: '/api/v1/apix/monthly', desc: 'Monthly headline index benchmarked against official MoSPI publication cycles.' },
      { method: 'GET', path: '/api/v1/apix/scraped-vs-dgca', desc: 'Comparative validation series: real-time scraped average fare vs. DGCA backward tariffs.' },
    ],
  },
  {
    category: 'Econometric Models & Forecasters',
    items: [
      { method: 'GET', path: '/api/v1/forecast?horizon=14', desc: 'Forward 14-day projection with 95% Bayesian confidence intervals and alert level.' },
      { method: 'POST', path: '/api/v1/scenario/simulate', desc: 'Macroeconomic shock stress-testing (ATF fuel hikes, capacity constraints, demand surges).' },
      { method: 'GET', path: '/api/v1/validation', desc: 'Model governance center: Pearson R, MAPE, R², RMSE against DGCA ground truth.' },
      { method: 'GET', path: '/api/v1/elasticity?route_id=1', desc: 'Price elasticity curve estimates across advance booking horizons.' },
    ],
  },
  {
    category: 'Surveillance & Policy Intelligence',
    items: [
      { method: 'GET', path: '/api/v1/anomalies', desc: 'Algorithmic spike anomaly detector flagging unseasonal price deviations & yield inversions.' },
      { method: 'GET', path: '/api/v1/alerts', desc: 'Real-time alert feed for anti-competitive surge pricing and capacity bottlenecks.' },
      { method: 'GET', path: '/api/v1/data-quality', desc: '7-dimension data trust scorecard (freshness, completeness, outlier rate, plausibility).' },
      { method: 'GET', path: '/api/v1/provenance', desc: 'Cryptographic quote trace from scraper payload to index cell with SHA-256 validation.' },
      { method: 'GET', path: '/api/v1/temporal', desc: 'Day-of-week seasonality, booking lead-time curves, and departure time-of-day yield dynamics.' },
      { method: 'GET', path: '/api/v1/reports/export', desc: 'Download official MoSPI intelligence gazette report (.CSV format).' },
    ],
  },
];

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('overview');
  const [copiedEndpoint, setCopiedEndpoint] = useState(null);

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedEndpoint(text);
    setTimeout(() => setCopiedEndpoint(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-card border border-hairline rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
              <span className="text-[11px] font-mono font-bold tracking-wider uppercase text-primary">
                Official Technical Reference & Standards
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-card-elevated text-accent-blue border border-hairline">
                MoSPI / NSO SIH26056
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight font-sans">
              APIx System Documentation & Index Methodology
            </h1>
            <p className="text-xs text-ink-muted mt-1 max-w-3xl leading-relaxed">
              Standard Operating Procedures, axiomatic price index formulations, DGCA route weighting matrices, fare unbundling taxonomies, and high-frequency REST/WebSocket APIs.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="/api/v1/reports/export"
              className="px-3.5 py-2 rounded-lg bg-card-elevated border border-hairline text-xs font-mono font-medium text-ink-muted hover:text-white hover:border-hairline-strong transition-colors flex items-center gap-2 shadow-sm"
            >
              <span>📜</span>
              <span>Export Official Gazette (.CSV)</span>
            </a>
          </div>
        </div>
      </div>

      {/* Main Documentation Shell */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Sidebar Nav */}
        <aside className="lg:col-span-3 bg-card border border-hairline rounded-xl p-3 shadow-sm sticky top-28">
          <div className="px-3 py-2 border-b border-hairline mb-2">
            <p className="text-[11px] font-mono uppercase font-bold text-ink-faint tracking-wider">
              Documentation Index
            </p>
          </div>
          <nav className="space-y-1">
            {SECTIONS.map((sec) => {
              const isActive = activeSection === sec.id;
              return (
                <button
                  key={sec.id}
                  onClick={() => setActiveSection(sec.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-xs transition-all duration-150 flex items-center justify-between group ${
                    isActive
                      ? 'bg-primary text-black font-bold shadow-sm border border-primary'
                      : 'text-ink-muted hover:text-white hover:bg-card-hover'
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <span className="text-sm">{sec.icon}</span>
                    <span className="truncate">{sec.title}</span>
                  </div>
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded uppercase tracking-wider shrink-0 ${
                      isActive
                        ? 'bg-black/15 text-black font-bold'
                        : 'bg-card-elevated text-ink-faint group-hover:text-ink-muted border border-hairline'
                    }`}
                  >
                    {sec.badge}
                  </span>
                </button>
              );
            })}
          </nav>

          <div className="mt-4 p-3 bg-card-elevated rounded-lg border border-hairline text-[11px] text-ink-faint leading-relaxed">
            <span className="font-bold text-primary font-mono">Statistical Mandate:</span> All formulations comply with the <strong className="text-white">ILO CPI Manual (2020)</strong> and <strong className="text-white">MoSPI Technical Advisory Committee</strong> guidelines.
          </div>
        </aside>

        {/* Content View */}
        <main className="lg:col-span-9 space-y-6">
          {/* SECTION 1: OVERVIEW */}
          {activeSection === 'overview' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Problem & Solution Mandate
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  The National Airfare Inflation Blindspot
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  Historically, India's Consumer Price Index (CPI) computed the civil aviation sub-component via manual monthly ticket-counter surveys. In a modern economy where &gt;90% of bookings occur dynamically online, this created three critical policy failures:
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="text-accent-rose font-mono text-sm font-bold mb-1">01. Extreme Stale Lag</div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Counter data reaches MoSPI & RBI 30–45 days after the fact, missing volatile 200–400% daily fare swings caused by fuel spikes or holiday surges.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="text-accent-rose font-mono text-sm font-bold mb-1">02. 30% Coverage Gap</div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Only ~30% of offline travelers were represented, completely ignoring dynamic yield management algorithms used by modern low-cost carriers.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="text-accent-rose font-mono text-sm font-bold mb-1">03. Composite Bias</div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    A single "total price" was recorded, conflating statutory taxes (GST, UDF) with pure airline base fare movements, misleading monetary policy transmission.
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="text-primary">✓</span> The APIx Solution
                </h3>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  APIx autonomously ingests high-frequency online quotes across India's top 20 domestic city-pairs, isolates pure base fares from statutory charges via an unbundling pipeline, computes a DGCA volume-weighted Laspeyres Price Index daily, and provides macro-econometric transmission models for the Reserve Bank of India.
                </p>
              </div>
            </div>
          )}

          {/* SECTION 2: METHODOLOGY & MATH */}
          {activeSection === 'methodology' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Econometric Formulations
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  Axiomatic Price Index Methodology
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  APIx employs a two-tier aggregation architecture: elementary micro-aggregation via Jevons geometric means, followed by higher-level aggregation using the official Laspeyres fixed-basket formula.
                </p>
              </div>

              {/* Formula Cards */}
              <div className="space-y-4">
                {/* Laspeyres */}
                <div className="p-5 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-bold text-white font-sans">
                      1. Higher-Level Master Index: Laspeyres Formulation
                    </h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-primary text-black font-bold">
                      PUBLISHED STANDARD
                    </span>
                  </div>
                  <div className="p-3 bg-canvas/80 rounded-lg border border-hairline my-2 font-mono text-center text-sm text-primary font-bold">
                    I_L^(t) = [ ∑ ( w_r · ( P_(r,t) / P_(r,0) ) ) ] × 100
                  </div>
                  <ul className="text-xs text-ink-muted space-y-1.5 list-disc list-inside mt-3">
                    <li><code className="text-accent-blue font-mono">w_r</code> : Fixed annual passenger volume weight for route corridor <code className="text-white font-mono">r</code> sourced from DGCA domestic passenger carriage statistics.</li>
                    <li><code className="text-accent-blue font-mono">P_(r,t)</code> : Composite price relative across all advance booking windows for route <code className="text-white font-mono">r</code> at day <code className="text-white font-mono">t</code>.</li>
                    <li><code className="text-accent-blue font-mono">P_(r,0)</code> : Standardized base period benchmark price (July 2026 baseline = 100.0).</li>
                  </ul>
                </div>

                {/* Jevons Micro-aggregation */}
                <div className="p-5 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-bold text-white font-sans">
                      2. Elementary Cell Micro-Aggregation: Jevons Geometric Mean
                    </h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-blue/10 text-accent-blue border border-accent-blue/30 font-bold">
                      MICRO-CELL FORMULA
                    </span>
                  </div>
                  <div className="p-3 bg-canvas/80 rounded-lg border border-hairline my-2 font-mono text-center text-sm text-accent-blue font-bold">
                    P_(r,w,t) = ( ∏_(k=1)^N p_(r,w,k,t) )^(1 / N)
                  </div>
                  <p className="text-xs text-ink-muted mt-2 leading-relaxed">
                    Within any given route-window cell (e.g. DEL-BOM at $T+7$), multiple airline carriers and flight departures exist. Following ILO recommendations, unweighted prices are aggregated geometrically to eliminate arithmetic mean upward bias.
                  </p>
                </div>

                {/* Superlative Matrix */}
                <div className="p-5 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-bold text-white font-sans">
                      3. Superlative Axiomatic Testing: Fisher Ideal & Paasche
                    </h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-rose/10 text-accent-rose border border-accent-rose/30 font-bold">
                      SUBSTITUTION AUDIT
                    </span>
                  </div>
                  <div className="p-3 bg-canvas/80 rounded-lg border border-hairline my-2 font-mono text-center text-sm text-accent-rose font-bold">
                    I_F^(t) = √( I_L^(t) × I_P^(t) )
                  </div>
                  <p className="text-xs text-ink-muted mt-2 leading-relaxed">
                    APIx runs daily parallel Fisher Ideal and Paasche computations to measure consumer substitution bias: <strong className="text-white font-mono">Bias = I_L - I_F</strong>. This verifies whether passengers substitute towards cheaper corridors during airfare spikes.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 3: DGCA ROUTE BASKET */}
          {activeSection === 'basket' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Representative Sample
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  DGCA Top 20 Domestic Air Route Basket
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  These 20 corridors represent over 65% of India's scheduled domestic passenger throughput. Weights are derived from statutory DGCA City-Pair Traffic Reports.
                </p>
              </div>

              {/* Advance booking windows */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="p-3 bg-card-elevated rounded-lg border border-hairline text-center">
                  <p className="text-[10px] font-mono text-ink-faint">Window 1</p>
                  <p className="text-sm font-mono font-bold text-primary">T+1 (Tomorrow)</p>
                  <p className="text-[10px] text-ink-muted mt-0.5">Weight: 22%</p>
                </div>
                <div className="p-3 bg-card-elevated rounded-lg border border-hairline text-center">
                  <p className="text-[10px] font-mono text-ink-faint">Window 2</p>
                  <p className="text-sm font-mono font-bold text-primary">T+7 (1 Week)</p>
                  <p className="text-[10px] text-ink-muted mt-0.5">Weight: 34% (Primary)</p>
                </div>
                <div className="p-3 bg-card-elevated rounded-lg border border-hairline text-center">
                  <p className="text-[10px] font-mono text-ink-faint">Window 3</p>
                  <p className="text-sm font-mono font-bold text-primary">T+15 (2 Weeks)</p>
                  <p className="text-[10px] text-ink-muted mt-0.5">Weight: 24%</p>
                </div>
                <div className="p-3 bg-card-elevated rounded-lg border border-hairline text-center">
                  <p className="text-[10px] font-mono text-ink-faint">Window 4</p>
                  <p className="text-sm font-mono font-bold text-primary">T+30 (1 Month)</p>
                  <p className="text-[10px] text-ink-muted mt-0.5">Weight: 14%</p>
                </div>
                <div className="p-3 bg-card-elevated rounded-lg border border-hairline text-center">
                  <p className="text-[10px] font-mono text-ink-faint">Window 5</p>
                  <p className="text-sm font-mono font-bold text-primary">T+45 (Advance)</p>
                  <p className="text-[10px] text-ink-muted mt-0.5">Weight: 6%</p>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto border border-hairline rounded-xl">
                <table className="w-full text-xs font-mono">
                  <thead className="bg-card-elevated border-b border-hairline text-ink-faint uppercase text-[10px]">
                    <tr>
                      <th className="py-2.5 px-3 text-left">Corridor</th>
                      <th className="py-2.5 px-3 text-left">Origin / Destination</th>
                      <th className="py-2.5 px-3 text-right">DGCA Weight</th>
                      <th className="py-2.5 px-3 text-left">Market Category</th>
                      <th className="py-2.5 px-3 text-right">Great Circle Distance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-hairline">
                    {ROUTE_BASKET.map((r) => (
                      <tr key={r.code} className="hover:bg-card-hover transition-colors">
                        <td className="py-2 px-3 font-bold text-primary">{r.code}</td>
                        <td className="py-2 px-3 text-white font-sans">{r.origin} ➔ {r.dest}</td>
                        <td className="py-2 px-3 text-right font-bold text-accent-blue">{r.weight}</td>
                        <td className="py-2 px-3 text-ink-muted font-sans">{r.share}</td>
                        <td className="py-2 px-3 text-right text-ink-faint">{r.distance}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 4: FARE UNBUNDLING */}
          {activeSection === 'unbundling' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Aviation Pricing Transparency
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  Fare Component Decomposition Model
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  Composite ticket prices are systematically deconstructed into five standardized tariff layers to track genuine airline pricing power vs. pass-through statutory airport charges.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-sm font-bold text-white">1. Base Airline Tariff</h3>
                    <span className="w-3 h-3 rounded-full bg-primary" />
                  </div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Pure carrier seat fare determined by revenue management inventory buckets. This is the only component driven by airline supply-demand elasticity.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-sm font-bold text-white">2. User Development Fee (UDF)</h3>
                    <span className="w-3 h-3 rounded-full bg-accent-blue" />
                  </div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Airports Economic Regulatory Authority (AERA) approved airport development charges. Distinct per airport and independent of carrier pricing.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-sm font-bold text-white">3. Statutory Taxes & Regulatory</h3>
                    <span className="w-3 h-3 rounded-full bg-accent-emerald" />
                  </div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Goods and Services Tax (GST 5% economy / 12% business), Aviation Security Fee (ASF ₹236), and Passenger Service Fee (PSF).
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline">
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-sm font-bold text-white">4. Convenience / Platform Fee</h3>
                    <span className="w-3 h-3 rounded-full bg-accent-rose" />
                  </div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Fixed charges levied by Online Travel Agencies (MakeMyTrip, EaseMyTrip) or airline direct portals (₹250–₹450) per passenger booking.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline md:col-span-2">
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-sm font-bold text-white">5. Ancillary Surcharges & Fuel (ATF)</h3>
                    <span className="w-3 h-3 rounded-full bg-ink-muted" />
                  </div>
                  <p className="text-xs text-ink-muted leading-relaxed">
                    Aviation Turbine Fuel surcharges, seat selection premiums, checked baggage overages, and travel insurance options.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 5: CPI TRANSMISSION */}
          {activeSection === 'transmission' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Monetary Policy Linkage
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  CPI Passthrough Transmission Mechanism
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  How airfare swings feed mathematically into MoSPI's official Headline Consumer Price Index and the Transport & Communication subgroup.
                </p>
              </div>

              <div className="p-5 rounded-xl bg-card-elevated border border-hairline space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                  <div className="p-3 bg-canvas/60 border border-hairline rounded-lg">
                    <p className="text-[11px] text-ink-muted">Transport & Comm CPI Weight</p>
                    <p className="text-xl font-mono font-bold text-white mt-1">8.59%</p>
                    <p className="text-[10px] text-ink-faint">National CPI Basket</p>
                  </div>
                  <div className="p-3 bg-canvas/60 border border-hairline rounded-lg">
                    <p className="text-[11px] text-ink-muted">Airfare Share in Transport</p>
                    <p className="text-xl font-mono font-bold text-white mt-1">3.85%</p>
                    <p className="text-[10px] text-ink-faint">Civil Aviation Sub-group</p>
                  </div>
                  <div className="p-3 bg-canvas/60 border border-hairline rounded-lg">
                    <p className="text-[11px] text-ink-muted">Effective Headline Weight</p>
                    <p className="text-xl font-mono font-bold text-primary mt-1">0.3307%</p>
                    <p className="text-[10px] text-ink-faint">Direct CPI Impact</p>
                  </div>
                </div>

                <div className="p-4 bg-canvas/80 rounded-xl border border-hairline">
                  <p className="text-xs font-mono uppercase text-ink-faint mb-1">Transmission Equation</p>
                  <p className="text-sm font-mono font-bold text-primary">
                    ΔHeadline CPI (bps) = ΔAPIx (%) × 0.0385 × 0.0859 × 100
                  </p>
                  <p className="text-xs text-ink-muted mt-2">
                    A +10% nationwide surge in airfare transmits approximately <strong className="text-white font-mono">+3.85 bps</strong> to the Transport subgroup and <strong className="text-white font-mono">+0.33 bps</strong> to Headline CPI.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 6: SCRAPERS & GOVERNANCE */}
          {activeSection === 'scrapers' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Data Acquisition
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  Stealth Scraper Architecture & Ethics
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  APIx operates a lightweight, polite scraping cluster engineered to extract public tariffs without overloading airline servers or violating cyber statutes.
                </p>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-4 rounded-xl bg-card-elevated border border-hairline flex items-start gap-3">
                  <span className="text-base text-primary font-mono font-bold">01</span>
                  <div>
                    <h3 className="font-bold text-white text-sm">TLS Fingerprint Impersonation</h3>
                    <p className="text-ink-muted mt-0.5">
                      Uses <code className="text-primary font-mono">curl_cffi</code> to match legitimate browser JA3/JA4 TLS handshake signatures, avoiding bot challenges without heavy headless browser overhead.
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline flex items-start gap-3">
                  <span className="text-base text-primary font-mono font-bold">02</span>
                  <div>
                    <h3 className="font-bold text-white text-sm">Randomized Jitter & Throttling</h3>
                    <p className="text-ink-muted mt-0.5">
                      Enforces mandatory 1.5s–3.5s randomized intervals between route requests, ensuring server loads remain virtually indistinguishable from organic user traffic.
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-card-elevated border border-hairline flex items-start gap-3">
                  <span className="text-base text-primary font-mono font-bold">03</span>
                  <div>
                    <h3 className="font-bold text-white text-sm">Synthetic Mock Mode for Offline Operation</h3>
                    <p className="text-ink-muted mt-0.5">
                      When <code className="text-primary font-mono">MOCK_MODE=true</code> is set, the system serves pre-generated multi-year synthetic price archives with zero live network calls.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 7: API SPECIFICATION */}
          {activeSection === 'api' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Developer Interface
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  RESTful & WebSocket API Specification
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  All requests require a Bearer token: <code className="text-primary font-mono">Authorization: Bearer &lt;API_TOKEN&gt;</code>.
                </p>
              </div>

              <div className="space-y-6">
                {API_ENDPOINTS.map((grp) => (
                  <div key={grp.category} className="space-y-3">
                    <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-ink-faint">
                      {grp.category}
                    </h3>
                    <div className="space-y-2">
                      {grp.items.map((item) => (
                        <div
                          key={item.path}
                          className="p-3 bg-card-elevated border border-hairline rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-hairline-strong transition-colors"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                                  item.method === 'GET'
                                    ? 'bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30'
                                    : 'bg-accent-blue/10 text-accent-blue border border-accent-blue/30'
                                }`}
                              >
                                {item.method}
                              </span>
                              <span className="font-mono text-xs font-semibold text-white">
                                {item.path}
                              </span>
                            </div>
                            <p className="text-[11px] text-ink-muted">{item.desc}</p>
                          </div>

                          <button
                            onClick={() => handleCopy(`curl -H "Authorization: Bearer dev-token" http://localhost:8000${item.path}`)}
                            className="px-2.5 py-1 rounded bg-card border border-hairline text-[10px] font-mono text-ink-muted hover:text-black hover:bg-primary hover:border-primary transition-colors self-start sm:self-auto shrink-0"
                            title="Copy cURL command"
                          >
                            {copiedEndpoint === `curl -H "Authorization: Bearer dev-token" http://localhost:8000${item.path}` ? '✓ Copied' : 'Copy cURL'}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION 8: SETUP & ENVIRONMENT */}
          {activeSection === 'deployment' && (
            <div className="bg-card border border-hairline rounded-xl p-6 space-y-6 shadow-sm">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-bold">
                  Infrastructure & Runtime
                </span>
                <h2 className="text-xl font-bold text-white mt-2 font-sans">
                  Environment Configuration & Local Setup
                </h2>
                <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                  Follow these standard instructions to spin up the local development stack with FastAPI, TimescaleDB, Celery, and Vite.
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-canvas/80 rounded-xl border border-hairline">
                  <p className="text-xs font-mono font-bold text-white mb-2">1. Quickstart with Docker Compose</p>
                  <pre className="text-xs font-mono text-primary bg-card p-3 rounded-lg overflow-x-auto border border-hairline">
                    docker-compose up -d --build
                  </pre>
                  <p className="text-[11px] text-ink-muted mt-2">
                    Launches API (port 8000), TimescaleDB (5432), Redis (6379), Celery Worker & Beat scheduler.
                  </p>
                </div>

                <div className="p-4 bg-canvas/80 rounded-xl border border-hairline">
                  <p className="text-xs font-mono font-bold text-white mb-2">2. Local Python Backend Setup</p>
                  <pre className="text-xs font-mono text-ink-body bg-card p-3 rounded-lg overflow-x-auto border border-hairline">
{`# Create virtualenv and install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Run FastAPI dev server
uvicorn app.main:app --reload --port 8000`}
                  </pre>
                </div>

                <div className="p-4 bg-canvas/80 rounded-xl border border-hairline">
                  <p className="text-xs font-mono font-bold text-white mb-2">3. Frontend Vite Development</p>
                  <pre className="text-xs font-mono text-ink-body bg-card p-3 rounded-lg overflow-x-auto border border-hairline">
{`cd frontend
npm install
npm run dev`}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
