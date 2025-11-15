from __future__ import annotations

import time
from typing import List, Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.app.core.config import settings
from src.app.db.session import psql_ping
from src.app.schemas.transit import (
    ActiveRoutesResponse,
    ArrivalsWidgetResponse,
    WidgetStop,
)
from src.app.services import transit_cache

router = APIRouter(prefix="/widgets", tags=["widgets"])

# ---------- models ----------
class ArrivalsWidgetRequest(BaseModel):
    stop_ids: List[str] = Field(..., min_items=1)
    horizon_sec: int = Field(45*60, ge=300, le=12*3600)
    per_stop_limit: int = Field(30, ge=1, le=100)

# ---------- redis dependency ----------
async def get_redis(request: Request) -> redis.Redis:
    # Reuse app-level redis if available
    r: Optional[redis.Redis] = getattr(request.app.state, "redis", None)
    if r is None:
        r = redis.from_url(settings.redis_url, decode_responses=False)
        # mark for cleanup after response if you have lifespan hooks; otherwise leave pooled
        request.state._redis_ephemeral = r
    return r

# ---------- endpoint ----------
@router.post("/arrivals", response_model=ArrivalsWidgetResponse)
async def arrivals_widget(req: ArrivalsWidgetRequest, r: redis.Redis = Depends(get_redis)):
    try:
        psql_ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unavailable: {e}")

    stops: List[WidgetStop] = await transit_cache.get_arrivals_widget(
        r,
        stop_ids=req.stop_ids,
        horizon_sec=req.horizon_sec,
        per_stop_limit=req.per_stop_limit,
    )
    return ArrivalsWidgetResponse(as_of=int(time.time() * 1000), stops=stops)

@router.get("/active-routes", response_model=ActiveRoutesResponse)
async def active_routes_widget(r: redis.Redis = Depends(get_redis)):
    try:
        psql_ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unavailable: {e}")

    routes = await transit_cache.get_active_routes(r)
    return ActiveRoutesResponse(as_of=int(time.time() * 1000), routes=routes)
