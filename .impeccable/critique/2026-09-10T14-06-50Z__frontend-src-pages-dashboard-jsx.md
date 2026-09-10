---
target: entire project
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 2
target_identity: "file:/Users/sourabhpatne16/Developer/JetIndex/frontend/src/pages/Dashboard.jsx"
target_fingerprint: "sha256:92e6a19e5fc6f0c35feede65e0905b0e42a68d73db5fe5880a349f579a9bc5b5"
target_path: /Users/sourabhpatne16/Developer/JetIndex/frontend/src/pages/Dashboard.jsx
timestamp: 2026-09-10T14-06-50Z
slug: frontend-src-pages-dashboard-jsx
closed: true
---
# Design Critique: JetIndex / APIx Dashboard (Entire Project)

**Target**: `frontend/src/pages/Dashboard.jsx` (and overall Frontend Application)
**Date**: 2026-09-10
**Design Health Score**: 24 / 40 (Rating Band: Needs Work / Mediocre)

## Nielsen's 10 Heuristics Scorecard

| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3/4 | "Last Updated" is displayed, but lacks live polling indicator or ingestion heartbeat. |
| 2 | Match Between System and Real World | 3/4 | Domain terminology (APIx, DoD %, MAPE, DGCA) is accurate to civil aviation economics. |
| 3 | User Control and Freedom | 2/4 | Tabs are state-only (no URL routing or back-button support); custom date range cannot be easily reset. |
| 4 | Consistency and Standards | 2/4 | Disconnected from `DESIGN.md` tokens; cards and tables vary in paddings and border styles across tabs. |
| 5 | Error Prevention | 3/4 | Date inputs lack min/max bounds and inline range validation. |
| 6 | Recognition Rather Than Recall | 2/4 | Heavy econometric acronyms (bps, MAPE, Laspeyres, z-score) lack contextual tooltips or definitions. |
| 7 | Flexibility and Efficiency of Use | 2/4 | 10 unranked flat tabs; no keyboard shortcuts or analyst presets (e.g. "Diwali Peak", "Monsoon Dip"). |
| 8 | Aesthetic and Minimalist Design | 2/4 | Generic Tailwind gray-box aesthetic (`bg-slate-50`, `border-slate-200`); lacks authoritative Sentry-grade craft. |
| 9 | Help Users Recognize/Recover from Errors | 3/4 | Generic error banner on fetch failure without a retry button or offline diagnostics. |
| 10 | Help and Documentation | 2/4 | AI Analyst tab exists, but no onboarding guide or embedded methodology primer for policymakers. |
| **Total** | | **24/40** | **Needs Refinement** |

## Design Specificity Verdict

- **LLM Assessment**: The current UI suffers from "Tailwind Template Syndrome". While functional, it presents itself as an unstyled generic admin prototype rather than a premier, mission-critical national airfare index built for MoSPI and RBI leadership. The recently installed `DESIGN.md` (Sentry-inspired dark-canvas `#150f23`, deep violet, and lime accents) is completely unused in the code, leaving the application stranded in default `slate-50` / `blue-600` styling.
- **Deterministic Scan**: 
  - `frontend/src/index.css`: Warning for overused font (`Inter`).
  - Missing token integration between `DESIGN.md` and `frontend/tailwind.config.js`.
- **Browser Visualization**: All 10 tabs render without console errors, but visual hierarchy is flat and data density is suboptimal on high-resolution displays.

## Strengths (What's Working)
1. **Strong Functional Depth**: Seamless mock-mode integration across all 10 views (Forecast, Anomalies, Data Quality, Heatmap, Backtest, and interactive AI Analyst).
2. **Interactive Econometric Visualizations**: Recharts integration handles 14-day forecast confidence intervals and DGCA backtest curves cleanly.
3. **Responsive Core Controls**: Time range filter (7D/30D/90D/1Y) and export utilities (CSV/JSON) are immediately accessible.

## Priority Issues

1. **[P0] Aesthetic Disconnect & Missing Design System Tokens**
   - *Why*: `DESIGN.md` specifies a high-authority Sentry-inspired visual system (`#150f23` canvas, violet accents, lime highlights, uppercase tracked badges), but the code uses generic light-mode `slate-50` and `blue-500` with standard Inter type.
   - *Fix*: Map `DESIGN.md` color tokens, typography, and card treatments into `frontend/tailwind.config.js` and apply the dark/ink palette across the app shell and cards.
   - *Suggested Command*: `/impeccable bolder` or `/impeccable colorize`

2. **[P1] Information Architecture & Navigation Clutter (10 Flat Tabs)**
   - *Why*: Having 10 flat, unranked horizontal tabs (`Overview`, `Forecast`, `Anomalies`, `Data Quality`, `Alerts`, `Scenario`, `Temporal`, `Provenance`, `Validation`, `AI Analyst`) causes cognitive overload and forces horizontal overflow on laptops.
   - *Fix*: Restructure navigation into a sleek sidebar or categorized navigation (e.g. *Index Analytics*, *Modeling & Forecasts*, *Governance & Provenance*, *AI Assistant*) with URL routing.
   - *Suggested Command*: `/impeccable layout`

3. **[P1] Lack of Contextual Explanations & Policy Tooltips**
   - *Why*: Senior economists and policy officers (MoSPI/RBI) reviewing anomalies or elasticity need immediate contextual definitions for metrics like *z-score*, *basis points*, *unbundled fare delta*, and *Laspeyres base*.
   - *Fix*: Add micro-tooltips, glossary hover cards, and formula breakdowns on metric cards and anomaly feeds.
   - *Suggested Command*: `/impeccable clarify`

4. **[P2] Route Heatmap Visual Clash**
   - *Why*: The Leaflet map uses standard bright OpenStreetMap tiles, creating a jarring visual contrast with dark analytical charts and modern enterprise styling.
   - *Fix*: Switch to CartoDB Dark Matter / Positron tiles or custom vector map styling that matches the dark canvas.
   - *Suggested Command*: `/impeccable polish`

## Persona Red Flags
- **Dr. Sharma (Senior Economic Advisor, MoSPI)**: Needs to cite numbers in official briefings. Red flag: Cannot easily print or share a permalink to an anomaly or backtest chart because tab state is in-memory only and lacks an executive summary view.
- **Priya (Airline Revenue Analyst)**: Monitors route price spikes and lead-time elasticity. Red flag: 10 horizontal tabs require repetitive manual scanning with no quick filters, density toggles, or keyboard shortcuts.
- **Rohan (First-time Policy Reviewer)**: Unfamiliar with APIx terminology. Red flag: Confronted with raw z-scores and MAPE figures without inline tooltips or plain-language translations.
