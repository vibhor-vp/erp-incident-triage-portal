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

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json|plain
    LOG_SERVICE_NAME: str = "erp-incident-triage-api"

    # CloudWatch logging (optional)
    CLOUDWATCH_ENABLED: bool = False
    AWS_REGION: str | None = None
    CLOUDWATCH_LOG_GROUP: str | None = None
    CLOUDWATCH_LOG_STREAM: str | None = None

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
