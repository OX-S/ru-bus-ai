from sqlalchemy.orm import Session
from src.app.db.session import get_session

def get_db() -> Session:           # ← now a plain sync generator
    with get_session() as sess:
        yield sess
