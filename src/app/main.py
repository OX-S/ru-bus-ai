# src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.endpoints import health

app = FastAPI(title="Bus LLM Backend")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://your-frontend.com"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/v1"
app.include_router(health.router, prefix=api_prefix, tags=["health"])
# app.include_router(chat.router,   prefix=api_prefix, tags=["chat"])
# app.include_router(data.router,   prefix=api_prefix, tags=["data"])
