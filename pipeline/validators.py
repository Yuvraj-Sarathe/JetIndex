"""Validators — business-rule checks for raw quotes."""

from loguru import logger

from pipeline.schemas import RawQuote

# Allowed carriers
ALLOWED_CARRIERS = {"6E", "AI", "QP", "SG", "UK", "G8", "I5"}


def validate_raw(q: RawQuote) -> RawQuote | None:
    """
    Validate a raw quote against business rules.

    Returns the quote if valid, None if invalid (and logs the reason).
    """
    # Positive fares
    if q.total_fare <= 0:
        logger.warning(f"Rejected {q.flight_no}: non-positive fare {q.total_fare}")
        return None

    # Depart date must be after scrape date
    if q.depart_date <= q.scrape_date:
        logger.warning(f"Rejected {q.flight_no}: depart_date {q.depart_date} <= scrape_date {q.scrape_date}")
        return None

    # Lead time must match
    expected_lead = (q.depart_date - q.scrape_date).days
    if q.lead_time != expected_lead:
        logger.warning(f"Rejected {q.flight_no}: lead_time mismatch {q.lead_time} != {expected_lead}")
        return None

    # Carrier allow-list
    if q.carrier not in ALLOWED_CARRIERS:
        logger.warning(f"Rejected {q.flight_no}: unknown carrier '{q.carrier}'")
        return None

    # Currency must be INR
    if q.currency != "INR":
        logger.warning(f"Rejected {q.flight_no}: non-INR currency '{q.currency}'")
        return None

    return q
