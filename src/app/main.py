from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.core.config import settings
from src.app.api.v1.endpoints import health

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_PREFIX, tags=["health"])
# app.include_router(chat.router,   prefix=settings.API_PREFIX, tags=["chat"])
# app.include_router(data.router,   prefix=settings.API_PREFIX, tags=["data"])
