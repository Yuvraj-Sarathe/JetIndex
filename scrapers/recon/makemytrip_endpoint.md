# MakeMyTrip Flight Search Endpoint Recon

## Overview
* **URL:** `https://flights.makemytrip.com/makemytrip/flight/search`
* **Method:** `POST`
* **Content-Type:** `application/json`
* **Target Environment:** Production (`flights.makemytrip.com` / `www.makemytrip.com`)

---

## Key Headers

- `x-flt`: Encoded search context / filter token
- `device-id` / `mcid`: Client device UUID
- `domain` / `region`: Regional routing headers (`in`)
- `pfm`: Platform identifier (`DESKTOP`)
- `origin` / `referer`: Must point to `https://www.makemytrip.com`
- `Cookie`: Required session & Akamai Bot Manager cookies (`_abck`, `bm_sz`, `ak_bmsc`, `bm_s`, `bm_so`)

## Request Body Shape

- `it`: Route itinerary string in format `{ORIGIN}-{DESTINATION}-{YYYYMMDD}` (e.g. `DEL-BOM-20260906`)
- `pax`: Passenger counts string (e.g. `A-1_C-0_I-0` for 1 Adult, 0 Child, 0 Infant)
- `cc`: Cabin class code (`E` for Economy)
- `cur`: Currency code (`INR`)
- `crId`: Search correlation / session UUID
- `pfm`: Platform (`DESKTOP`)
- `rkeys`: List of flight listing keys
- `user-agent`: Standard browser User-Agent (Chrome / macOS or Windows)
- `sec-ch-ua`: `"Chromium";v="124", "Google Chrome";v="124"`
- `sec-ch-ua-platform`: `"macOS"`

---

## Dynamic Parameters & Request Body Shape

The payload is structured as follows:

```json
{
  "tripType": "OW",
  "itinerary": [
    {
      "from": "DEL",
      "to": "BOM",
      "departureDate": "2026-10-13"
    }
  ],
  "paxInfo": {
    "adults": 1,
    "children": 0,
    "infants": 0
  },
  "cabinClass": "E"
}
```

### Parameter Mapping:
* **Trip Type:** `tripType` (`"OW"` for One-Way, `"RT"` for Round-Trip)
* **Origin Airport:** `itinerary[0].from` (3-letter IATA code, e.g. `"DEL"`)
* **Destination Airport:** `itinerary[0].to` (3-letter IATA code, e.g. `"BOM"`)
* **Departure Date:** `itinerary[0].departureDate` (format: `YYYY-MM-DD`, e.g. `"2026-10-13"`)
* **Adult Passenger Count:** `paxInfo.adults` (integer, default `1`)
* **Children Count:** `paxInfo.children` (integer, default `0`)
* **Infant Count:** `paxInfo.infants` (integer, default `0`)
* **Cabin Class:** `cabinClass` (`"E"` for Economy, `"PE"` for Premium Economy, `"B"` for Business)

---

## Anti-bot & Token Lifecycle (Akamai Bot Manager)
* **WAF Protection:** MakeMyTrip deploys heavy Akamai Bot Manager protection.
* **Akamai Tracking Cookies:**
  * `_abck`: Sensor score / telemetry token (must be evaluated via JavaScript sensor script).
  * `bm_sz`: Akamai bot signature cookie.
  * `bm_sv`: Session verification cookie.
  * `ak_bmsc`: Behavioral state machine tracking cookie.
* **Session Lifecycle:**
  * Initial page visit loads telemetry scripts (`akamai/sensor.js`).
  * Telemetry triggers and returns signed `_abck` valid cookie.
* **Stealth Strategy:**
  1. Primary: Use Playwright headless/stealth browser session to bootstrap valid session cookies (`_abck`, `bm_sz`).
  2. Secondary: Reuse session cookies with `curl_cffi` using Chrome impersonation (`impersonate="chrome124"`).
  3. Fallback: If 403 Forbidden or captcha challenge is detected, switch to full Playwright stealth fallback to complete the search sweep.

---

## Response Schema Outline
The API returns structured flight offers:

```json
{
  "searchResult": {
    "flightOffers": [
      {
        "airline": {
          "code": "6E",
          "name": "IndiGo"
        },
        "flightNumber": "6E-2054",
        "departure": "2026-10-13T06:00:00",
        "arrival": "2026-10-13T08:15:00",
        "stops": 0,
        "duration": 135,
        "fare": {
          "totalFare": 4500,
          "breakdown": {
            "baseFare": 3600,
            "taxes": 550,
            "convenienceFee": 350
          }
        },
        "refundable": false,
        "seatsLeft": 5
      }
    ]
  }
}
```

---

## Full cURL Command (Bash Formatted)

```bash
curl --location 'https://flights.makemytrip.com/makemytrip/flight/search' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'content-type: application/json' \
  -H 'origin: https://www.makemytrip.com' \
  -H 'referer: https://www.makemytrip.com/flight/search' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  --data '{
    "tripType": "OW",
    "itinerary": [
      {
        "from": "DEL",
        "to": "BOM",
        "departureDate": "2026-10-13"
      }
    ],
    "paxInfo": {
      "adults": 1,
      "children": 0,
      "infants": 0
    },
    "cabinClass": "E"
  }'
```
