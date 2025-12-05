from __future__ import annotations

from typing import List, Literal, Union
from pydantic import BaseModel, Field



class ChatMessageConfig(BaseModel):
    type: Literal["chat_message"] = "chat_message"
    message: str


class BusArrivalsConfig(BaseModel):
    type: Literal["bus_arrivals"] = "bus_arrivals"
    stopIds: List[str]


class ActiveRoutesConfig(BaseModel):
    type: Literal["active_routes"] = "active_routes"

class ArrivalsWidgetRequest(BaseModel):
    stop_ids: List[str] = Field(..., min_items=1)
    horizon_sec: int = Field(45*60, ge=300, le=12*3600)
    per_stop_limit: int = Field(30, ge=1, le=100)


LLMWidgetConfig = Union[ChatMessageConfig, BusArrivalsConfig, ActiveRoutesConfig]

