"""Aggregated v1 router — includes all sub-routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.ai_analyst import router as ai_analyst_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.anomalies import router as anomalies_router
from app.api.v1.apix import router as apix_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.data_quality import router as data_quality_router
from app.api.v1.elasticity import router as elasticity_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.provenance import router as provenance_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.reports import router as reports_router
from app.api.v1.route_intelligence import router as route_intelligence_router
from app.api.v1.routes import router as routes_router
from app.api.v1.scenario import router as scenario_router
from app.api.v1.source_analytics import router as source_analytics_router
from app.api.v1.source_consensus import router as source_consensus_router
from app.api.v1.streaming import router as streaming_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.temporal import router as temporal_router
from app.api.v1.validation import router as validation_router

router = APIRouter()

router.include_router(admin_router)
router.include_router(apix_router, prefix="/apix", tags=["apix"])
router.include_router(routes_router, prefix="/routes", tags=["routes"])
router.include_router(elasticity_router, prefix="/elasticity", tags=["elasticity"])
router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
router.include_router(forecast_router, prefix="/forecast", tags=["forecast"])
router.include_router(anomalies_router, prefix="/anomalies", tags=["anomalies"])
router.include_router(data_quality_router, prefix="/data-quality", tags=["data-quality"])
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
router.include_router(route_intelligence_router, prefix="/route-intelligence", tags=["route-intelligence"])
router.include_router(source_analytics_router, prefix="/source-analytics", tags=["source-analytics"])
router.include_router(source_consensus_router, prefix="/source-consensus", tags=["source-consensus"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])
router.include_router(temporal_router, prefix="/temporal", tags=["temporal"])
router.include_router(scenario_router, prefix="/scenario", tags=["scenario"])
router.include_router(provenance_router, prefix="/provenance", tags=["provenance"])
router.include_router(validation_router, prefix="/validation", tags=["validation"])
router.include_router(ai_analyst_router, prefix="/ai-analyst", tags=["ai-analyst"])
router.include_router(streaming_router, tags=["streaming"])
