"""app/config.py — Configuration settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dockerized FastAPI with PostgreSQL & Redis"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    DOCS_URL: str = "/docs"
    DATABASE_URL: str = "postgresql+psycopg2://admin:supersecretpassword123@db:5432/product_catalog"
    REDIS_URL: str = "redis://cache:6379/0"
    CACHE_DEFAULT_TTL_SECONDS: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        case_sensitive = True


settings = Settings()