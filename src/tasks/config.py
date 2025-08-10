from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(_REPO_ROOT / ".env")

def _env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return val

@dataclass(frozen=True)
class Settings:
    repo_root: Path = _REPO_ROOT
    data_dir: Path = Path(os.getenv("DATA_DIR") or (_REPO_ROOT / "data"))
    index_dir: Path = Path(os.getenv("INDEX_DIR") or (_REPO_ROOT / "data" / "index"))

    gtfs_url: str = _env("GTFS_URL", "https://passio3.com/rutgers/passioTransit/gtfs/google_transit.zip")
    gtfs_schema: str = _env("GTFS_SCHEMA", "gtfs")

    database_url: str | None = os.getenv("DATABASE_URL")
    pg_host: str = os.getenv("PGHOST", "localhost")
    pg_port: str = os.getenv("PGPORT", "5432")
    pg_user: str = os.getenv("PGUSER", "appuser")
    pg_password: str = os.getenv("PGPASSWORD", "1234")
    pg_database: str = os.getenv("PGDATABASE", "ru_gtfs")

    build_faiss: bool = os.getenv("BUILD_FAISS", "true").lower() == "true"
    sbert_model: str = os.getenv("SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    def dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.index_dir.mkdir(parents=True, exist_ok=True)
