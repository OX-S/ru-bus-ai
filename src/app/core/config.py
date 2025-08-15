# src/app/core/config.py
from __future__ import annotations
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: str = "dev"
    app_name: str = "Bus LLM Backend"
    app_version: str = "0.1.0"

    api_prefix: str = "/api"
    api_version: str = "v1"

    database_url: str
    sql_echo: bool = False
    db_connect_timeout: int = 5
    gtfs_schema: str = "gtfs"

    cors_allow_origins: str = "*"

    redis_url: str = "redis://localhost:6379/0"
    redis_key_prefix: str = "gtfsrt"

    vehicle_positions_staleness_s: int = 60
    trip_updates_staleness_s: int = 90

    @property
    def allow_origins_list(self) -> List[str]:
        s = (self.cors_allow_origins or "").strip()
        return ["*"] if s == "*" else [o.strip() for o in s.split(",") if o.strip()]

@lru_cache
def _cached_settings() -> Settings:
    return Settings()

settings: Settings = _cached_settings()
