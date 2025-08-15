# src/app/db/session.py
from __future__ import annotations
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": settings.db_connect_timeout},
    future=True,
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def psql_ping() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.execute(
            text("SELECT to_regnamespace(:nsp) IS NOT NULL"),
            {"nsp": settings.gtfs_schema},
        )
