# src/app/api/v1/endpoints/transit.py
from __future__ import annotations

import time
from fastapi import APIRouter, Depends, HTTPException, Query
import redis.asyncio as redis

from src.app.api.deps import get_redis
from src.app.schemas.transit import (
    ArrivalsResponse,
    ArrivalItem,
    VehiclesResponse,
    Vehicle,
    AlertsResponse,
)
from src.app.services.transit_cache import (
    get_stop_arrivals as svc_get_stop_arrivals,
    get_route_vehicles as svc_get_route_vehicles,
    get_vehicle as svc_get_vehicle,
    get_alerts as svc_get_alerts,
)

router = APIRouter(prefix="", tags=["transit"])

@router.get("/stops/{stop_id}/arrivals", response_model=ArrivalsResponse)
async def get_stop_arrivals(
    stop_id: str,
    limit: int = Query(10, ge=1, le=50),
    horizon_sec: int = Query(3 * 3600, ge=300, le=12 * 3600),
    r: redis.Redis = Depends(get_redis),
):
    arrivals_raw, stale = await svc_get_stop_arrivals(r, stop_id, limit, horizon_sec)
    arrivals = [ArrivalItem(**doc) for doc in arrivals_raw]
    return ArrivalsResponse(
        stop_id=stop_id,
        as_of=int(time.time() * 1000),
        arrivals=arrivals,
        stale=stale,
    )

@router.get("/routes/{route_id}/vehicles", response_model=VehiclesResponse)
async def get_route_vehicles(route_id: str, r: redis.Redis = Depends(get_redis)):
    vehicles_docs, stale = await svc_get_route_vehicles(r, route_id)
    vehicles = [Vehicle(**doc) for doc in vehicles_docs]
    return VehiclesResponse(
        route_id=route_id,
        as_of=int(time.time() * 1000),
        vehicles=vehicles,
        stale=stale,
    )

@router.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, r: redis.Redis = Depends(get_redis)):
    doc = await svc_get_vehicle(r, vehicle_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return Vehicle(**doc)

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(r: redis.Redis = Depends(get_redis)):
    data = await svc_get_alerts(r)
    return AlertsResponse(**data)