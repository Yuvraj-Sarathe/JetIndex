"""Aggregated v1 router — includes all sub-routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.anomalies import router as anomalies_router
from app.api.v1.apix import router as apix_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.data_quality import router as data_quality_router
from app.api.v1.elasticity import router as elasticity_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.reports import router as reports_router
from app.api.v1.routes import router as routes_router

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
