"""TLS fingerprint profiles and User-Agent rotation for curl_cffi."""

import random

# curl_cffi impersonate profiles — these mimic real browser TLS fingerprints
IMPERSONATE_PROFILES = [
    "chrome120",
    "chrome124",
    "safari17_0",
    "edge101",
]

# Matching User-Agent strings for header rotation — literal UA strings, can't break
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",  # noqa: E501
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",  # noqa: E501
]

# TLS Client Hint + modern browser header profile for each impersonate slot
_HINT_PROFILES = [
    {"sec_ch_ua": '"Chromium";v="126", "Google Chrome";v="126", "Not/A)Brand";v="8"', "platform": '"Windows"'},
    {"sec_ch_ua": '"Chromium";v="125", "Google Chrome";v="125", "Not/A)Brand";v="8"', "platform": '"macOS"'},
    {"sec_ch_ua": '"Firefox";v="127"', "platform": '"Windows"'},
    {"sec_ch_ua": '"Firefox";v="127"', "platform": '"macOS"'},
    {"sec_ch_ua": '"Safari";v="17.5", "Not/A)Brand";v="8"', "platform": '"macOS"'},
    {"sec_ch_ua": '"Chromium";v="126", "Google Chrome";v="126", "Not/A)Brand";v="8"', "platform": '"Linux"'},
    {"sec_ch_ua": '"Chromium";v="126", "Microsoft Edge";v="126", "Not/A)Brand";v="8"', "platform": '"Windows"'},
]

# Standard headers that real browsers send
STANDARD_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def get_random_profile() -> dict:
    """Return a random impersonate profile + matching headers with TLS client hints."""
    idx = random.randrange(len(IMPERSONATE_PROFILES))
    profile = IMPERSONATE_PROFILES[idx]
    ua = USER_AGENTS[idx % len(USER_AGENTS)]
    hints = _HINT_PROFILES[idx % len(_HINT_PROFILES)]

    headers = {
        **STANDARD_HEADERS,
        "User-Agent": ua,
        "Sec-Ch-Ua": hints["sec_ch_ua"],
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": hints["platform"],
    }
    return {
        "impersonate": profile,
        "headers": headers,
    }
