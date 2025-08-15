from __future__ import annotations

from typing import Optional
import redis.asyncio as redis

RedisClient = redis.Redis

async def connect(url: str) -> RedisClient:
    return redis.from_url(url, decode_responses=False)

async def close(client: Optional[RedisClient]) -> None:
    if client is not None:
        await client.aclose()