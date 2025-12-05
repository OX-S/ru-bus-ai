from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.app.schemas.chat import ChatRequest
from src.app.schemas.chat_widgets import LLMWidgetConfig
from src.app.services.llm_router import route_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    summary="Chat with the model router",
    response_model=LLMWidgetConfig,
)
async def chat(req: ChatRequest) -> LLMWidgetConfig:
    try:
        return await route_message(req.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM routing failed: {exc}")
