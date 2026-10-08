"""Configuración leída de variables de entorno (y de `.env` en desarrollo local)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno de la app. Cada campo se lee de su nombre en mayúsculas.

    La tabla completa (tipo, default, obligatoriedad) está en docs/configuracion.md.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "app-prueba"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/app"
    # Lista JSON, por ejemplo: CORS_ORIGINS='["http://localhost:5173"]'
    cors_origins: list[str] = []

    # OpenTelemetry se activa solo si OTEL_EXPORTER_OTLP_ENDPOINT tiene valor.
    otel_exporter_otlp_endpoint: str | None = None
    otel_service_name: str = "app-prueba-api"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración del proceso (se lee una sola vez y se cachea)."""
    return Settings()
