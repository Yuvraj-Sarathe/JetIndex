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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1213.53",  # noqa: E501
]

# Standard headers that real browsers send
STANDARD_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def get_random_profile() -> dict:
    """Return a random impersonate profile + matching headers."""
    profile = random.choice(IMPERSONATE_PROFILES)
    ua = random.choice(USER_AGENTS)
    headers = {**STANDARD_HEADERS, "User-Agent": ua}
    return {
        "impersonate": profile,
        "headers": headers,
    }


def get_headers_for_profile(profile: str | None = None) -> dict:
    """Get headers matching a specific profile, or random if None."""
    if profile and profile in IMPERSONATE_PROFILES:
        ua_idx = IMPERSONATE_PROFILES.index(profile) % len(USER_AGENTS)
        return {**STANDARD_HEADERS, "User-Agent": USER_AGENTS[ua_idx]}
    return get_random_profile()["headers"]
