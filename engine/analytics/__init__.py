"""Route Intelligence & Multi-Corridor Comparator Engine.

Re-exports everything from the analytics_engine module so that
`from engine.analytics import X` works for both the module's symbols
and the package's symbols.
"""
# Re-export analytics module contents (the .py file)
from engine.analytics_engine import (
    _AIRFARE_SHARE,
    _TRANSPORT_WEIGHT,
    compute_pressure_score,
    compute_cpi_decomposition,
    compute_heatmap,
    compute_trust_score,
    HeatmapCell,
    HeatmapMatrix,
    PressureReport,
    CPIDecomposition,
    TrustScoreReport,
    generate_temporal_heatmap,
    generate_carrier_comparative_heatmap,
    generate_route_index_growth_heatmap,
    TemporalHeatmapResult,
    DailyHeatmapCell,
)

# Package-level exports
from .route_intelligence import RouteIntelligenceEngine, route_intel_engine
from .source_analytics import SourceAnalyticsEngine
from .source_consensus import SourceConsensusReport, SourcePriceEntry, RouteConsensusRecord
from .source_telemetry import PORTAL_LABELS
from .temporal import TemporalAnalyticsEngine

__all__ = [
    "_AIRFARE_SHARE",
    "_TRANSPORT_WEIGHT",
    "compute_pressure_score",
    "compute_cpi_decomposition",
    "compute_heatmap",
    "compute_trust_score",
    "HeatmapCell",
    "HeatmapMatrix",
    "PressureReport",
    "CPIDecomposition",
    "TrustScoreReport",
    "generate_temporal_heatmap",
    "generate_carrier_comparative_heatmap",
    "generate_route_index_growth_heatmap",
    "TemporalHeatmapResult",
    "DailyHeatmapCell",
    "RouteIntelligenceEngine",
    "route_intel_engine",
    "SourceAnalyticsEngine",
    "SourceConsensusReport",
    "SourcePriceEntry",
    "RouteConsensusRecord",
    "PORTAL_LABELS",
    "TemporalAnalyticsEngine",
]
