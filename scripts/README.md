# `scripts/`

| Script | Use |
|---|---|
| `generate_mock_data.py` | Regenerates `data/mock/*.json` deterministically (seeded). Run after schema changes. |
| `run_local_sweep.sh` | One route/lead/source scrape without proxy, prints raw file path. |
| `wait_for_db.sh` | Used by compose to wait for Postgres before migrations. |
