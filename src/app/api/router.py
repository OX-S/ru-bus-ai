from __future__ import annotations

from fastapi import APIRouter

from src.app.api.v1.endpoints import health as health_v1
from src.app.api.v1.endpoints import transit as transit_v1
from src.app.api.v1.endpoints import widgets as widgets_v1

api_router_v1 = APIRouter(prefix="/v1")
api_router_v1.include_router(health_v1.router)
api_router_v1.include_router(transit_v1.router)
api_router_v1.include_router(widgets_v1.router)