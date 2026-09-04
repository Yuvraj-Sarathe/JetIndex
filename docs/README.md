# `docs/` — Documentation

**Owner: Sneh** (technical content supplied by each module owner)

| File | Purpose | Source of truth |
|---|---|---|
| `architecture.md` | **Max 2 pages.** Problem → architecture diagram → pipeline → schema → stealth strategy → index math → backtest. Exported to PDF for submission. | Everyone; outline pre-filled |
| `api_reference.md` | Endpoint table with sample requests/responses | Yuvraj (`/docs` OpenAPI) |
| `data_contract.md` | Human-readable `CleanQuote` + fee mapping | Vanshika |
| `index_methodology.md` | Laspeyres derivation, weights source, base period, rebasing, limitations | Sourabh + Abhay |
| `ethics_and_compliance.md` | robots.txt, rate limits, no-booking policy, data retention, legal posture | Sourabh + Abhay |
| `img/` | diagrams, backtest PNGs | |

## Step-by-step for Sneh
1. Read every folder README and this plan; draft `architecture.md` skeleton by Day 2 using the diagrams in the SIH PDF.
2. Collect from owners: API examples (Yuvraj), schema (Vanshika), formula + backtest numbers (Sourabh/Abhay), screenshots (Mehak).
3. Rewrite root `README.md` for judges: 30-second pitch, one-command run, screenshots, results.
4. Build `slides/pitch_deck.pptx` (5 slides: Problem · Scraping Stealth · Unbundling & Index Math · APIx vs DGCA · Impact).
5. Write `demo/video_script.md`, record the 2-min demo (see `demo/README.md`).
6. Export `architecture.md` → PDF; verify ≤ 2 pages.
