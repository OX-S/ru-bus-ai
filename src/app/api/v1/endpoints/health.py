from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
import redis.asyncio as redis

from src.app.api.deps import get_redis
from src.app.services.transit_cache import get_health as redis_health
from src.app.db.session import psql_ping

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", summary="Liveness probe")
def liveness() -> dict[str, str]:
    # Process can answer HTTP.
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def readiness(r: redis.Redis = Depends(get_redis)) -> dict[str, object]:
    pg_ok = True
    try:
        psql_ping()
    except Exception:
        pg_ok = False

    redis_ok = True
    vehicle_positions_stale = True
    try:
        rh = await redis_health(r)
        redis_ok = bool(rh.get("ok"))
        vehicle_positions_stale = bool(rh.get("vehicle_positions_stale"))
    except Exception:
        redis_ok = False

    if not (pg_ok and redis_ok):
        detail = {"postgres_ok": pg_ok, "redis_ok": redis_ok}
        raise HTTPException(status_code=503, detail=detail)

    return {
        "status": "ready",
        "postgres_ok": pg_ok,
        "redis_ok": redis_ok,
        "vehicle_positions_stale": vehicle_positions_stale,
    }
