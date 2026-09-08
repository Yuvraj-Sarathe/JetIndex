# Ethics & Compliance

## Scraping Policy

| Principle | Implementation |
|---|---|
| **Rate limiting** | ≤1 request/3 seconds per source per IP (`rate_limit_rps: 0.33`) |
| **robots.txt** | Respected for all targeted endpoints (`robots_paths_checked: true` in `sources.yaml`) |
| **Off-peak scheduling** | Scraping runs at 02:00 IST via Celery Beat |
| **Retry discipline** | Max 4 retries with exponential backoff; stops on persistent blocks |
| **IP protection** | Proxy rotation with cooldown on 403/429; no IP stampeding |

## Data Handling

| Principle | Implementation |
|---|---|
| **No login/booking** | Only anonymous search flows — never books or holds seats |
| **No personal data** | Only collects fare prices, routes, and flight metadata |
| **Audit trail** | Raw scraper payloads retained in `data/raw/` for reproducibility |
| **No resale** | Data used solely for the APIx index computation |
| **Minimal collection** | Scrapes only the 6-route DGCA basket needed for the index |

## Legal Posture

- Scraping **publicly available pricing data** from airline and OTA websites
- No circumvention of paywalls, authentication, or access controls
- TLS fingerprint impersonation (`curl_cffi`) is used for anti-bot resilience, not for impersonating authenticated sessions
- Terms of Service review documented per-source in `scrapers/recon/`

## DGCA Data Attribution

| Dataset | Source | Coverage |
|---|---|---|
| Passenger traffic weights | DGCA "City Pair Wise Passenger Traffic" FY 2024–25 | 6 routes, 23.1M passengers |
| Monthly average fares | Kaggle ["India Aviation Traffic Data"](https://github.com/Vonter/india-aviation-traffic) by Vonter — compiled from DGCA published reports | Jan 2024 – Nov 2025, 32 data points |

**Note on data freshness:** DGCA's online portal has not been updated with recent monthly figures in a timely manner. We use the most recent available official data and a well-sourced Kaggle aggregation that compiles the same DGCA reports into a machine-readable format. The underlying data is DGCA-sourced.

## Transparency

- All data files are committed to the repository (`config/dgca_weights.csv`, `config/dgca_monthly_avg_fare.csv`)
- Backtest results are computed from real data, not random numbers
- Historical backfill data is clearly marked with `source = "dgca_backfill"` and `quality_flag = "ok"` in the database
- The API serves mock data by default (`MOCK_MODE=true`) for demo safety; real data requires explicit configuration
