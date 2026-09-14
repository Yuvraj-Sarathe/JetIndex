<!-- generated-by: gsd-doc-writer -->

# Data Contract

This document describes the canonical data schemas used throughout the JetIndex pipeline. The schemas are defined in `pipeline/schemas.py` and are **frozen** — changes require a tagged PR and approval from the team lead.

## RawQuote

Raw fare quote as parsed directly from scraper output. Fields are vendor-specific and unnormalised.

```python
class RawQuote(BaseModel):
    # Identity
    source: Literal["indigo", "makemytrip", "airindia", "akasa", "easemytrip"]
    route_code: str          # "DEL-BOM"
    origin: str              # IATA code
    destination: str         # IATA code
    carrier: str             # "6E", "AI", "QP", "SG"
    flight_no: str
    depart_date: date
    depart_time: time | None
    scrape_date: date
    scraped_at: datetime
    lead_time: int           # days between scrape_date and depart_date
    fare_class: str | None   # "Saver", "Flexi", "Economy"
    stops: int = 0
    is_refundable: bool | None
    currency: str = "INR"

    # Money, as reported (unnormalised)
    total_fare: float
    fare_breakdown: dict[str, float]  # vendor labels → amounts
    seats_left: int | None
    sold_out: bool = False

    # Audit
    raw_ref: str             # path to raw payload
```

## CleanQuote

Normalised fare quote with unbundled canonical components. This is the primary schema used for index computation and API responses.

```python
class CleanQuote(BaseModel):
    # Identity
    route_code: str
    origin: str
    destination: str
    carrier: str
    flight_no: str
    depart_date: date
    depart_time: time | None
    scrape_date: date
    scraped_at: datetime
    lead_time: int
    fare_class: str | None
    stops: int = 0
    is_refundable: bool | None
    source: str
    currency: str = "INR"

    # Unbundled fare components
    base_fare: float
    udf: float = 0.0         # User Development Fee
    taxes: float = 0.0       # GST + PSF + ASF
    convenience_fee: float = 0.0
    other_fees: float = 0.0
    total_fare: float

    # Quality
    quality_flag: Literal["ok", "iqr_outlier", "sold_out", "sum_mismatch", "duplicate"] = "ok"

    # Audit
    raw_ref: str
```

## Fee Mapping

The unbundler maps vendor-specific fare labels to canonical components:

| Canonical Component | Vendor Labels (examples) | Description |
|---------------------|--------------------------|-------------|
| `base_fare` | Base Fare, Basic Fare, Ticket Price | Core ticket price |
| `udf` | UDF, User Development Fee, Airport Fee | Airport infrastructure charges |
| `taxes` | GST, PSF, ASF, Service Tax, Passenger Fee | Government taxes and statutory charges |
| `convenience_fee` | Convenience Fee, Platform Fee, Booking Fee | OTA platform charges |
| `other_fees` | Fuel Surcharge, Meals, Seats, Baggage | Ancillary charges |

**Statutory Constants:**
- ASF (Airport Security Fee): ₹200
- PSF (Passenger Service Fee): ₹91
- UDF (User Development Fee): ₹420 (varies by airport)
- GST: 5% on base fare

## Sum Consistency Check

A `model_validator` on `CleanQuote` verifies that unbundled components sum to `total_fare` within ±₹5 tolerance. If the sum deviates, `quality_flag` is set to `"sum_mismatch"`.

```python
@model_validator(mode="after")
def check_sum_consistency(self) -> "CleanQuote":
    computed_total = self.base_fare + self.udf + self.taxes + self.convenience_fee + self.other_fees
    if abs(computed_total - self.total_fare) > 5.0:
        self.quality_flag = "sum_mismatch"
    return self
```

## Quality Flags

| Flag | Description |
|------|-------------|
| `ok` | Quote passed all validation checks |
| `iqr_outlier` | Fare is a statistical outlier (MAD Z-score or IQR) |
| `sold_out` | Flight is sold out (0 seats available) |
| `sum_mismatch` | Unbundled components do not sum to total_fare (±₹5) |
| `duplicate` | Duplicate quote detected (same source, route, carrier, flight, date) |

## Carrier Allowlist

Only flights from these carriers are included in the index:

| Code | Carrier |
|------|---------|
| `6E` | IndiGo |
| `AI` | Air India |
| `QP` | Akasa Air |
| `SG` | SpiceJet |
| `UK` | Vistara |
| `G8` | GoFirst |
| `I5` | AirAsia India |

## Database Tables

### fare_quotes (TimescaleDB Hypertable)

The primary table for clean, unbundled fare quotes. Partitioned by `scraped_at` with 7-day chunks.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `source` | TEXT | Data source (indigo, makemytrip) |
| `route_id` | BIGINT | FK to routes table |
| `carrier` | TEXT | Airline code |
| `flight_no` | TEXT | Flight number |
| `depart_date` | DATE | Departure date |
| `lead_time` | INTEGER | Days between scrape and departure |
| `fare_class` | TEXT | Fare class (Saver, Flexi, etc.) |
| `base_fare` | NUMERIC | Base ticket price |
| `udf` | NUMERIC | User Development Fee |
| `taxes` | NUMERIC | GST + PSF + ASF |
| `convenience_fee` | NUMERIC | OTA platform fee |
| `other_fees` | NUMERIC | Fuel surcharge, meals, etc. |
| `total_fare` | NUMERIC | Total fare (sum of components) |
| `quality_flag` | TEXT | Quality indicator |
| `scraped_at` | TIMESTAMPTZ | Scrape timestamp (partition key) |

### routes

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `route_code` | TEXT | e.g., "DEL-BOM" |
| `origin` | TEXT | IATA code |
| `destination` | TEXT | IATA code |
| `weight` | NUMERIC | DGCA passenger volume weight |
| `is_metro` | BOOLEAN | Metro route flag |
| `o_lat`, `o_lon` | NUMERIC | Origin coordinates |
| `d_lat`, `d_lon` | NUMERIC | Destination coordinates |

### apix_daily

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Primary key |
| `apix` | NUMERIC | Laspeyres index value |
| `apix_base_only` | NUMERIC | Base-only variant |
| `n_quotes` | INTEGER | Number of quotes used |
| `n_routes` | INTEGER | Number of routes covered |
| `method` | TEXT | Index method used |
| `base_period` | TEXT | Base period description |
