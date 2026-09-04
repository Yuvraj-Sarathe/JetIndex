# `engine/` — Index math, elasticity & DGCA backtest

**Owners: Sourabh + Abhay** (Yuvraj supports)

## Mission
Turn clean quotes into the **daily APIx** using a **DGCA passenger-weighted Laspeyres index**, produce weekly/monthly rollups and lead-time elasticity, and **backtest ≥ 30 days against DGCA monthly average fares**.

## The formula
```
I_t = Σ_i ( P_{i,t} · Q_{i,0} ) / Σ_i ( P_{i,0} · Q_{i,0} ) × 100
```
- `i` = route in basket · `P_{i,t}` = representative price of route i on day t · `Q_{i,0}` = DGCA passenger volume weight (base period) · `P_{i,0}` = base-period price.
- **Representative price:** median `total_fare` across carriers & non-stop flights, per lead time; then aggregate lead times (default: simple mean of the 5 lead-time medians; optional: lead-time weights from `config/routes.yaml`).
- **Base period:** first 7 days of collected data (mean) = 100. Store `base_period` in `apix_daily`.
- Also compute `apix_base_only` using `base_fare` only (shows tax/fee inflation separately — nice talking point).
- Optional: Geometric Young index for comparison.

## Files
| File | What to build |
|---|---|
| `weights.py` | load `dgca_weights`, normalise to sum 1, handle missing routes |
| `index_calculator.py` | `laspeyres()`, `geometric_young()`, `compute_daily(date)` → writes `apix_daily` |
| `aggregator.py` | weekly/monthly means, `pct_change` helpers |
| `elasticity.py` | matrix route × lead_time of median fares; elasticity = d ln(P) / d ln(lead_time) via `scipy.stats.linregress` |
| `backtest.py` | monthly mean of APIx-implied fares vs `dgca_benchmark`; output MAPE, RMSE, Pearson r; write `data/backtest_results.json`; plot PNG to `docs/img/` |
| `run.py` | CLI: `python -m engine.run --date … [--rebuild]`, `--backtest` |

## Step-by-step
1. Unit-test `laspeyres()` with a hand-computed 3-route example (`tests/test_engine/`).
2. Run `compute_daily` on `data/mock/fare_quotes.json` → should reproduce `data/mock/apix_daily.json` roughly.
3. Get real DGCA data: monthly traffic reports (for weights) and any published average-fare series → put in `data/reference/`, document source URLs in `docs/index_methodology.md`.
4. Backtest: since we can't scrape the past, use (a) our own 30+ days of collection and (b) a synthetic back-fill from historical fare datasets (e.g., public Kaggle Indian flight-price datasets) — be explicit about which in the doc.
5. Expose functions to Yuvraj: `get_daily_series(from,to)`, `get_heatmap(date)`, `get_elasticity(route)`, `get_backtest()`.

## Definition of done
- `make index DATE=…` writes `apix_daily`; `make backtest` prints MAPE and writes JSON + PNG.
- Methodology written up in `docs/index_methodology.md` (Sneh will reuse it in slides).
