"""
JetIndex - Prometheus Metrics & Microservice Observability Service
Ported from VayuSutra-V4. Uses prometheus_client for OpenMetrics exposure.
"""

import logging

logger = logging.getLogger("jetindex.metrics")

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        REGISTRY,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.info("prometheus_client not installed, metrics endpoint will return empty")

if PROMETHEUS_AVAILABLE:
    QUOTES_INGESTED_TOTAL = Counter(
        "apix_quotes_ingested_total",
        "Total raw flight quotes ingested from all airlines and OTAs",
        ["source_portal", "route_corridor"],
    )
    QUOTES_REJECTED_OUTLIERS_TOTAL = Counter(
        "apix_quotes_rejected_outliers_total",
        "Total flight quotes rejected by MAD modified Z-score",
        ["filter_type"],
    )
    LASPEYRES_CURRENT_INDEX = Gauge("apix_laspeyres_current_index", "Current Master Laspeyres Airfare Price Index")
    FISHER_CURRENT_INDEX = Gauge("apix_fisher_current_index", "Current Fisher Ideal Index")
    PAASCHE_CURRENT_INDEX = Gauge("apix_paasche_current_index", "Current Paasche Index")
    SPOT_T1_INDEX = Gauge("apix_spot_t1_index", "Current Spot T+1 Sub-Index")
    CPI_TRANSPORT_IMPACT_BPS = Gauge("apix_cpi_transport_impact_bps", "CPI Transport impact in bps")
    CPI_HEADLINE_IMPACT_BPS = Gauge("apix_cpi_headline_impact_bps", "CPI Headline impact in bps")
    PIPELINE_DURATION_SECONDS = Histogram(
        "apix_pipeline_duration_seconds",
        "Pipeline execution duration",
        buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
    MODEL_TRAINING_R2 = Gauge("apix_model_training_r2", "Latest ML model R²")
    MODEL_TRAINING_RMSE = Gauge("apix_model_training_rmse", "Latest ML model RMSE")
    SYSTEM_CPU_PERCENT = Gauge("apix_system_cpu_percent", "Server CPU utilization %")
    SYSTEM_MEMORY_MB = Gauge("apix_system_memory_mb", "Server RAM in MB")
    ACTIVE_WEBSOCKET_CLIENTS = Gauge("apix_active_websocket_clients", "Active WebSocket clients")


def update_system_gauges():
    """Refreshes hardware metrics (optional, requires psutil)."""
    if not PROMETHEUS_AVAILABLE:
        return
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().used / (1024 * 1024)
        SYSTEM_CPU_PERCENT.set(cpu)
        SYSTEM_MEMORY_MB.set(mem)
    except Exception:
        pass


def get_prometheus_metrics_payload() -> tuple:
    """Generates OpenMetrics formatted byte buffer."""
    if not PROMETHEUS_AVAILABLE:
        return b"", "text/plain"
    update_system_gauges()
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
