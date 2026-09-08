"""SQLAlchemy 2 declarative models for TimescaleDB tables."""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.session import Base


class Route(Base):
    """DGCA sector basket route with airport coordinates."""

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_code = Column(String(10), unique=True, nullable=False, index=True)  # "DEL-BOM"
    origin = Column(String(3), nullable=False)  # IATA
    destination = Column(String(3), nullable=False)  # IATA
    o_lat = Column(Float)
    o_lon = Column(Float)
    d_lat = Column(Float)
    d_lon = Column(Float)
    active = Column(Boolean, default=True)

    # Relationships
    raw_quotes = relationship("RawQuote", back_populates="route")
    fare_quotes = relationship("FareQuote", back_populates="route")
    dgca_weights = relationship("DgcaWeight", back_populates="route")


class RawQuote(Base):
    """Raw scraper payload — audit/landing table."""

    __tablename__ = "raw_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    scrape_date = Column(Date, nullable=False)
    depart_date = Column(Date, nullable=False)
    lead_time = Column(Integer, nullable=False)
    fetched_at = Column(DateTime, nullable=False)
    status_code = Column(Integer)
    method = Column(String(20))  # "curl_cffi" or "playwright"
    proxy_used = Column(String(255))
    raw_path = Column(String(500))
    payload = Column(JSONB)

    # Relationships
    route = relationship("Route", back_populates="raw_quotes")


class FareQuote(Base):
    """Clean, unbundled fare quote — TimescaleDB hypertable on scraped_at."""

    __tablename__ = "fare_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    carrier = Column(String(10), nullable=False, index=True)
    flight_no = Column(String(20))
    depart_date = Column(Date, nullable=False)
    depart_time = Column(DateTime)
    lead_time = Column(Integer, nullable=False, index=True)
    fare_class = Column(String(30))
    base_fare = Column(Float, nullable=False)
    udf = Column(Float, default=0)
    taxes = Column(Float, default=0)
    convenience_fee = Column(Float, default=0)
    other_fees = Column(Float, default=0)
    total_fare = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    is_refundable = Column(Boolean)
    stops = Column(Integer, default=0)
    source = Column(String(20))
    scraped_at = Column(DateTime, nullable=False, index=True)  # Hypertable partition column
    raw_quote_id = Column(Integer, ForeignKey("raw_quotes.id"))
    quality_flag = Column(String(20), default="ok")

    # Relationships
    route = relationship("Route", back_populates="fare_quotes")


class ApixDaily(Base):
    """Daily APIx index values."""

    __tablename__ = "apix_daily"

    date = Column(Date, primary_key=True)
    apix = Column(Float, nullable=False)
    apix_base_only = Column(Float)
    n_quotes = Column(Integer, default=0)
    n_routes = Column(Integer, default=0)
    method = Column(String(20), default="laspeyres")
    base_period = Column(String(30))  # e.g., "2025-01-01 to 2025-01-07"


class DgcaWeight(Base):
    """DGCA passenger volume weights for index calculation."""

    __tablename__ = "dgca_weights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    period = Column(String(10), nullable=False)  # "2025-01"
    passengers = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    # Relationships
    route = relationship("Route", back_populates="dgca_weights")


class DgcaBenchmark(Base):
    """DGCA monthly average fares for backtesting, per route."""

    __tablename__ = "dgca_benchmark"

    route_code = Column(String(10), primary_key=True)  # "DEL-BOM"
    month = Column(String(7), primary_key=True)  # "2025-01"
    avg_fare = Column(Float, nullable=False)
    source_url = Column(String(500))

    __table_args__ = (UniqueConstraint("route_code", "month", name="uq_dgca_benchmark_route_month"),)
