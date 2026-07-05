"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for local, container, and Cloud Run environments."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PharmaGenie"
    app_env: str = "local"
    log_level: str = "INFO"
    google_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "global"
    gemini_model: str = "gemini-2.5-flash"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    ncbi_email: str | None = None
    ncbi_api_key: str | None = None
    request_timeout_seconds: int = Field(default=20, ge=1, le=120)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
