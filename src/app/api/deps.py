from __future__ import annotations
from fastapi import Request
from typing import Generator, cast, Iterable
from sqlalchemy.orm import Session
from src.app.db.session import get_session
from src.app.core.config import settings
import redis.asyncio as redis
from starlette.datastructures import State
from src.app.db import redis_client as redis_db


async def get_settings():
    return settings

def get_db() -> Generator[Session, None, None]:
    with get_session() as sess:
        yield sess

async def get_redis(request: Request) -> redis.Redis:
    state: State = cast(State, request.app.state)
    client = getattr(state, "redis", None)
    if client is None:
        # Lazy init fallback
        client = await redis_db.connect(settings.redis_url)
        setattr(state, "redis", client)
    return client

def k(*parts: Iterable[str]) -> str:
    return ":".join([settings.redis_key_prefix, *parts])