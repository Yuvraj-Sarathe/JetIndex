# `tests/`

Run: `make test` or `pytest`. CI runs `pytest -m "not integration"`.

- Mirror the package: `tests/test_<pkg>/test_<module>.py`.
- Fixtures in `conftest.py` (sample raw payloads, in-memory SQLite session). Real-DB tests → `@pytest.mark.integration`.
- Scraper tests must **never hit the network** — mock `curl_cffi` with `respx`/monkeypatch.
- Each owner: at least one test per public function you ship. PRs without tests get bounced.
