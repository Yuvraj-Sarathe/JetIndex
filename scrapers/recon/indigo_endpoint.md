# IndiGo Flight Search Endpoint Recon

## Overview
* **URL:** `https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search`
* **Method:** `POST`
* **Content-Type:** `application/json`
* **Target Environment:** Production (`api-prod-flight-skyplus6e.goindigo.in`)

---

## Key Headers
* `authorization`: Required user session bearer JWT token (`Bearer eyJhbGci...`)
* `user_key`: Static API client key (`31e90be8fff2f5e2eea242c225f21b1a`)
* `origin`: `https://www.goindigo.in`
* `referer`: `https://www.goindigo.in/`
* `content-type`: `application/json`
* `user-agent`: Standard browser User-Agent (Chrome / macOS or Windows)
* `accept`: `*/*`
* `accept-language`: `en-US,en;q=0.9`

---

## Dynamic Parameters & Request Body Shape

The payload is structured as follows:

```json
{
  "codes": {
    "currency": "INR",
    "promotionCode": ""
  },
  "criteria": [
    {
      "dates": {
        "beginDate": "2026-10-13"
      },
      "flightFilters": {
        "type": "All"
      },
      "stations": {
        "originStationCodes": [
          "DEL"
        ],
        "destinationStationCodes": [
          "BOM"
        ]
      }
    }
  ],
  "passengers": {
    "residentCountry": "IN",
    "types": [
      {
        "count": 1,
        "discountCode": "",
        "type": "ADT"
      }
    ]
  },
  "taxesAndFees": "TaxesAndFees",
  "tripCriteria": "oneWay",
  "isRedeemTransaction": false
}
```

### Parameter Mapping:
* **Origin Airport:** `criteria[0].stations.originStationCodes` (array with 3-letter IATA code, e.g. `["DEL"]`)
* **Destination Airport:** `criteria[0].stations.destinationStationCodes` (array with 3-letter IATA code, e.g. `["BOM"]`)
* **Departure Date:** `criteria[0].dates.beginDate` (format: `YYYY-MM-DD`, e.g. `2026-10-13`)
* **Passenger Count:** `passengers.types[0].count` (integer, default `1`)
* **Passenger Type:** `passengers.types[0].type` (default `"ADT"`)
* **Currency:** `codes.currency` (default `"INR"`)

---

## Token Lifespan & Authentication Flow
* **Token Type:** JSON Web Token (JWT) issued during session bootstrap (`/v1/auth` / anonymous session).
* **Token Lifespan:** 15 minutes (`expiresInMilliSeconds: 900000`).
* **Header Format:** `Authorization: <JWT>` or `Authorization: Bearer <JWT>`.
* **Cookie Persistence:** `auth_token` and `auth_cookie` stored in browser cookies with expiry timestamp (`validTillMilliSeconds`).
* **Session Refresh Strategy:** When HTTP 401/403 is received or token expires, the session manager requests a new anonymous guest token or bootstraps via Playwright stealth session.

---

## Anti-bot & Akamai Observations
* **WAF / Bot Manager:** Akamai Bot Manager (`_abck`, `bm_sz`, `bm_sv`, `ak_bmsc`, `akaalb_sanjeevni_prod`).
* **Cookie Requirements:** Akamai sensor cookies (`_abck` valid marker) must accompany requests if TLS fingerprint is inspected.
* **Stealth Strategy:** Use `curl_cffi` with Chrome impersonation (`impersonate="chrome124"`) matching the `User-Agent` header, or Playwright stealth fallback on Akamai challenges.

---

## Response Schema Outline
The API returns a flight search hierarchy containing:
* `trips` / `flightFilter` / `fares`:
  * `journeys[]`: List of available flight journeys for the requested date.
  * `segments[]`: Flight number, departure time, arrival time, origin, destination.
  * `fares[]` / `fareFamilies[]`: Pricing tiers (`Saver`, `Flexi Plus`, `Super 6E`) with base fare, taxes, and fees breakdown.

---

## Full cURL Command (Bash Formatted)

```bash
curl --location 'https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpYmUiLCJqdGkiOiI1YWMwN2FkMC0wYTg3LThmNzctMTkyNS1kYzEzODViMWQ5ODciLCJpc3MiOiJkb3RSRVogQVBJIn0.gmU2BVLxLQCPzqpbYbRzRZ2cRHYkwGRBB6EvI2sbw88' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'origin: https://www.goindigo.in' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.goindigo.in/' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'user_key: 31e90be8fff2f5e2eea242c225f21b1a' \
  --data '{
    "codes": {
      "currency": "INR",
      "promotionCode": ""
    },
    "criteria": [
      {
        "dates": {
          "beginDate": "2026-10-13"
        },
        "flightFilters": {
          "type": "All"
        },
        "stations": {
          "originStationCodes": [
            "DEL"
          ],
          "destinationStationCodes": [
            "BOM"
          ]
        }
      }
    ],
    "passengers": {
      "residentCountry": "IN",
      "types": [
        {
          "count": 1,
          "discountCode": "",
          "type": "ADT"
        }
      ]
    },
    "taxesAndFees": "TaxesAndFees",
    "tripCriteria": "oneWay",
    "isRedeemTransaction": false
  }'
```
