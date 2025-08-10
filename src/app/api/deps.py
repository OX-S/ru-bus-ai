from __future__ import annotations
from typing import Generator
from sqlalchemy.orm import Session
from src.app.db.session import get_session

def get_db() -> Generator[Session, None, None]:
    with get_session() as sess:
        yield sess
