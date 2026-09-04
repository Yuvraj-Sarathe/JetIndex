"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="APIx – Airfare Price Index API",
        description=(
            "Real-time airfare price index for India, "
            "powered by automated scraping and DGCA-weighted Laspeyres methodology."
        ),
        version="0.1.0",
    )

    # CORS for frontend dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "mock_mode": settings.MOCK_MODE,
            "version": "0.1.0",
        }

    # Mount API router
    from app.api.v1.router import router as v1_router

    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
