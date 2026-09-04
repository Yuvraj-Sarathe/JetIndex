# `pipeline/` — Cleaning, validation & fare unbundling

**Owner: Vanshika**

## Mission
Turn raw scraper payloads into **standardised, de-duplicated, outlier-free `CleanQuote` rows** where the total fare is split into `base_fare | udf | taxes | convenience_fee | other_fees`, then load them into `fare_quotes`.

You also own the **data contract** — `schemas.py` — which everyone else builds against. Finalise it on Day 1.

## Inputs / outputs
- **In:** raw JSON in `data/raw/{source}/{date}/…` (+ `raw_quotes` rows). Until real scrapes exist, use `tests/fixtures/*_sample.json`.
- **Out:** Polars DataFrame of `CleanQuote` → `fare_quotes` hypertable (via `loader.py`).

## Files
| File | What to build |
|---|---|
| `schemas.py` | **The contract.** `RawQuote`, `CleanQuote` (alias `FlightQuote`), `quality_flag` enum. Already drafted — review, tighten, then freeze. |
| `parsers/indigo_parser.py`, `parsers/makemytrip_parser.py` | `parse(payload, job_meta) -> list[RawQuote]`. Walk the vendor JSON, one `RawQuote` per flight × fare family. Put the vendor's fee labels **untouched** into `fare_breakdown`. |
| `validators.py` | `validate_raw()` — positive money, `depart_date > scrape_date`, `lead_time` matches, carrier allow-list, currency INR. Return `None` (and log) for junk. |
| `unbundler.py` | `unbundle(RawQuote) -> CleanQuote`. Mapping tables `INDIGO_FEE_MAP`, `MMT_FEE_MAP` from vendor labels → canonical components (see table below). Regex fallback for unknown labels. If `base + components != total` (±₹5) set `quality_flag="sum_mismatch"`. |
| `cleaner.py` | Polars: `dedupe()` on `(source, route_code, carrier, flight_no, depart_date, scrape_date, fare_class)`; `iqr_filter()` grouped by `(route_code, lead_time, scrape_date)`, k=1.5 on `total_fare`; `flag_sold_out()`; `clean_batch()` orchestrates. |
| `loader.py` | Upsert into `fare_quotes` (Sourabh/Abhay's `db/models.py`). |
| `run.py` | CLI: `python -m pipeline.run --date 2025-01-15 [--source indigo] [--dry-run]` prints counts: parsed / valid / unbundled / outliers / loaded. |

## Canonical component mapping
| Vendor label examples | Canonical field |
|---|---|
| Base Fare, Airfare, Fare | `base_fare` |
| UDF, User Development Fee, ADF | `udf` |
| PSF, ASF, Aviation Security Fee, GST, K3, CUTE fee | `taxes` |
| Convenience Fee, Service Fee, Platform Fee (OTA) | `convenience_fee` |
| Fuel Surcharge / YQ, Seat, Meal, Insurance (if bundled) | `other_fees` |

Document any new label you find in `docs/data_contract.md`.

## Step-by-step
1. **Day 1:** finalise `schemas.py`; run `python scripts/generate_mock_data.py` so `data/mock/` conforms to your schema; tell Mehak & Sourabh/Abhay it's frozen.
2. Write `indigo_parser.py` against `tests/fixtures/indigo_sample.json` (ask Sourabh/Abhay for it — it's their first deliverable). Test: parse → N `RawQuote`s.
3. Write `unbundler.py` + mapping; test that components sum to total on fixtures.
4. Write `cleaner.py`; craft a test with an injected ₹99,999 fare and assert it's flagged `iqr_outlier`.
5. Write `loader.py` once `db/models.py` exists; run `make pipeline DATE=…` end to end.
6. Edge cases: sold-out flights (keep row, flag, exclude from index), missing fare class, multi-stop (keep `stops`, engine filters to non-stop), duplicate flights across sources (keep both — different `source`).
7. Repeat parser for MakeMyTrip.

## Definition of done
- `make pipeline DATE=<day>` loads ≥ 90% of valid raw quotes with `quality_flag="ok"`.
- Unit tests in `tests/test_pipeline/` for parser, unbundler, IQR, dedupe.
- `docs/data_contract.md` matches `schemas.py`.
