# `scrapers/` — Multi-source stealth scraping engine

**Owners: Sourabh + Abhay** (Yuvraj supports)

## Mission
For every route in `config/routes.yaml` × lead time `{1,7,15,30,45}` × enabled source, fetch the **fare search response** (ideally the site's internal JSON/XHR API, not the rendered HTML), save it raw, and hand it to Vanshika's pipeline.

Priority order: **IndiGo → MakeMyTrip → Air India → Akasa → EaseMyTrip**. Two working sources is the MVP.

## Inputs / outputs
- **In:** `ScrapeJob(source, origin, destination, depart_date, lead_time, scrape_date)` built by `registry.build_jobs_for_date()`.
- **Out:** raw JSON at `data/raw/{source}/{scrape_date}/{ORIGIN}-{DEST}_T{lead}.json` + a row in `raw_quotes` (via `storage.save_raw`). Never parse/normalise here — that's `pipeline/`.

## Files
| File | What to build |
|---|---|
| `base_scraper.py` | `BaseScraper.fetch()` is the shared loop: build request → curl_cffi with impersonated TLS → check `parse_ok` → retry with new proxy on 403/429/5xx (tenacity, exponential backoff, max 4) → Playwright fallback → `save_raw`. Subclasses only implement `build_request()` and `parse_ok()`. |
| `indigo.py` | Fill in endpoint URL, headers, JSON body template found via DevTools. Watch for API keys/tokens in headers that rotate. |
| `makemytrip.py` | Same. MMT is heavier on anti-bot (Akamai); expect Playwright fallback to be needed for token bootstrap, then reuse cookies with curl_cffi. |
| `airindia.py` | Stub — pick up after MVP. |
| `proxy_manager.py` | Round-robin over `PROXY_URL` list, mark bad on 403/429, cool-down, `PROXY_ENABLED=false` → direct connection. |
| `session_manager.py` | Persist cookies/tokens per source to `data/raw/.sessions/{source}.json`; refresh when expired. |
| `fingerprints.py` | `impersonate` profiles for curl_cffi (`chrome124`, `safari17_0` …) + matching `User-Agent` / `sec-ch-ua` headers. Rotate per job. |
| `playwright_fallback.py` | `async fetch_with_browser(job)` using `playwright-stealth`, intercept the XHR response body (page.on("response")), don't scrape DOM. |
| `storage.py` | `save_raw()` — writes file + DB row; must never crash the scrape if DB is down. |
| `registry.py` | `SCRAPERS` dict, `get_scraper()`, `build_jobs_for_date()`. |
| `recon/` | Your notes, HAR exports (gitignored), endpoint docs. See `recon/README.md`. |

## Step-by-step
1. **Recon (Day 1):** open IndiGo search in Chrome → DevTools → Network → filter `Fetch/XHR` → do a DEL→BOM one-way search → find the response containing fares → right-click → *Copy as cURL (bash)*. Paste into `recon/indigo_endpoint.md`. Note: URL, method, required headers, body, which cookies/tokens are needed and where they come from. Repeat for MMT.
2. Convert the cURL to `curl_cffi.requests.Session(impersonate="chrome124")`. Get **one** successful response saved to `tests/fixtures/indigo_sample.json` (strip personal data) — **this unblocks Vanshika**.
3. Implement `build_request()` / `parse_ok()` in `indigo.py`; run `make scrape ROUTE=DEL-BOM LEAD=7 SOURCE=indigo`.
4. Implement `proxy_manager.py` and `session_manager.py`; test 403/429 handling by hammering with a low delay once (then don't).
5. Build Playwright fallback; verify it triggers only when curl_cffi fails N times.
6. Repeat for MakeMyTrip. Then Air India if time permits.
7. Wire into `app/tasks/scrape_tasks.py` with Yuvraj; run a full 6×5×2 = 60-job sweep and time it.

## Rules of engagement (ethics — graders check this)
- Respect `robots.txt` for the paths you hit; document any grey areas in `docs/ethics_and_compliance.md`.
- ≤ **1 request / 3 s per source per IP** (`rate_limit_rps` in `config/sources.yaml`), random jitter 1–4 s.
- Only anonymous search flows. **Never** log in, hold seats, or start a booking.
- Off-peak schedule (02:00 IST). Store raw payloads only for audit.
- No credentials or proxy URLs in code — use `.env`.

## Definition of done
- `make scrape` succeeds for both sources for all 6 routes × 5 lead times.
- Failure rate < 10% per sweep with retries; fallback works.
- `tests/test_scrapers/` covers job building, retry logic (mocked), and storage path format.
