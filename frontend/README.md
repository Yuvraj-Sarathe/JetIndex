# `frontend/` — APIx Dashboard (React + Vite + Tailwind)

**Owner: Mehak**

## Mission
An analyst-grade dashboard for MoSPI/RBI showing the daily APIx, route heatmap, lead-time elasticity, fare unbundling, and the DGCA backtest — with time-range filters and CSV/JSON export.

## Run
```bash
cd frontend
cp .env.example .env        # VITE_API_BASE=/api/v1  VITE_API_TOKEN=change-me-dev-token
npm ci
npm run dev                 # http://localhost:5173 (proxies /api → :8000)
```
The API runs in **mock mode** by default, so all endpoints return realistic data from Day 1. Do **not** hard-code data in the frontend — always fetch.

## Stack
React 18 (JSX) · Vite · TailwindCSS 3 · Recharts · react-leaflet + Leaflet · date-fns · papaparse (CSV export)

## Components to build (`src/components/`)
| Component | Data | Notes |
|---|---|---|
| `MetricCard.jsx` | `/apix/daily` | Headline APIx today, DoD %, WoW %, MoM %; green/red arrows |
| `ApixTrend.jsx` | `/apix/daily\|weekly\|monthly` | Recharts `LineChart`, toggle granularity, overlay `apix_base_only` |
| `Heatmap.jsx` | `/routes/heatmap` | Leaflet map of India; polylines between airports colored by volatility, width by weight; tooltip with avg fare |
| `ElasticityCurve.jsx` | `/elasticity` | Fare vs lead time (T+45 → T+1) per route; route selector |
| `UnbundlingInspector.jsx` | `/quotes` | Stacked bar: base / udf / taxes / convenience / other, by carrier; table of raw quotes below |
| `BacktestChart.jsx` | `/backtest` | APIx (rebased) vs DGCA monthly avg; show MAPE badge |
| `TimeRangeFilter.jsx` | — | presets 7/30/90d + custom; lifts state to `Dashboard.jsx` |
| `ExportButton.jsx` | current view | CSV + JSON download |

`src/pages/Dashboard.jsx` composes them in a responsive grid (2 cols desktop, 1 mobile). `src/api/client.js` already wraps fetch with the bearer token — extend, don't bypass.

## Step-by-step
1. `npm run dev`, confirm `MetricCard` shows mock APIx.
2. Build `ApixTrend` + `TimeRangeFilter` (they share state).
3. `Heatmap` — airports lat/lon come from `/routes`; use `Polyline` + `CircleMarker`.
4. `ElasticityCurve`, `UnbundlingInspector`, `BacktestChart`.
5. `ExportButton`; loading skeletons; error toasts when API is down.
6. Polish for the demo video: dark/light, MoSPI-ish header, "Last updated 02:00 IST" badge, a "Trigger sweep" button calling `POST /admin/trigger-sweep`.

## Conventions
- Colors: Tailwind `slate` base, `indigo` accent, `emerald`/`rose` for up/down.
- Format money with `utils/format.js` (`₹4,250`), dates in IST for display.
- Keep components dumb; data fetching in `hooks/useApix.js`.
- `npm run lint` and `npm run build` must pass (CI).
