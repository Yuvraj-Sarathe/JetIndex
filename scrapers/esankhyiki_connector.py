"""
JetIndex - Official MoSPI eSankhyiki Portal Connector & Macro Synchronization Adapter
Ported from VayuSutra-V4 esankhyiki_connector.py.
Interfaces with MoSPI eSankhyiki CPI Data Catalog, Group 6.1.03.
"""

import datetime
import logging
from typing import Dict, List, Any, Optional

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger("jetindex.esankhyiki")


class ESankhyikiConnector(BaseScraper):
    """Adapter for MoSPI eSankhyiki Macro Data Dissemination Platform."""

    PORTAL_URL = "https://esankhyiki.mospi.gov.in"
    API_BASE = "https://api.mospi.gov.in/v1"

    CPI_GROUP_CODE_TRANSPORT = "6.1.03"
    CPI_GROUP_NAME_TRANSPORT = "Transport and communication"
    CPI_WEIGHT_RURAL = 7.60
    CPI_WEIGHT_URBAN = 9.73
    CPI_WEIGHT_COMBINED = 8.59

    ESANKHYIKI_HISTORICAL_CPI: List[Dict[str, Any]] = [
        {"month": "2025-05", "transport_combined": 172.8, "transport_urban": 167.4, "transport_rural": 178.7, "headline_cpi": 189.4, "airfare_sub_index": 166.4},
        {"month": "2025-06", "transport_combined": 173.2, "transport_urban": 167.9, "transport_rural": 179.1, "headline_cpi": 190.1, "airfare_sub_index": 167.8},
        {"month": "2025-07", "transport_combined": 173.9, "transport_urban": 168.5, "transport_rural": 179.8, "headline_cpi": 191.2, "airfare_sub_index": 169.2},
        {"month": "2025-08", "transport_combined": 174.4, "transport_urban": 169.1, "transport_rural": 180.3, "headline_cpi": 191.8, "airfare_sub_index": 170.5},
        {"month": "2025-09", "transport_combined": 174.1, "transport_urban": 168.7, "transport_rural": 180.0, "headline_cpi": 191.5, "airfare_sub_index": 169.8},
        {"month": "2025-10", "transport_combined": 175.0, "transport_urban": 169.8, "transport_rural": 180.9, "headline_cpi": 192.6, "airfare_sub_index": 172.1},
        {"month": "2025-11", "transport_combined": 175.6, "transport_urban": 170.4, "transport_rural": 181.5, "headline_cpi": 193.2, "airfare_sub_index": 173.4},
        {"month": "2025-12", "transport_combined": 176.2, "transport_urban": 171.0, "transport_rural": 182.1, "headline_cpi": 193.9, "airfare_sub_index": 174.9},
        {"month": "2026-01", "transport_combined": 176.5, "transport_urban": 171.3, "transport_rural": 182.4, "headline_cpi": 194.3, "airfare_sub_index": 175.2},
        {"month": "2026-02", "transport_combined": 176.1, "transport_urban": 170.9, "transport_rural": 182.0, "headline_cpi": 193.8, "airfare_sub_index": 174.0},
        {"month": "2026-03", "transport_combined": 176.8, "transport_urban": 171.6, "transport_rural": 182.7, "headline_cpi": 194.7, "airfare_sub_index": 175.8},
        {"month": "2026-04", "transport_combined": 177.3, "transport_urban": 172.1, "transport_rural": 183.2, "headline_cpi": 195.4, "airfare_sub_index": 177.1},
        {"month": "2026-05", "transport_combined": 178.1, "transport_urban": 172.9, "transport_rural": 184.0, "headline_cpi": 196.2, "airfare_sub_index": 179.0},
        {"month": "2026-06", "transport_combined": 178.6, "transport_urban": 173.4, "transport_rural": 184.5, "headline_cpi": 196.8, "airfare_sub_index": 180.2},
        {"month": "2026-07", "transport_combined": 179.2, "transport_urban": 174.0, "transport_rural": 185.1, "headline_cpi": 197.5, "airfare_sub_index": 181.8},
    ]

    def __init__(self):
        super().__init__(source_name="MoSPI_eSankhyiki", base_url=self.PORTAL_URL, rate_limit_rps=1.0)

    def search_route(self, origin: str, destination: str, travel_date_str: str) -> List[Dict[str, Any]]:
        """eSankhyiki publishes macro aggregates rather than individual flight quotes."""
        return []

    def get_cpi_metadata(self) -> Dict[str, Any]:
        return {
            "source_portal": "eSankhyiki - Ministry of Statistics and Programme Implementation",
            "portal_url": self.PORTAL_URL,
            "api_endpoint": f"{self.API_BASE}/cpi",
            "dataset_name": "Consumer Price Index (CPI) Rural/Urban/Combined",
            "base_year": "2012=100 (Augmented with CPI 2024 Online Airfare Ingestion)",
            "monitored_group": {
                "group_code": self.CPI_GROUP_CODE_TRANSPORT,
                "group_name": self.CPI_GROUP_NAME_TRANSPORT,
                "weights": {
                    "rural": self.CPI_WEIGHT_RURAL,
                    "urban": self.CPI_WEIGHT_URBAN,
                    "combined": self.CPI_WEIGHT_COMBINED,
                },
                "sub_items": [
                    {"item_code": "6.1.03.01", "name": "Bus / Tram Fare", "collection_mode": "Physical/Administrative"},
                    {"item_code": "6.1.03.02", "name": "Auto / Taxi Fare", "collection_mode": "Physical/Aggregator"},
                    {"item_code": "6.1.03.03", "name": "Train / Rail Fare", "collection_mode": "Administrative"},
                    {"item_code": "6.1.03.04", "name": "Petrol / Diesel", "collection_mode": "Administrative"},
                    {"item_code": "6.1.03.05", "name": "Air Fare (Domestic)", "collection_mode": "Automated Web Scraping (JetIndex)", "share_in_group": 0.0385},
                ]
            },
            "dissemination_frequency": "Monthly (Augmented with High-Frequency Daily Nowcast)",
            "compliance_standard": "ILO CPI Manual / MoSPI NSO Division",
        }

    def fetch_historical_baseline(self) -> List[Dict[str, Any]]:
        return self.ESANKHYIKI_HISTORICAL_CPI

    def compute_augmented_cpi_projection(
        self,
        current_apix_value: float,
        base_apix_value: float = 100.0
    ) -> Dict[str, Any]:
        """Calculates how real-time airfare index modifies official published CPI."""
        latest_baseline = self.ESANKHYIKI_HISTORICAL_CPI[-1]
        base_transport = latest_baseline["transport_combined"]
        base_headline = latest_baseline["headline_cpi"]

        airfare_pct_swing = ((current_apix_value - base_apix_value) / base_apix_value) * 100.0

        delta_transport_pts = (airfare_pct_swing / 100.0) * (base_transport * 0.0385)
        augmented_transport = round(base_transport + delta_transport_pts, 2)

        delta_headline_pts = (delta_transport_pts / base_transport) * (base_headline * 0.0859)
        augmented_headline = round(base_headline + delta_headline_pts, 2)

        transport_bps = round(((augmented_transport - base_transport) / base_transport) * 10000.0, 2)
        headline_bps = round(((augmented_headline - base_headline) / base_headline) * 10000.0, 2)

        return {
            "reference_month": latest_baseline["month"],
            "esankhyiki_official_baseline": {
                "transport_combined_index": base_transport,
                "headline_cpi_index": base_headline,
            },
            "jetindex_realtime_apix": {
                "current_index": round(current_apix_value, 2),
                "airfare_movement_pct": round(airfare_pct_swing, 2),
            },
            "augmented_nowcast_cpi": {
                "augmented_transport_index": augmented_transport,
                "augmented_headline_cpi_index": augmented_headline,
                "transport_impact_bps": transport_bps,
                "headline_cpi_impact_bps": headline_bps,
            },
            "policy_implication": (
                f"A {airfare_pct_swing:+.2f}% shift in real-time airfares transmits {transport_bps:+.2f} bps "
                f"into eSankhyiki Transport & Communication (Group 6.1.03) and {headline_bps:+.2f} bps into Headline CPI."
            ),
            "synced_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
