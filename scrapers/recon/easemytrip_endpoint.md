# EaseMyTrip Flight Search Endpoint Recon

## Overview

* **URL:** `https://flightservice-node.easemytrip.com/AirAvail_Lights/AirBus_New?_=1788696063212&ngsw-bypass=true`
* **Method:** `POST`
* **Content-Type:** `application/json`

## Key Headers

* `Origin` / `Referer`: Must point to `https://www.easemytrip.com/`
* `Accept`: `application/json, text/plain, */*`

## Request Body Shape

* `org`: 3-letter IATA origin airport code (e.g., `"DEL"`)
* `dept`: 3-letter IATA destination airport code (e.g., `"BOM"`)
* `deptDT`: Departure date in `YYYY-MM-DD` format (e.g., `"2026-09-06"`)
* `arrDT`: Return arrival date if roundtrip (empty string for one-way)
* `adt` / `chd` / `inf`: Passenger count strings for adult, child, and infant
* `isDomestic` / `isOneway`: Search criteria boolean flags (`true`)
* `currCode`: Currency code (e.g., `"INR"`)
* `Cabin`: Cabin class identifier integer (`0` for Economy)
* `TKN`: Session security validation token string
* `TraceId` / `queryname`: Unique search transaction UUIDs
* `serviceid`: Service backend routing tag (`"EMTSERVICE;"`)

## cURL Command

```bash
curl 'https://flightservice-node.easemytrip.com/AirAvail_Lights/AirBus_New?_=1788696063212&ngsw-bypass=true' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: application/json' \
  -H 'Referer: https://www.easemytrip.com/' \
  -H 'Origin: https://www.easemytrip.com' \
  -H 'Sec-GPC: 1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'Connection: keep-alive' \
  --data-raw '{"org":"DEL","dept":"BOM","adt":"1","chd":"0","inf":"0","deptDT":"2026-09-06","arrDT":"","userid":"","IsDoubelSeat":false,"isDomestic":true,"isOneway":true,"airline":"undefined","Cabin":0,"currCode":"INR","appType":1,"isSingleView":false,"ResType":2,"IsNBA":false,"CouponCode":"","IsArmedForce":false,"AgentCode":"","IsWLAPP":false,"IsFareFamily":false,"serviceid":"EMTSERVICE;","serviceDepatment":"","IpAddress":"","LoginKey":"","UUID":"","TKN":"xYwdl5M/EAwA6ZbckMSawbaK4Sdn6lNRZe1/S1OQ0CFNDz30Yq9ZZFHgdhRGBLJpLphyI0Qh32cDqENe4OcwHg==","TraceId":"80311701-3a24-4827-89e2-1d0b2d7a5ef5","queryname":"80311701-3a24-4827-89e2-1d0b2d7a5ef5","FareTypeUI":0}'
```
