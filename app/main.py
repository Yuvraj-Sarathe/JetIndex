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

    # Create all tables on startup (safe — no-ops if they already exist)
    # Skip in mock mode to avoid needing a real database connection
    if not settings.MOCK_MODE:
        try:
            from db.session import Base, SessionLocal, engine

            Base.metadata.create_all(bind=engine)

            # Auto-enable mock mode if DB has no routes (prevents empty-dashboard 500s)
            from sqlalchemy import select

            from db.models import Route

            session = SessionLocal()
            try:
                has_routes = session.execute(select(Route).limit(1)).scalar_one_or_none()
                if not has_routes:
                    settings.MOCK_MODE = True
            finally:
                session.close()
        except Exception:
            # DB unreachable — fall back to mock mode so the app still starts
            settings.MOCK_MODE = True

    # CORS for frontend dev server + Vercel production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "https://jetindex.vercel.app",
        ],
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
