"""Aggregated v1 router — includes all sub-routers."""

from fastapi import APIRouter

from app.api.v1.apix import router as apix_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.elasticity import router as elasticity_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.routes import router as routes_router

router = APIRouter()

router.include_router(apix_router, prefix="/apix", tags=["apix"])
router.include_router(routes_router, prefix="/routes", tags=["routes"])
router.include_router(elasticity_router, prefix="/elasticity", tags=["elasticity"])
router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
