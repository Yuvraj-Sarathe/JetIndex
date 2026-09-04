# `config/` — Static configuration (Yuvraj)

| File | Purpose | Edited by |
|---|---|---|
| `routes.yaml` | Sector basket (6 routes), lead times `[1,7,15,30,45]`, airport lat/lon, optional lead-time weights | Yuvraj; Sourabh/Abhay may add routes |
| `sources.yaml` | Per-scraper: `enabled`, `rate_limit_rps`, `max_retries`, `use_playwright_fallback`, `robots_paths_checked` | Sourabh/Abhay |
| `dgca_weights.csv` | `route_code,period,passengers` — placeholder values now; replace with real DGCA monthly traffic | Sourabh/Abhay |

Everything that is "a list of things we track" lives here, never hard-coded in Python/JS. `db/seed.py` loads these into the DB.
