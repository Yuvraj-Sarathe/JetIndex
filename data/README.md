# `data/` — Datasets

| Folder | Contents | Git? |
|---|---|---|
| `raw/` | Raw scraper payloads `raw/{source}/{date}/{ROUTE}_T{lead}.json` + `.sessions/` | **No** (gitignored) |
| `mock/` | Realistic fake API responses used when `MOCK_MODE=true`. Regenerate with `make mock-data` (`scripts/generate_mock_data.py`). Shapes must match `pipeline/schemas.py` and `app/schemas/responses.py`. | Yes |
| `reference/` | DGCA monthly avg fare CSV, DGCA traffic, `airports.csv`. Cite source URLs in `docs/index_methodology.md`. | Yes (small files only) |

Never commit anything with personal data or vendor tokens.
