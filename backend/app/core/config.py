"""Application configuration and settings helpers."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Values can be provided via:
    - Environment variables OR
    - .env file
    """

    # App
    APP_NAME: str = "ERP Incident Triage API"
    ENV: str = "local"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg2://<username>:<password>@localhost:5432/erp_incidents"
    )

    # OpenAI (optional / stub-friendly)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    """
    return Settings()


settings = get_settings()
