from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = Field("My Service", env="APP_NAME")
    APP_VERSION: str = Field("0.1.0", env="APP_VERSION")
    API_PREFIX: str = Field("/api/v1", env="API_PREFIX")


    DUCKDB_PATH: Path = Field("gtfs.duckdb", env="DUCKDB_PATH")
    SQL_ECHO: bool = Field(False, env="SQL_ECHO")   # SQLAlchemy echo flag
    #
    # CORS_ALLOW_ORIGINS: List[str] = Field(["*"], env="CORS_ALLOW_ORIGINS")
    #
    #
    # LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    #
    # # Read values from a .env file *in addition* to the actual env vars
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

@lru_cache
def _cached_settings() -> Settings:
    return Settings()

settings: Settings = _cached_settings()
