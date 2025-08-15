# src/app/schemas/transit.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ArrivalItem(BaseModel):
    trip_id: Optional[str] = None
    route_id: Optional[str] = None
    stop_sequence: Optional[int] = None
    arrival: Optional[int] = None
    departure: Optional[int] = None
    delay_s: Optional[int] = None
    eta_seconds: Optional[int] = None

class ArrivalsResponse(BaseModel):
    stop_id: str
    as_of: int
    arrivals: List[ArrivalItem]
    stale: bool = False

class Vehicle(BaseModel):
    vehicle_id: str
    trip_id: Optional[str] = None
    route_id: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    label: Optional[str] = None
    updated_at: Optional[int] = None
    ingested_at_ms: Optional[int] = None

class VehiclesResponse(BaseModel):
    route_id: str
    as_of: int
    vehicles: List[Vehicle]
    stale: bool = False

class AlertsResponse(BaseModel):
    as_of: int
    alerts: List[Dict[str, Any]]