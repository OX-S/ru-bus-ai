from __future__ import annotations

import contextlib

from src.app.api.router import api_router_v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import State

from src.app.core.config import settings
from src.app.db import redis_client as redis_db

class App(FastAPI):
    state: State

@contextlib.asynccontextmanager
async def lifespan(app: App):
    state: State = app.state
    if getattr(state, "redis", None) is None:
        state.redis = await redis_db.connect(settings.redis_url)
    try:
        yield
    finally:
        await redis_db.close(getattr(state, "redis", None))

app = App(
    title=settings.app_name,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.on_event("startup")
async def _startup() -> None:
    state: State = app.state
    if getattr(state, "redis", None) is None:
        state.redis = await redis_db.connect(settings.redis_url)

@app.on_event("shutdown")
async def _shutdown() -> None:
    await redis_db.close(getattr(app.state, "redis", None))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router_v1, prefix=settings.api_prefix)