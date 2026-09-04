"""Application settings — loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings. All packages import `settings` from here."""

    APP_ENV: str = "dev"
    MOCK_MODE: bool = True
    API_TOKEN: str = "change-me-dev-token"

    POSTGRES_USER: str = "apix"
    POSTGRES_PASSWORD: str = "apix"
    POSTGRES_DB: str = "apix"
    DATABASE_URL: str = "postgresql+psycopg://apix:apix@db:5432/apix"

    REDIS_URL: str = "redis://redis:6379/0"

    PROXY_ENABLED: bool = False
    PROXY_URL: str | None = None

    RAW_DATA_DIR: str = "data/raw"
    SCRAPE_HOUR_IST: int = 2
    LOG_LEVEL: str = "INFO"

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "minio123"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
