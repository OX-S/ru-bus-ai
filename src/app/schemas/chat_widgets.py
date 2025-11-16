from __future__ import annotations

from typing import List, Literal, Union

from pydantic import BaseModel


class ChatMessageConfig(BaseModel):
    type: Literal["chat_message"] = "chat_message"
    message: str


class BusArrivalsConfig(BaseModel):
    type: Literal["bus_arrivals"] = "bus_arrivals"
    stopIds: List[str]


class ActiveRoutesConfig(BaseModel):
    type: Literal["active_routes"] = "active_routes"


LLMWidgetConfig = Union[ChatMessageConfig, BusArrivalsConfig, ActiveRoutesConfig]

