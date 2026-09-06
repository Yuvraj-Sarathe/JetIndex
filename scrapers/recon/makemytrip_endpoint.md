# MakeMyTrip Search Endpoint Recon

## Overview

* **URL:** `https://flights-cb.makemytrip.com/api/postSearch?crId=f22d4102-dbca-4611-9f79-08fbfe782a56&region=in&currency=INR&language=eng&cmpId=`
* **Method:** `POST`
* **Content-Type:** `application/json`

## Key Headers

* `x-flt`: Base64 encoded payload with search metadata (cabin class, pax counts, itinerary dates, etc.)
* `origin` / `Referer`: Must point to `https://www.makemytrip.com/`
* `device-id` / `mcid`: Unique client UUID
* `pfm`: Platform indicator (e.g. `DESKTOP`)
* `Cookie`: Akamai bot management cookies (`_abck`, `bm_s`, `bm_sz`, `ak_bmsc`, `bm_so`) and session cookies

## Request Body Shape

* `pax`: Passenger count identifier (e.g. `"A-1_C-0_I-0"`)
* `cc`: Cabin class (e.g. `"E"` for Economy)
* `it`: Route and departure date (e.g. `"DEL-BOM-20260906"`)
* `cur`: Currency code (e.g. `"INR"`)
* `rkeys`: Array of flight listing result keys returned from initial search batch
* `sortBy`: Sorting criterion (e.g. `"rhino"`)
* `forwardFlowRequired`: Boolean flag

## cURL Command

```bash
curl 'https://flights-cb.makemytrip.com/api/postSearch?crId=f22d4102-dbca-4611-9f79-08fbfe782a56&region=in&currency=INR&language=eng&cmpId=' \
--compressed \
-X POST \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0' \
-H 'Accept: application/json' \
-H 'Accept-Language: en-US,en;q=0.9' \
-H 'Accept-Encoding: gzip, deflate, br, zstd' \
-H 'Content-Type: application/json' \
-H 'Referer: https://www.makemytrip.com/' \
-H 'x-flt: eyJjIjoiRSIsInAiOiJBLTFfQy0wX0ktMCIsInQiOiIiLCJzIjoiREVMLUJPTS0yMDI2MDkwNiIsIkl0aW5lcmFyeUlkIjoiREVMLUJPTS0wNi8wOS8yMDI2IiwiVHJpcFR5cGUiOiJPIiwiUGF4VHlwZSI6IkEtMV9DLTBfSS0wIiwiSW50bCI6ZmFsc2UsIkNhYmluQ2xhc3MiOiJFIiwiQ2NkZSI6ImluIiwiUGZ0IjoiIiwiUGFmcyI6IiIsIkZvcndhcmRGbG93UmVxdWlyZWQiOnRydWUsIkNtcElkIjoiIn0=' \
-H 'os: Mac OS' \
-H 'domain: in' \
-H 'mcid: 1235f672-2765-4b4c-a2d6-54bd287d6a3b' \
-H 'src: mmt' \
-H 'device-id: 1235f672-2765-4b4c-a2d6-54bd287d6a3b' \
-H 'profile-type: PERSONAL' \
-H 'Cache-Control: no-cache' \
-H 'app-ver: 1.0.0' \
-H 'pfm: DESKTOP' \
-H 'Access-Control-Allow-Credentials: true' \
-H 'region: in' \
-H 'currency: INR' \
-H 'language: eng' \
-H 'entity-name: india' \
-H 'user-country: IN' \
-H 'User-Currency: INR' \
-H 'x-user-ip: 104.28.215.179' \
-H 'x-user-cc: IN' \
-H 'x-user-rc: INDORE' \
-H 'Origin: https://www.makemytrip.com' \
-H 'Sec-GPC: 1' \
-H 'Sec-Fetch-Dest: empty' \
-H 'Sec-Fetch-Mode: cors' \
-H 'Sec-Fetch-Site: same-site' \
-H 'cmp-id: ' \
-H 'mmt-auth: ' \
-H 'flow: ' \
-H 'auuid: ' \
-H 'Connection: keep-alive' \
-H 'Cookie: name=value; lang=eng; ccde=IN; isWW=0; userCurrency=INR; dvid=1235f672-2765-4b4c-a2d6-54bd287d6a3b; _abck=27B2DB7967E40B23714CAC5293BE7DFA~-1~YAAQvlQ/F/XguFSgAQAAtGrhdRDh5WXfSMzO068vpdXbyNJUYVeF1BkGE0/sbAMwRXGjAnz1njEnbtwmJ6YXVEejWtBXbZQKJVhQIOD74cXRW6cSfsyn9kaaOOH4On2ZjhiRzQqn74/LUPbv9qpVoJVrZS5fbDxaBukzoT6QMMkZgVqEVBjqCGJEkOhqFh3MU7s/DIhGzxKLQYrnA9A8t8RnSsMbS7dTq1HcnqOo7r7C+3ybMlxXrnGWvKANlkn9f2DHzscC1Z8bnS7j/PCSaKRswBMzN5J3yEdVWCyC96Snjhdx8/t5uoIEC/JgSS1NZyv4T3et/RCt3QJdDosU4UPnf+jkZfIVO3PZLCzmHsrGiZwtrdH+PawSzLKLbK8ou1j2R5B4tWKWVO/p2bkaorqWU7TclQs98qd/ak84hLrJ2m42MRJefAUy83zHoOS7Wlfebx4d2T+uxiX+sNuiM820kNQ8ipgAJAZHsRbZPhuteBK0OQEFHNIDhQSSV/0h8NF/mOnN63O0StvEdtLtArr3gwYWOQWWxZrRMve5A5MLPabe12b5zNB/SpFaX5VgkbuykHmnZFoOxKpIFh3sI09i/3JZpZ1vEMKz966+JGyrRrkk7KvohVASg1SwFsLnklzZ5rFLPbO9Oc241zT7zprLx1Qe3iaJhfXVbnGxXJ2kuDRtW/B6LcuXPfZlMV6hv0xipc3C27grTVcQlWXt1bfwWKvqatKOLekCZc+Q/G0w5Z1Y0jUEEOU9G9/sWNY1bC0zS42nd8SI6cwWN8tg4dQ+EPVjGGdcPtHwoTicC2Kj+wnqBpfOqGYeimG7pwFiUhhATMAgfN7n06vt7JYEgSzuoO55RQmbVZT4YACl4lx1~0~-1~-1~AAQAAAAG%2f%2f%2f%2f%2fz+Q5h7u+werd%2frveJDJCXdwzvMWKId8LwGToRX3g0BZBMzccdKI+Cgr1M9ppQIfgEoahjQ7tgP+EgMZXRPX4cYlF8L0HT9Fs5Zh~-1; bm_s=YAAQvlQ/F/bguFSgAQAAtGrhdQbOzGyxsrVo/Jk7iO0xOvDv6Dz0du+3KldAxSJ3qyRXSdT27qYo4/vLYn59MJ1bRzXzuWd6A7vomuKD1h119ZQ9aTXA+RfBQxwFw1GPrdb8vt8OZ5t18Fq7ji8Ptw+L6Hkrd4k9Gv0PH089zdgmqifNZo6vlVKypQQdqBg39/GNbbhw8yHxQbB+2FWSpJP85+bOHDx7S/CtfTPDYtP0GFCoxpQSFaQ9qVhJHfIaAY/LCYQOavzGHXICc9rWHKg9jFsM4RPlpg87pGrRQWbFirvlQuuDPPtakvVmGgEK38kkJ1GsOfW0Jx9CPS5RKBtzBrGKi/VBT/dHxWkvjbiaVcaXAKGSDeFmQykXdtzst1YagkKUOq4Zry89w62KsKGmtxVqv66tKhqrcnBwq5+OLa6KVXj5SGKmFDg6/FBfzsPVQDkLDDmZjQCW+f1Rg29nPA1DGvPepxe371vlCCcm6+84pnw5n0dRU3G96HcVTtnx1/26Sq1QsnsLU2O7OeL+NDDUFMOW/a+zk+wb/+kBk5xq0di9ypR5ZjDrXrfrTzS6q2FR+acMppLhtGwub/Rggdbq8uOsDU4URG00S2shBoY3lZNLiYwvMQYw9JTYzoUUN2WT6K2XOInOr7fGbYfGA/H5OmuOMYJoKeie0Lh0uVesMFbMGwTNWzvGAzToh4iKf2o8EHV62P0hOEvMJ9M/tdHEpkHsv1eK5fO4bNJdhjeDP7mJ/TjjA1mDQ66Yf/bnOS9l4g/Vf2BhwvHok1qJxPf+EDyYY+ofGDkKoN70+Mqs763jGr2RKyXcdZWCexZCQjYfePQXbR9Mi4aBPOP3B8N3yWnHAH01Ed+3JvAcur9+tSKYUidvbead9DodFljXf8AJPDX3+jb3JxEpCIIxRVdDs6Kq1Mj6aAgGLvw6Xr++yp7yNAAuexRJFPSkR+AS7aPZwuOEcmp2XyEHfXYoNZoN5KdR6vnUILX1E2UfK6bE/AeFoNJDpVC095Hko9OMEHA33EyE2TEGrLYR6ec5BkzYWh71PCBXgSYR3vfA/Th7h+fzqTTobqWhf1w+/O6cBSJVkUrZVvXd; AMCV_1E0D22CE527845790A490D4D%40AdobeOrg=-1712354808%7CMCIDTS%7C20702%7CMCMID%7C54770683406189872244096977519271600491%7CMCAAMLH-1789288877%7C12%7CMCAAMB-1789288877%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1788691277s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.3.0; s_ecid=MCMID%7C54770683406189872244096977519271600491; s_pers=%20s_vnum%3D1790793000078%2526vn%253D3%7C1790793000078%3B%20s_depth%3D3%7C1788685901558%3B%20s_lv%3D1788684103256%7C1883292103256%3B%20s_lv_s%3DLess%2520than%25207%2520days%7C1788685903256%3B%20gpv_pn%3Dfunnel%253Adomestic%2520flights%253Alisting%7C1788685903256%3B%20s_invisit%3Dtrue%7C1788685903257%3B%20s_nr3650%3D1788684103257-Repeat%7C2104044103257%3B%20s_nr30%3D1788684103257-Repeat%7C1791276103257%3B%20s_nr120%3D1788684103257-Repeat%7C1799052103257%3B%20s_nr7%3D1788684103257-Repeat%7C1789288903257%3B; kndctr_1E0D22CE527845790A490D4D_AdobeOrg_identity=CiY1NDc3MDY4MzQwNjE4OTg3MjI0NDA5Njk3NzUxOTI3MTYwMDQ5MVIRCIGx%5FoGHNBgBKgRJTkQxMAPwAbqUhK%2DHNA%3D%3D; GL=true; _gcl_au=1.1.628113288.1788589643; isGdprRegion=0; referrer=%7B%22referer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%7D; AMCVS_1E0D22CE527845790A490D4D%40AdobeOrg=1; s_sess=%20s_sq%3D%3B%20s_cc%3Dtrue%3B%20tp%3D376%3B%20s_ppv%3Dfunnel%25253Adomestic%252520flights%25253Alisting%252C88%252C88%252C332%3B; bm_sz=FE5F412A28C14561073FA245BD412B3D~YAAQvlQ/F/fguFSgAQAAtGrhdQGvn2/vZap7mgmBbR+rA+RJzwQSM/+BK+8kPJX8h6W5RmOfAz1CR9nWtv59k/JW64R9ei980x30vMYnTB53A9YaPTagpqLADG43cNtkHt20h73ddPZ/WMxyAuL9SVUS/SOYSzw31qJtQMQblkONNIdwAFCkFWTwZ2GtPCEq1VwOUW12ZpztLc3M/NGSOllB39QtwAu2XgPxUcc96sXJbTnlrJA+iYjv+5rKO3D8VY8MzjMJX0YAfrdxUTsL4TEesnDYbdGNf8bN23PMc5D/ka92dejnIWhkSHJJgYbcJmmeGy5UJPC+zp7dyFuwIFUKkpVCFFuelhb/Vi++Pi1xWOvZDo4G6BjVQlmSu1860CXAePHLpxpoPkGgNie8x+LgjLj1a9j7IqBSRfV+kLrhTAb/~4470853~4403251; kndctr_1E0D22CE527845790A490D4D_AdobeOrg_cluster=ind1; ak_bmsc=DE022A2558BF5BE81B03E036196FF0AF~000000000000000000000000000000~YAAQvlQ/Fw/AuFSgAQAA8wrhdQE14+CFQfmm1qBTALNUnrDw44Xmo7OKvSlKX5yCqD7HgY4uPzM9kgDXLA4LgOmku1SsTTlJ5jRuhpFu7XNnb83/IUsptVpUsu4nS7YohfzIxiUlsb4hqgwrXGp+5dJqyknVV25CWGwiL+cwo1jhdO6eEfnCfWaJwPPJ+/u/wVll1Z72W62sz81kSVZ/Woxmb+71hqRCyt8VCt6uT21xJhVHQ/w4OBRuWETAUm1XzYn5ZAPojUEKTOwF6BRKUkPPRNHaBN1OQCsETi7iu72Gls3LGfl+RPQQJmtxw7AYDl7fBWoef7oE6y9l2ldbfB0G2K2TUW1cmH8Wh9U/83NwBf1B0HhdS2pJpjQNjEBu7Ts0hw1Wj6am2GKyc/+Ol64=; bm_so=D128D49BDD57F98A0FFDF6EDE9C09AE6FB603C971ACE774813A338CC0E7C79AD~YAAQvlQ/F6zPuFSgAQAA7DbhdQiTyB/GrI4pwmbKzBzUIq4ytBnCF80v4nJjDWQfRRH3Jts77WHpYSSq0L/SjgNv3dNhzbB7Pgvhoyn1g6TYWgDSunrBM+CAgwv6YzdBp/B7AnWr3Moki7cwAPgePlAi4vz4HbcKo974iDCd5NTKpDo9B4Ur0uGAa4/xTx2E3l/IOrdXsOaRO+Zu27+oI49tukC8N/6Cb9+vhwpdj/oGaaNnTLcMZotYfeQkI3FsJtTLlsf7yDw92TEP4s6+obyowE322EzwGgJ7/LklunHCZal1SmMOFAWk1E5uVK2WOWzWqhft2klvJ/sNxcPEy4W0KSI1K1XEaHiTkbwv0mYjn9xvVEOJEQIA7VD89aoFVIqbZvEwku+uUEwz2Fk2EaNFWtEPZMoxl/8dUJ1S/xBt2Jvxc+i5RNTQLpDpuVY4f5haiUKnCgkaDEp7php6by1M64OGTHw=' \
--data-raw '{"pax":"A-1_C-0_I-0","cc":"E","src":"","crId":"f22d4102-dbca-4611-9f79-08fbfe782a56","pfm":"DESKTOP","cur":"INR","shd":true,"isGrpBkg":false,"dfs":0,"it":"DEL-BOM-20260906","sortBy":"rhino","apiCallTimestamp":1788684103265,"creditShellInfo":"","forwardFlowRequired":true,"rkeys":["RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:22_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:9_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:27_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:15_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:26_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:3_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:47_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:16_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:1_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:34_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:6_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:7_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:39_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:42_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:35_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:33_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:8_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:32_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:13_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:37_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:25_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:0_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:2_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:44_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:23_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:49_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:31_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:46_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:19_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:18_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:43_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:30_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:41_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:10_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:45_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:28_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:29_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:4_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:38_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:17_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:24_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:5_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:36_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:12_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:20_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:14_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:40_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:21_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:11_0","RKEY:dfdc38e6-778c-4599-a407-fb377ab7904b:48_0"],"pageType":"LISTING","lcl":"en","isEmiEnabled":false}'
```