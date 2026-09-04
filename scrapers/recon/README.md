# `scrapers/recon/` — Endpoint reconnaissance notes

Keep one markdown file per source: `indigo_endpoint.md`, `makemytrip_endpoint.md`, …

Template for each file:
1. **Search URL** you used in the browser.
2. **XHR endpoint**: method, URL, query params.
3. **Required headers** (paste, redact tokens as `<TOKEN>`).
4. **Body template** with placeholders `{origin}`, `{destination}`, `{date}`.
5. **Auth/token flow**: where the token/cookie comes from, TTL, how to refresh.
6. **Response shape**: path to the fare array, fields for base/tax/fee breakdown, sold-out marker.
7. **Anti-bot observed**: Cloudflare/Akamai headers, challenge pages, rate-limit status codes.

`*.har` and `*.json` in this folder are gitignored — share sensitive captures privately.
