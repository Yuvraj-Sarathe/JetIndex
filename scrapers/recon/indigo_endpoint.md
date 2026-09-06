
# Indigo Flight Search Endpoint Recon

## Overview
* **URL:** `https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search`
* **Method:** `POST`
* **Content-Type:** `application/json`

## Key Headers
* `authorization`: Required user session bearer token
* `user_key`: Static API client key (`31e90be8fff2f5e2eea242c225f21b1a`)
* `origin` / `referer`: Must point to `https://www.goindigo.in/`

## Request Body Shape
* `criteria[0].dates.beginDate`: Flight date format (`YYYY-MM-DD`)
* `criteria[0].stations.originStationCodes`: Array of origin airport codes (e.g., `["DEL"]`)
* `criteria[0].stations.destinationStationCodes`: Array of destination airport codes (e.g., `["BOM"]`)
* `passengers.types[0].count`: Number of adult passengers

## cURL Command
```bash
curl --url ^"https://api-prod-flight-skyplus6e.goindigo.in/v2/flight/search^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: en-US,en;q=0.9^" ^
  -H ^"authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpYmUiLCJqdGkiOiI1YWMwN2FkMC0wYTg3LThmNzctMTkyNS1kYzEzODViMWQ5ODciLCJpc3MiOiJkb3RSRVogQVBJIn0.gmU2BVLxLQCPzqpbYbRzRZ2cRHYkwGRBB6EvI2sbw88^" ^
  -H ^"cache-control: no-cache^" ^
  -H ^"content-type: application/json^" ^
  -b ^"AKA_A2=A; akaalb_sanjeevni_prod=~op=sanjeevni_prod:clu2-ci^|~rv=26~m=clu2-ci:0^|~os=936795b546b11f87e62780f83093a871~id=acfdbdc21504b186e6a72067e5a4ccfa; projectname=ux-revamp; bm_mi=967A76B5293920C96785A86332539638~YAAQntfXF4+ENB2gAQAA8kySdQEmYpwfOJGDVo2FBrU5HDhO6h3HK/RJ5siJcI/vBfhJONSWOoHoxB2Hi/noc+Yani+w9/ftJjMTrk7SMSb52rfd4MbGfecxK0dkSG1lj8uazu5Jk3uqZrZunrO4Vp6p0Gnf1u/gfOPuuGeyyGf9/2w5Rsd1ntWBLtvXlY+OLhb4jzAYqYeqU8m4U8bhogKLGQr5XAZVLcTwbiLQYPxNXsYCndtZ1t7dmHMYM3VHgHYqzHAlWJ4pbiNBQeo6qwopPtCw0M07zsWO0eQU0M7AXlgQMGrEcStmsP0xz3A=~1; bm_sv=D5BAF498D12450FC7102CE86ECB8F64D~YAAQntfXF9CENB2gAQAAqluSdQGWAE1XBVPiSCvmG3Pr+x86/S/tU37VYfeNABT1Owo9ywVWeocd4C3d1cSO14A8LtBBXMWMkDoMS90eHt6j8y4ZRH/K5c2WAYJFwYln3MkuzkZfxXOEKDKuv9KWqo7tED9bbpolTcuGviBkDYi4qIvJp+X3VoBsL5cDhOxKex0JxXRZbK9WvuM96RyLfPk2mvPqbGh6KghaatKsfLHfhnCaHndP/lbdoRan+EqnwuM=~1; ak_bmsc=9CE851F8E8ECD20EA03F1D3D5041B410~000000000000000000000000000000~YAAQntfXFzqINB2gAQAARBuTdQGQMB5/s+ClCbf9JJ2LHbQixeowSg+WNWTpXZkfW3mkx+MGbIdqYOTZ/cY9FLPuqP7DmufBvmME5bPN0YSlNMxLnSeUsrO3PoG3udXFgEPmLW+Guv+7KvRoQEGZAQlVHGXtQSvxYJgn34X51P16MKkZJaNCTJ2AJ+Yv3/HjxNYRuKss6mT6JJm15T350QX6dU1v3npl6J0Y31hkSL+K1o9FW9E/Q+wZop0KU+Q6aTaCGqv7fr7EmeCVxtDWNgYkG08mq+xfCIqVOq0SwhHseO59XBcEOdNMvQFKFU8bmB1uBmH+sElsqO5EwzIeG4B1Lpy3J5G2HOy1o6hXEs1jCcnEGLpkhgA80IOqspIm6v5la9kI17yWxkfwqeO8sYrH6PrHsUWd6O70dXSirbi0SyGzsuQEWq7JbLYSVivXnaRqCcYV8EUeDUBR; 1814f089dcd852897212cb1be0c682f4=64c9a529d621b2670172f90bfd3853a2; 13a6c316f30a0b3fad1f7d781eb19c19=d1c3450ba150464b825cdd7bb9722e80; auth_cookie=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpYmUiLCJqdGkiOiI1YWMwN2FkMC0wYTg3LThmNzctMTkyNS1kYzEzODViMWQ5ODciLCJpc3MiOiJkb3RSRVogQVBJIn0.gmU2BVLxLQCPzqpbYbRzRZ2cRHYkwGRBB6EvI2sbw88; role_details=^{^\^"roleName^\^":^\^"Anonymous^\^",^\^"roleCode^\^":^\^"WWWA^\^"^}; personasType=Anonymous; auth_token=^{^\^"token^\^":^\^"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpYmUiLCJqdGkiOiI1YWMwN2FkMC0wYTg3LThmNzctMTkyNS1kYzEzODViMWQ5ODciLCJpc3MiOiJkb3RSRVogQVBJIn0.gmU2BVLxLQCPzqpbYbRzRZ2cRHYkwGRBB6EvI2sbw88^\^",^\^"createdAtMilliSeconds^\^":1788681562953,^\^"expiresInMilliSeconds^\^":900000,^\^"validTillMilliSeconds^\^":1788682462953^}; s_nr60=1788681607820-New; s_nr90=1788681607821-New; s_nr120=1788681607822-New; s_nr30=1788681607824-New; s_nr180=1788681607825-New; bm_s=YAAQTvQwFztG2DOgAQAAO2O7dQZChVW2gx9Ysthrj9unzoHElX8dSTJQ5N2TfmmJFHVfVy7WtbTbLkJFceJjLE9fteW711VkEcUrFpi64fAXaqnQjRqtieAqVmAwBQC+0P9R2BHRgL4VmUuMcx0F5gkAOyldOsd1THBSnzYh74n1fa1eBn6sKDSjcW6i7Tspt6EbSuIJoGGfpSoLmSLm2Wal6A0xUpPB9DhZ+/BADSyy+8+jN1PrqOmhYPPdNxgmtov0exbt7rG5QaXQlptuiCRORSAyBkMCJkb7iJmoj3o+gIvsq/bWnxoq414jujpDKbkQOym++/lmaVmKbFMITIt7Jh2xScteLB8zcEYxqDYiE9/v/zID7qR4gvQghYGb61WG79NynCJTJfmk1VCj5nEhXq+OH87VFtFSu8LzVGgRSxX8L3FY91KhjJ6RCCSjMyCNCC1BeaHJOZnrcjCHC6UdDKunVXr03F01ZkNVY//nvg5Xf6FrXLzRCPJzQQ6jCAo3zvha6p4c80FhermC435HPlfI1iViwbdX281VZWSOLBq6TyzVmoq4RE3tD/wNET02MAjGDTG5s4/T2BeHOkYD6ifXFi9KqxKtlP9vucCLwfqmB0zWwBSJnC5vGuO5rHiroTZHnHuMJx32VDwXiTTWC6ZUqgQdn4/74RFbPgB8ZAT/Stp/9olN28/6mICpm+QgwQ7g3Tlc+Hm8M7zF2OaoMKFWBrI7RG8e1+lXsgotkY1jjSuzgewL/PL8lCak5ZiGmHcBEkbgh9QOI15Oa45bto0TiNoxf/MtzU4h7hVz2uhZDwPwTAgXlRRRUsHQwNAxMNb7oZUtmxF/NjEjA9NCyp39CvW/GUWQoZ4LCpiM9cN4WT4zAIRMm3MNSbaoljtN/6k7TCLJkMFIVSvS5SgqW7zcW8IC0VCESf40bJ27BLiiuWDXviV4+NUFGiSxFg+WxCTXuWpvZLdCiPo+TkaP4MFKL3xSXI+5Z02AGJycXV8rFyztktns/ZKnLZsu5eY7iHJ8NI0ciBWX///Fsfh1aLNg5J+op26KjSA0i0xmD/GQXfJKPe+p/grWgCOXkR2WGkO0hfNJ2AhxUTw4JZv8kfA7FoHLbd1nXHDTFS0mM6wwpDEv38AK4D01qTQo2tUdQYp2P3sghAh/Kt62fN63w0eewbXvWSXmH2mP9HDZuuMCtAb0T74=; bm_so=B6C5B7BC5DDC343E58C97A25DC0B3BD3753545E8967497023EE15DF4D5BDBEFF~YAAQTvQwFzxG2DOgAQAAO2O7dQhi0WlG97m9nsXeVQwPNrTeqb3cQxF5+Lv4E2njReUtYrw/lHNhZ5MK19ZLmt0v+UJO6s+ia+8FzpgRRQbVceWgr+VwGn1Uh/BwxC5ukARvwagxz2RRljOhW9kEKN1UGJomvBMOifELIt2mo5suETO7ZLax7GswDj9XoEjR+TTAd9N/a8N5NM29C84Gt9BWX3nsQCe+7g9m4kC3bHuNNCw0oW3IjW1AtBdSYi6PTsF2vgODSR+W1z8AhGmvc8SKqZh1sgpqev++sS5HsD7J7AhwjcpEoIyDzCXp0UsZARxLj/3sG/utfrX2aVxx/cK6nK1IzCmlBVYllyuqY4qWvw8MFJ17G1BKxFeSPFdKL73hMnUNaFn11CkBgjUtg29oO3mi8MPikKoPCCWRy0G7a53ZHEXVBHZmRUt0UM12wfn1dh5DaKV8EpU62yZUm8UpNw==; bm_sz=AC37B2794AE86EEDF5EF7C0D2FFCF69E~YAAQTvQwFz1G2DOgAQAAO2O7dQGLXRmFGl7Co1cdjYsENJxSKZccsCeFR7FYdycvcUaoaNt+S4RqWHELUUTQFwOGEhEZLUYG8Xd65tJcISWZDRoLH4brbSwyndHqRm63smJD1jb9h73YF7aV4cx+NyMqUo3BUj2/6WFvPlUXI6hfEA/Elv4ajSDV6gu6f9aUc4Ktqd3tTKLtWFmrgXbrfutME9sVFK9Qgh0tQ0Zct0vvesnu2YaHkjEbee8ommdYB55pSjyl0tpjp2BITwI2vS8VxMXUjtl/IY3Z1fhLcTUJqHGcsdg3h0bjBkAxteQj1vCTBbyZgGH/GUk/PRrR15wj8vZpsmjTU5bGQifBdv2XxI8jSkMYbjw4vIRfSipT/ItAd1soW/Zo1mQ75cS3z16boSgIqfAjCrsUCWxXNv6pE7NUdN5XJc03wlK1KUl5c4fN8ArtdR6UioO8DQInxDKZehUZDD1jiFGCCPV5rOlNCzg/8IA5tPHcyDWsFDhh/7z0UuE=~3490625~4599862; _abck=E3BB73C9A711DA194E50CE48FED5BA4F~-1~YAAQTvQwF5hG2DOgAQAAU3W7dRBDHL7mciTC2dhUDPiCX4MD/HRs7TZE688nizaR5Xx8BU5xKyjD6cxP/zOcTNiZYQOvDzBaNfmWUSLE+QwiCM1R9eJ3VtwQWGcHnQVLIDs3gCCvggWwxWMNa1EO0XQmaiulHuQk7uPRTIrrMb6nPvISDt0+pD8/2Us3T4/P/URv7kkHiMAN00B8vPWlg7IfNzVumVOb3P68UXHdg7oJtQef32j88/aMHWwA1WLiEHo4BtegVyEb60quzuSyXgdVCxDOAUFaIj0N8uRlumC5XykRVw8vG5tIU6EWZJxH+FQVeIL9gXzmVuRIjphU+VzfkN1pJh0utNRxe+d3tfEuwTYse8sEJs8rRLaFJQ/9a5IIcaQHFAeYEDGqDbdqyL1++F0x1+UvDfwmXH38z76N+/XUOhQrZHoopvCuRcCkkN3eNbkCxkbKOFDUDaHK18q2CWagALrloHBwMCHHj3E2StSGJufUj7eBh/aJ9WYL6TZbrXlPK8Ni8yov7Q0qliR7bSkLw0ct+Fmw1EmWNJu+YRSE6Z9DfWeBm/lR+UnCvOKWNR4vvCbiCHxEZXOcaEv+LsKNsHq+OlwwmtsofxJVgQfeg+GcCB0hEednJ5xfBe7BEexTulZnMLs2SwJ7AfcK/J+dk2ZV5IGxj2tlSGb6cboyPgm7ifu9Joc0tYK28Bx4uDzgb7GBLmmTJakmFHtZL79dGgFfcpsvPj5btOQnw4vXoiesxJ1uPHLc3m89XCVzDD5Y/+nB5NpBS5BDQWyQO8t89/S9B+Vw8mGXaj0KWEv5~-1~-1~1788682297~AAQAAAAG^%^2f^%^2f^%^2f^%^2f^%^2f^%^2fenSuKIYXwHuJdJfk^%^2f0W5JfEg0749MeYu^%^2f^%^2fvQX4r2GfabnDkPGC73nf9dfBUza5VNr1DUhzDUg0REjAJlxnhL96lQVaTzgu8R^%^2fJabkf3uCSYi0OHW^%^2fqNHTsxIfuJt4SzMobxcNg1ZH41DxkjNgUyXd4ksAgiS0bXzTrppCO6KF1g^%^2fIWep86NyfHt0d5yYw7bwTxtfDVaDHB~1788681674^" ^
  -H ^"origin: https://www.goindigo.in^" ^
  -H ^"pragma: no-cache^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://www.goindigo.in/^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"152^\^", ^\^"Not?A_Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"152^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36^" ^
  -H ^"user_key: 31e90be8fff2f5e2eea242c225f21b1a^" ^
  --data-raw ^"^{^\^"codes^\^":^{^\^"currency^\^":^\^"INR^\^",^\^"promotionCode^\^":^\^"^\^"^},^\^"criteria^\^":^[^{^\^"dates^\^":^{^\^"beginDate^\^":^\^"2026-10-13^\^"^},^\^"flightFilters^\^":^{^\^"type^\^":^\^"All^\^"^},^\^"stations^\^":^{^\^"originStationCodes^\^":^[^\^"DEL^\^"^],^\^"destinationStationCodes^\^":^[^\^"BOM^\^"^]^}^}^],^\^"passengers^\^":^{^\^"residentCountry^\^":^\^"IN^\^",^\^"types^\^":^[^{^\^"count^\^":1,^\^"discountCode^\^":^\^"^\^",^\^"type^\^":^\^"ADT^\^"^}^]^},^\^"taxesAndFees^\^":^\^"TaxesAndFees^\^",^\^"tripCriteria^\^":^\^"oneWay^\^",^\^"isRedeemTransaction^\^":false^}^"
```

