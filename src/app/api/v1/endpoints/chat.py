from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union

from src.app.schemas.chat_widgets import (
    ActiveRoutesConfig,
    BusArrivalsConfig,
    ChatMessageConfig,
    LLMWidgetConfig,
)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post(
    "",
    summary="Chat with the model router",
    response_model=LLMWidgetConfig,
)
async def chat(req: ChatRequest) -> LLMWidgetConfig:
    # TODO: LLM router.
    return ChatMessageConfig(message="Chat backend not wired to LLM yet.")
