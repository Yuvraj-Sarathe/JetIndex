# Akasa Air Flight Search Endpoint Recon

## Overview

* **URL:** `https://prod-bl.qp.akasaair.com/api/ibe/availability/search`
* **Method:** `POST`
* **Content-Type:** `application/json`

## Key Headers

* `Authorization`: Session authorization token / signature string required for search
* `Origin` / `Referer`: Must point to `https://www.akasaair.com/`

## Request Body Shape

* `criteria[0].stations.originStationCodes`: Array of 3-letter IATA origin airport codes (e.g., `["DEL"]`)
* `criteria[0].stations.destinationStationCodes`: Array of 3-letter IATA destination airport codes (e.g., `["BOM"]`)
* `criteria[0].stations.searchOriginMacs` / `searchDestinationMacs`: Boolean flags for Metropolitan Area Codes (`true`)
* `criteria[0].dates.beginDate`: Flight date in ISO format (`YYYY-MM-DDTHH:mm:ss`)
* `criteria[0].filters`: Filter criteria including `compressionType`, `maxConnections`, `productClasses` (`["NB", "LB", "EC", "AV"]`), and `fareTypes` (`["NB", "LB", "R", "V"]`)
* `passengers.types`: Array of passenger counts and types (e.g., `[{"type": "ADT", "count": 1}]`)
* `codes.currencyCode`: Currency (e.g., `"INR"`)
* `codes.currentSourceOrganization`: Source organization identifier (e.g., `"QPGGLEMETA"`)
* `numberOfFaresPerJourney`: Maximum number of fare quotes to return per journey (e.g., `10`)
* `taxesAndFees`: Taxes and fees calculation indicator (`1`)

## cURL Command

```bash
curl 'https://prod-bl.qp.akasaair.com/api/ibe/availability/search' \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0' \
  -H 'Accept: application/json' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: application/json' \
  -H 'Referer: https://www.akasaair.com/' \
  -H 'Origin: https://www.akasaair.com' \
  -H 'Sec-GPC: 1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'Authorization: dRzkj9cuKoL4HItQtGZBXHc/Wc1i2l+dnsR9DUqQmTkeVhYYQ1Z0GjPnyEwbN/MhWIKvyxhDuzlNkCf2BJmmX7TZiKgeFLJJtPuiNFXtwKJu+Ye/i6yQDtCdk9hLrx39AujewVl+8sC82m6sUvgAqDBXDAzk/4Q5KuwkywHVcH/23w/7sxWepwU7X4G3vAAeFfVOCv3NzuProt7awaVjq8alhzDNVWpPLuGc03cvNgVFenOp82ge/q2aInyVfXpl1vMvf9I2Oq3E3F0ci0Ub0L2jrtqAyADyF9QnKACmVYDYYvBeSvg5aA==' \
  -H 'Connection: keep-alive' \
  -H 'TE: trailers' \
  --data-raw '{"criteria":[{"stations":{"originStationCodes":["DEL"],"destinationStationCodes":["BOM"],"searchDestinationMacs":true,"searchOriginMacs":true},"dates":{"beginDate":"2026-09-06T00:00:00"},"filters":{"compressionType":1,"maxConnections":8,"productClasses":["NB","LB","EC","AV"],"fareTypes":["NB","LB","R","V"]}}],"passengers":{"types":[{"type":"ADT","count":1}],"residentCountry":""},"codes":{"currencyCode":"INR","currentSourceOrganization":"QPGGLEMETA","promotionCode":""},"offerCode":null,"numberOfFaresPerJourney":10,"taxesAndFees":1}'
```
