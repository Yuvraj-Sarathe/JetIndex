# Air India Flight Search Endpoint Recon

## Overview

* **URL:** `https://api.airindia.com/cbiz-booking/v2/prime/search/air-calendar`
* **Method:** `POST`
* **Content-Type:** `application/json`

## Key Headers

* `Authorization`: Bearer guest session JWT token containing `clientId`, `journeyId`, `countryCode`, `currencyCode`, and `customerType`
* `originCountryCode`: Origin country code (e.g., `IN`)
* `Origin` / `Referer`: Must point to `https://www.airindia.com/`
* `Cookie`: Akamai Bot Manager cookies (`_abck`, `bm_s`, `bm_so`, `bm_sz`, `ak_bmsc`, `bm_sv`) and session state

## Request Body Shape

* `cabin`: Cabin class (e.g., `"ECONOMY"`, `"PREMIUM_ECONOMY"`, `"BUSINESS"`, `"FIRST"`)
* `itineraries[0].departureDateTime`: Departure date in `YYYY-MM-DD` format
* `itineraries[0].originLocationCode`: 3-letter IATA origin airport code (e.g., `"del"`)
* `itineraries[0].destinationLocationCode`: 3-letter IATA destination airport code (e.g., `"bom"`)
* `itineraries[0].isRequestedBound`: Boolean indicating active flight bound (`true`)
* `itineraries[0].flexibility`: Integer range of days around target date (e.g., `7` for fare calendar)
* `searchPreferences`: Search options (e.g., `{"showUnavailableEntries": true}`)
* `travelers`: Array of passenger type objects (e.g., `[{"passengerTypeCode": "ADT"}]`)
* `promotion`: Optional promotional code object (e.g., `{"code": "SKYMAPAIR"}`)

## cURL Command

```bash
curl 'https://api.airindia.com/cbiz-booking/v2/prime/search/air-calendar' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: application/json' \
  -H 'originCountryCode: IN' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzM4NCJ9.eyJjbGllbnRJZCI6IndlYi1wYiIsImpvdXJuZXlJZCI6ImE5N2M4MjQ4LTkwNjgtNDdmYS1iMmYxLTc3YTZiMDViZmU4ZCIsImNvdW50cnlDb2RlIjoiSU4iLCJjdXJyZW5jeUNvZGUiOiJJTlIiLCJjdXN0b21lclR5cGUiOiJHVUVTVCIsImlhdCI6MTc4ODY5MzgxNSwiZXhwIjoxNzg4Njk2MjE1fQ.nCTo5NDyoGYMA19Qyvpbk1B1Bo4B2BSZR6YxMYoUC33fI61rwhEjdQOI38RLpoGZ' \
  -H 'Origin: https://www.airindia.com' \
  -H 'Sec-GPC: 1' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://www.airindia.com/' \
  -H 'Cookie: ai_cc=IN; _abck=675CDFB88D19E8A16D36A274712FD797~0~YAAQKxzFF8V2kz2gAQAA0UCPdhDML0H/4JfrsrI9G0yAitz9xcvjikZy0S3rxN0zh4rsnRVxmBCnHBi7p7n82cJRf/fOVni45/v/iFDLo1zGtwLgP53q1XkWH/zOMJSXK68FrVfPUgE9vf6nQV6JC8DWW47WGzcxUhuePSj6fKRTyWDMXQdx1CupTFWWudJySAVfCfuGfH/HFR0TkoHo1+SX+/zflldYIGY7yzS0KffttbpLIPbNZpJ0qN1QRGe697OlLZkv68H/X29iS+XtM/NAj0MpFi3+FxCNal2x78DavHbjB+qiQKM2426H2s0u+12HkVcEhMMVIFKmYYR/RphRhLd4iZI8oW0Fs2A3YIovg0W9aqGJJrIlHcciKvRsbHCvBj87YjflJ274En5jf6HONjOO6T5a5hMGX3T7vrU9Q3RoMFkyYVfhkRdBGmJSpTzpFV6KaXH/CCx7xdnz1MRf3YfJdNpVwFnBNOYEV2juWsjHKU5whrcO6pJCSO/KC69aO1rvmpyjGMwWVEv5e39yymz5UqZvrkzYCd9XxD8eKTmYYqvEReaKfsISsDazATdl1Rm44WxJgT3bljZkaUu3OgAtyF0u7gopnonNWQTGvNFuiLPcK5rbNmjUNlhNU5bg7RR0kgk1HRE7hdfUABkaI6HQ37y0u2AdRlFYYX/r//+p5LqT6/V3nwqgvY4ujPExmpxD0LbucrYhgtg2PK+zMHR4e0B1RUrPH4rQQLvu2X6Bk8SJnh46zULpTFaTKBWQB7DH/0tL+KIXbdBqiW9JEFOsg3D7ct6yyvwpAvY0HWwj40VIwlFZarvy2aAlyqEZzrlicckmHi/KKBO6wy+jtDnwR3m5rH+NEfvVO9ymQoL7pq16RWnP5B+z/r7rp3U0kSRCjJcaczKmsNBcO9bvktdcz/2+x5iZbcxrVHnHOThBwR/ItXXe+IA9sXibj4eAAxtRN3Z+Hrl+XHgycruV/5Epv7ZJCbSxY63t4DalfMjFQgnUWqARCoWe7kSfeGkh~-1~-1~1788697132~AAQAAAAG%2f%2f%2f%2f%2f+YhKg81DkrtLSdHsoIkFmeNczyFMBzBiJEpYKFOMqybbtIYBlxaEq6aDMi5sO4kglNM1osxE+PIUPcH66q5QrojwMzyF5xB6jj3Zphi7BqIqammDUF9wXXlsjqEhlw2iileDjUeKvFSSe%2f3uLkRTr0K1aGbAtBpo4E7VuHvbA%3d%3d~-1; bm_s=YAAQKxzFF3p2kz2gAQAAuT+PdgZnXZk3JVm9l2TEt6odFiq/PCnp/gD/2J/7e+3pHv6+ywdfnM8Q/Z0MJY0V2gA0OOdlkNn70Tmw3VndtvDaYd3/7IYllzOwdmYm0lJnlxtfRSQ70dKA9Tpn3MqPus7kBkrUwc6n09U+TflEvYQnqrXcqzofPz3AmwXqDdK7Bya7ic0rdXxd1gdHWDk29DRx5FF8+eLutmw3DvAYki8QNPRfkTn6R3p/xn9Lzolq+yDvtDP8j0QbuhwhoketCl1xB4rt/vaEP+LZ2kg88GnDcDWFL7diFZi1OPDTcp5sDfb1TwrfeLCMO7w00C8lcqrEmD7B+dIV/Dul34BLiqfe1/CU/vHMWJShJsD7b2s0h9jcC9iK6X7Z/VDJBJxW03tGgHPWoxqFnYDV1j9Kboxi6OJ8QBR2cgEuBOWED65MoALHrcns+a1wWrxQL7GBvpmyjkreK2Qli2wmjMrkbOko2PS92H5GYm94ZcdmKRGLaHHbHmO5kcUzNzwZs5AgTxypYQW9wqENgVVOOlWjQ5K2Riey3791xtArXNQIfrJ7v7JYQG8Su/oAYbZ3+Ts9lht6MNYnFOmaUQ/FyYfN14l/RqU/Cdm1Lt7Yg4kMIMgRlM/kXvj8xiwDTzo9l/Ii7LE5da2fXJxOTvd360e0rlvrrEGr0pSORGQues5AckhojdzL+RkWxluISYHI+wUIx0piKVQDwGcVdERjt4ToV8/Mp9VLdkxRubYgUA6NHBe9yx8s7zb7Y4FbMRKZANsiiFZOQf8PR5VQ3Tq0m8QzeWhiUK4C2MlFmGvQ4IcDJhCUri+76sC0cb+/3y30p6fLc06L8xCdn3tTM5cP4y6mlfGbWvFJO0vN8nmiZvwKJHFNcxb03qsHQYTAG5+ODaRYaXjiOdPcGxvdYxrSzdtxkJ6h79W1MAIzGV8vHMKfGPqrZ79JDfeNydTlojFdLy3Kk0rQbLEHehSkJ8G9P4YmptsO9vRNEjZNKH0G7mE/CEVsbBNQLPQd0FXXCXL3lAl4zv/XALkqQXR5pS/TJrLNxmBl5UdtLSS0TezavXrXAw3N8bE5fQM=; bm_so=359265AD20B818F8D9397FC72177D7BC4B2D03D3AF87D9D4BE0AA32BCFBB9B23~YAAQKxzFF3t2kz2gAQAAuT+Pdgjrz49MYfKsfCAJOdcGN9yIhSAY9/V3KcO+tSIAVwjvysuKZ89nrYlrjXt/ipHdt1wEeb5rBsYziY5CSdg7kyikPGxVY0XCqyzRJYkgbcDngFZ8gBucLOzjHyH/DTB9Oc+lkXQg3G4WAl+MiZMThw5S4hBeHCGAWM+kOrOlLdS5gaxOL6FcFoIdfBqWwb1A1mR6usScIt4F0cjASAcrmVA2jRExu5h8nNv1c/E2EjxgV1W1USe0Q1GC5azqzzIZBMbelvwxhhriSWpxno/8pGqwfr78ad3lSUaj2SUmixHXm0txJHhOtbatrQlfV3VZJaM5T9XTbRqU+dkwR0fOb+yLodRmn6ektkXzEB2kY5ORuTj68OulNZqu6c9VVxLgGRSkZMnVGSxKcG3+Fo+DlPtm1xT/n7S6sx44y45mjkP+63irLI+tKDKlEA8qgLuuoq04; bm_sz=B89F421163B1B0DE7964B98D1E5E9A9E~YAAQKxzFF312kz2gAQAAuT+PdgGG0acP2HGL+0cXSryzr/pNUNjrbxPocnk8sZ72WYH3gtya8gb81cjPhBbwBqtG4GwmeveMPpXTLThL0xBvzEnGK6N1gn3MHz28WGD2F+qcTwJMy72f/RXFg/tx8qJuhjp+7NsjLS86IrLJmxf3/36D97X/o/B7WCHJihJswc+0hpfIRXkIVk78pgpJJfHrSdSoeOyrZUlNkmKh/zpH1crgFDwBxi5xVe68EoYEd0LDhlfUINlXwdp9YyQfMTiWW9sY7DEMo/n8SjJJFiJ3/Hj41xL1Z1QAdb+6BQVBPubvIy6XfcprCkr/8SyARjkyt+CmNfjAdpxDHPcg098M76rYuQwf5vzjIam+wa1peyuN99uUNA0CtDla2K7gDM2WHc8dAunQz2Eu6fWlvGkyZwZGIpakkkXMPINTrRpkgX4rb9RT0K+bSE5UcrEkmzXJm8tbwyf2DlqP~4408375~3158577; ak_bmsc=465132B4F2EA22D65BD1E06980707EE8~000000000000000000000000000000~YAAQNRzFF0Z4s0igAQAABtU4dgFI6eSJ7bjC95J6Vf4fXwYCdFLuPWBTehkaAPeDS+ZvoUQ+/EJM+WDp1Lu2MQLXXiIgsdsblKwIb8lHPVZEF5UMGHbI1MxC3nXkVIvdOhrCDMh5s9bATgfr20rUD1/p3BxVy+IgkWp5xOUzYnZqIJlNqG2o83i7K3PQ0bSKEu3AQORYgHxoDAuIWoHcP9TmDnc/7YJFtUBP7DlA8bhAn5u+dlT95echFswiitkXS9NHNJVjTdmWnTbgd2osfXGKjmByUcy9grhgydhmHza0BupATiJ4IPVH4jez05L/B5lTh2EFnZW+BKPiozCfCnSHUnEC4riI2/2wrE2uRTIA8gB8QDbUlWZGNDaCRSwXMkDQclvcrD4uumRgOhifMi6X7TF9Drq2yztzgedW4l5XxKWCVJ0Uu6rbLWgHiTOM8jjFmZB2sKg=; bm_sv=49D8FC27F77AFA003974C00F80881CD0~YAAQKxzFF3N3kz2gAQAA7EWPdgHX6mnK/fXdNL4CUrNhfyDmOWFt/f333TrBUIFoex5gfm+i6e34s8ZGZIo18csGjYcT3iv6+/FzSHJVFVpI1z7XsdnXgMkXfeOP/paFmoPkyrATG6aGu5NbiGn6Z18wmwi8ZTzYZePK6bxeHKe7U3kY9Uelzr77TzJnU3MZmLErpN66s1Xrn2c5FVTNU/ev9q263uWEKkibThJzjSQHoEeCng6Ow2Yp9E3pH4inFCrH~1; _gcl_au=1.1.1896276591.1788689834.-.-.1788689953.383232828.1788689954.1788693820; _gcl_gs=2.1.k1$i1788690441$u65732542; _ga_KY2H50PYYH=GS2.1.s1788693796$o2$g1$t1788695494$j60$l0$h0; _ga=GA1.2.1066803119.1788689836; _fbp=fb.1.1788689842285.450551486475048326; OptanonConsent=isGpcEnabled=1&datestamp=Sun+Sep+06+2026+16%3A53%3A38+GMT%2B0530+(India+Standard+Time)&version=202605.1.0&browserGpcFlag=1&isDntEnabled=0&isIABGlobal=false&consentId=e5058051-1aa7-4560-a6c9-911b522ebeb3&interactionCount=2&isAnonUser=1&prevHadToken=0&intType=1&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1&crTime=1788689857714&fclco=&lastConsentTs=1788689856&geolocation=IN%3BMP&AwaitingReconsent=false; OptanonAlertBoxClosed=2026-09-06T10:17:36.719Z; _ga_8Y7N6KMX5B=GS2.1.s1788693796$o2$g1$t1788695494$j60$l0$h0; _twpid=tw.1788689858213.705495922595785779; gid=GA1.2.826483898.1788689858; trackingCodeSetValue=spectrum_37k8%3Aaffiliate%3Aairindia_direct_promo%3Aundefined%3Aundefined; previousPageNameCookie=Departure Flight Selection; kndctr_56C628E563E65FE60A495FBA_AdobeOrg_identity=CiY3Mzc2MjgwOTA2NDgwOTYxNzA5MDkyMDk5OTg4MDAwNTI2MDM3MFITCIqj5bGHNBABGAEqBElORDEwAPABiqPlsYc0; _hjSessionUser_3738565=eyJpZCI6ImEzOWE3YzdmLWQ5MGItNTUxMC1iNjQ3LWY5MzlmNzAwM2JmZCIsImNyZWF0ZWQiOjE3ODg2ODk5NTI4ODIsImV4aXN0aW5nIjp0cnVlfQ==; _uetsid=303eed60a9dc11f1815c65e7482b0190; _uetvid=303ee130a9dc11f1b7fd5f7b9e0a3528; _hjSession_3738565=eyJpZCI6IjA5YWU5ZDJiLTA4ZjAtNDQ2YS1iOWY1LTlhMTEyOWY4MzYyNiIsImMiOjE3ODg2OTM4MjAzOTgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; kndctr_56C628E563E65FE60A495FBA_AdobeOrg_cluster=ind1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'TE: trailers' \
  --data-raw '{"cabin":"ECONOMY","itineraries":[{"departureDateTime":"2026-09-07","originLocationCode":"del","destinationLocationCode":"bom","isRequestedBound":true,"flexibility":7},{"departureDateTime":"2026-09-07","originLocationCode":"bom","destinationLocationCode":"del","isRequestedBound":false}],"searchPreferences":{"showUnavailableEntries":true},"travelers":[{"passengerTypeCode":"ADT"}],"promotion":{"code":"SKYMAPAIR"}}'
```
