from __future__ import annotations

import asyncio
from typing import List, Optional, Tuple

import orjson
import requests

from src.app.core.config import settings
from src.app.schemas.chat_widgets import (
    ActiveRoutesConfig,
    BusArrivalsConfig,
    ChatMessageConfig,
    LLMWidgetConfig,
)
from src.app.services import semantic_search, transit_lookup


def _system_prompt() -> str:
    return (
        "You are a router for a Rutgers bus assistant. "
        "Respond with one JSON object only, no markdown. "
        'Allowed: {"type":"chat_message","message":"..."} '
        '{"type":"bus_arrivals","stopIds":["<stop_id>", "..."]} '
        '{"type":"active_routes"}. '
        "Use bus_arrivals when user asks about arrivals/next bus at a stop. "
        "Use active_routes when they ask which routes are running now. "
        "Otherwise use chat_message. "
        "Never invent stopIds; only use provided context."
    )


def _build_messages(user_message: str, context: Optional[str]) -> List[dict]:
    messages = [{"role": "system", "content": _system_prompt()}]
    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})
    messages.append({"role": "user", "content": user_message})
    return messages


def _parse_llm_json(raw_text: str) -> LLMWidgetConfig:
    try:
        data = orjson.loads(raw_text)
    except Exception:
        return ChatMessageConfig(message="Sorry, I could not understand that.")

    if not isinstance(data, dict):
        return ChatMessageConfig(message="Sorry, I could not understand that.")

    msg_type = data.get("type")
    if msg_type == "bus_arrivals":
        stop_ids = data.get("stopIds") or []
        return BusArrivalsConfig(stopIds=[str(s) for s in stop_ids])
    if msg_type == "active_routes":
        return ActiveRoutesConfig()
    if msg_type == "chat_message":
        message = data.get("message") or ""
        return ChatMessageConfig(message=message or "Let me help with that.")

    return ChatMessageConfig(message="Let me help with that.")


def _call_llm(messages: List[dict]) -> str:
    url = f"{settings.llm_api_base}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.2,
    }

    resp = requests.post(url, headers=headers, data=orjson.dumps(payload))
    resp.raise_for_status()
    body = resp.json()
    choice = body.get("choices", [{}])[0]
    msg = choice.get("message", {})
    content = msg.get("content")
    if not content:
        raise RuntimeError("LLM returned empty content")
    return content.strip()


def _resolve_context(user_message: str) -> Tuple[str, List[str]]:
    hits = semantic_search.search(user_message, k=5)
    stop_ids: List[str] = []
    parts: List[str] = []

    for hit in hits:
        meta = hit.get("metadata") or {}
        if meta.get("type") != "stop":
            continue
        stop_id = meta.get("stop_id")
        if not stop_id or stop_id in stop_ids:
            continue

        stop = transit_lookup.get_stop(stop_id)
        if not stop:
            continue
        routes = transit_lookup.get_routes_for_stop(stop_id)
        route_labels = [
            r["short_name"] or r["route_id"] for r in routes if r.get("route_id")
        ]
        stop_name = stop["name"] or stop_id
        label = f"Stop {stop_id} ({stop_name}), routes: {', '.join(route_labels) or 'none'}"
        parts.append(label)
        stop_ids.append(stop_id)

    context = " | ".join(parts)
    return context, stop_ids


async def route_message(user_message: str) -> LLMWidgetConfig:
    context, stop_ids = _resolve_context(user_message)
    messages = _build_messages(user_message, context or None)
    raw = await asyncio.to_thread(_call_llm, messages)
    result = _parse_llm_json(raw)

    if isinstance(result, BusArrivalsConfig) and not result.stopIds and stop_ids:
        return BusArrivalsConfig(stopIds=stop_ids)
    return result
