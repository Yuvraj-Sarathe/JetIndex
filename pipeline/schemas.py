"""DATA CONTRACT — Pydantic v2 models for fare quotes.

This is the single canonical schema. Frozen after Day-1 review.
All other packages build against these models.
"""

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class RawQuote(BaseModel):
    """Raw fare quote as parsed directly from scraper output.

    Fields are vendor-specific and unnormalised.
    """

    model_config = ConfigDict(extra="forbid")

    # Identity
    source: Literal["indigo", "makemytrip", "airindia", "akasa", "easemytrip"]
    route_code: str  # "DEL-BOM"
    origin: str  # IATA code
    destination: str  # IATA code
    carrier: str  # "6E", "AI", "QP", "SG"
    flight_no: str
    depart_date: date
    depart_time: time | None = None
    scrape_date: date
    scraped_at: datetime
    lead_time: int  # days between scrape_date and depart_date
    fare_class: str | None = None  # "Saver", "Flexi", "Economy"
    stops: int = 0
    is_refundable: bool | None = None
    currency: str = "INR"

    # Money, as reported (unnormalised)
    total_fare: float
    fare_breakdown: dict[str, float]  # vendor labels → amounts
    seats_left: int | None = None
    sold_out: bool = False

    # Audit
    raw_ref: str  # path to raw payload


class CleanQuote(BaseModel):
    """Normalised fare quote with unbundled canonical components.

    Total fare is split into: base_fare | udf | taxes | convenience_fee | other_fees.
    """

    model_config = ConfigDict(extra="forbid")

    # Identity
    route_code: str
    origin: str
    destination: str
    carrier: str
    flight_no: str
    depart_date: date
    depart_time: time | None = None
    scrape_date: date
    scraped_at: datetime
    lead_time: int
    fare_class: str | None = None
    stops: int = 0
    is_refundable: bool | None = None
    source: str
    currency: str = "INR"

    # Unbundled fare components
    base_fare: float
    udf: float = 0.0
    taxes: float = 0.0  # GST + PSF + ASF etc.
    convenience_fee: float = 0.0
    other_fees: float = 0.0
    total_fare: float

    # Quality
    quality_flag: Literal["ok", "iqr_outlier", "sold_out", "sum_mismatch", "duplicate"] = "ok"

    # Audit
    raw_ref: str

    @model_validator(mode="after")
    def check_sum_consistency(self) -> "CleanQuote":
        """Verify that unbundled components sum to total_fare (±₹5 tolerance)."""
        computed_total = self.base_fare + self.udf + self.taxes + self.convenience_fee + self.other_fees
        if abs(computed_total - self.total_fare) > 5.0:
            self.quality_flag = "sum_mismatch"
        return self


# Alias — kept because the SIH PDF refers to FlightQuote
FlightQuote = CleanQuote
