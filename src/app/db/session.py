"""
Central place to set up SQLAlchemy for an on‑disk DuckDB database.

• Uses the official `duckdb_engine` dialect  →  URI:  duckdb:///path/to/file.duckdb
• One shared connection is enough, so we wire SQLAlchemy to a StaticPool.
"""
import duckdb, duckdb_engine
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.core.config import settings  # expects settings.DUCKDB_PATH & settings.SQL_ECHO


DATABASE_URL = f"duckdb:///{settings.DUCKDB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    poolclass=StaticPool,
)


SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints or background tasks:

        with get_session() as db:
            ...

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping() -> None:
    """Raise if the file is gone or unreadable; return silently otherwise."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
