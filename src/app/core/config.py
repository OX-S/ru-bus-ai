# src/app/core/config.py
from __future__ import annotations
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = Field("Bus LLM Backend", env="APP_NAME")
    APP_VERSION: str = Field("0.1.0", env="APP_VERSION")
    API_PREFIX: str = Field("/v1", env="API_PREFIX")

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SQL_ECHO: bool = Field(False, env="SQL_ECHO")
    DB_CONNECT_TIMEOUT: int = Field(5, env="DB_CONNECT_TIMEOUT")
    GTFS_SCHEMA: str = Field("gtfs", env="GTFS_SCHEMA")

    CORS_ALLOW_ORIGINS: str = Field("*", env="CORS_ALLOW_ORIGINS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origins(self) -> List[str]:
        if self.CORS_ALLOW_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]

@lru_cache
def _cached_settings() -> Settings:
    return Settings()

settings: Settings = _cached_settings()
