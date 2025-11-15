# src/app/services/transit_cache.py
from __future__ import annotations

import asyncio
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple

import anyio
import redis.asyncio as redis
from sqlalchemy import text

from src.app.core.config import settings
from src.app.db.session import get_session
from src.app.schemas.transit import (
    ActiveRoute,
    ArrivalItem,
    AlertsResponse,
    Vehicle,
    WidgetArrival,
    WidgetStop,
)
from src.app.utils.json import jload

JSONDict = Dict[str, Any]
DEFAULT_ROUTE_COLOR = "#666666"
ARRIVAL_LOOKBACK_SECONDS = 3600
_STALE_TTL_FRACTION = 4


# ---------------------------------------------------------------------------
# Helpers: general utilities
# ---------------------------------------------------------------------------

def _now_seconds() -> int:
    return int(time.time())


def _arrival_window(now_sec: int, horizon_sec: int) -> Tuple[int, int]:
    return now_sec - ARRIVAL_LOOKBACK_SECONDS, now_sec + horizon_sec


async def _is_feed_stale(client: redis.Redis, raw_key: str, threshold_sec: int) -> bool:
    """Return True when the cached GTFS feed should be considered stale."""
    ttl = await client.ttl(raw_key)
    if ttl is None or ttl < 0:
        return True
    return ttl < max(1, threshold_sec // _STALE_TTL_FRACTION)


def _coerce_int(value: Any) -> int | None:
    """Best-effort conversion to int; returns None on failure."""
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_unix_ts(value: Any) -> int | None:
    """Extract a Unix timestamp (seconds) from various shapes."""
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("time", "timestamp", "epoch", "seconds", "value"):
            if key in value:
                ts = _coerce_unix_ts(value[key])
                if ts is not None:
                    return ts
        return None
    if isinstance(value, (list, tuple)):
        for item in value:
            ts = _coerce_unix_ts(item)
            if ts is not None:
                return ts
        return None
    if isinstance(value, (int, float)):
        try:
            return int(float(value))
        except (TypeError, ValueError, OverflowError):
            return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(float(stripped))
        except (TypeError, ValueError):
            return None
    return None


def _ensure_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return None
    return str(value)


def _extract_arrival_epoch(doc: JSONDict) -> int | None:
    """Find the best arrival timestamp within a trip_update payload."""
    if not isinstance(doc, dict):
        return None

    for key in ("arrival", "arrival_time", "arrival_timestamp"):
        if key in doc:
            ts = _coerce_unix_ts(doc[key])
            if ts is not None:
                return ts

    updates = doc.get("stop_time_update")
    if not isinstance(updates, list):
        return None

    target_stop_id = doc.get("stop_id")
    target_stop_id = str(target_stop_id) if target_stop_id is not None else None
    target_seq = _coerce_int(doc.get("stop_sequence"))

    preferred: List[JSONDict] = []
    fallback: List[JSONDict] = []
    for update in updates:
        if not isinstance(update, dict):
            continue
        fallback.append(update)

        if target_stop_id is not None:
            update_stop = update.get("stop_id")
            if update_stop is not None and str(update_stop) != target_stop_id:
                continue
        if target_seq is not None:
            update_seq = _coerce_int(update.get("stop_sequence"))
            if update_seq is not None and update_seq != target_seq:
                continue
        preferred.append(update)

    for candidate in preferred + fallback:
        ts = _coerce_unix_ts(candidate.get("arrival"))
        if ts is None:
            ts = _coerce_unix_ts(candidate.get("arrival_time"))
        if ts is not None:
            return ts

    return None


def _populate_arrival_fields(doc: JSONDict, now_sec: int, score: Any | None = None) -> bool:
    """Populate `arrival` and `eta_seconds` keys from GTFS data."""
    arrival_ts = _extract_arrival_epoch(doc)
    if arrival_ts is None:
        arrival_ts = _coerce_unix_ts(score)

    arrival_ts = _coerce_unix_ts(arrival_ts)
    if arrival_ts is None:
        return False

    doc["arrival"] = arrival_ts
    doc["eta_seconds"] = max(0, arrival_ts - now_sec)
    return True


def _deserialize_arrival(payload: bytes, score: Any, now_sec: int) -> JSONDict | None:
    """Decode and enrich a cached arrival entry."""
    try:
        doc = jload(payload)
    except Exception:
        return None
    if not isinstance(doc, dict):
        return None
    if not _populate_arrival_fields(doc, now_sec, score):
        return None
    return doc


def _decode_json_bytes(payload: bytes | None) -> JSONDict | None:
    """Decode a JSON payload stored as bytes."""
    if not payload:
        return None
    try:
        data = jload(payload)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _sanitize_color(raw_color: Optional[str]) -> str:
    if not raw_color:
        return DEFAULT_ROUTE_COLOR
    color = raw_color.strip()
    if not color:
        return DEFAULT_ROUTE_COLOR
    return color if color.startswith("#") else f"#{color}"


def _trip_ids_from_docs(documents: List[JSONDict]) -> Set[str]:
    trip_ids: Set[str] = set()
    for doc in documents:
        trip_id = _ensure_str(doc.get("trip_id"))
        if trip_id:
            trip_ids.add(trip_id)
    return trip_ids


def _deserialize_rows(
    rows: List[Tuple[bytes, Any]],
    now_sec: int,
    limit: int,
) -> List[JSONDict]:
    documents: List[JSONDict] = []
    for payload, score in rows:
        doc = _deserialize_arrival(payload, score, now_sec)
        if doc:
            documents.append(doc)
    documents.sort(key=lambda item: item.get("eta_seconds", float("inf")))
    return documents[:limit]


def _build_arrival_item(doc: JSONDict, route_id: str) -> ArrivalItem:
    payload = {
        "trip_id": _ensure_str(doc.get("trip_id")),
        "route_id": route_id,
        "stop_sequence": _coerce_int(doc.get("stop_sequence")),
        "arrival": _coerce_int(doc.get("arrival")),
        "departure": _coerce_int(doc.get("departure")),
        "delay_s": _coerce_int(doc.get("delay_s") or doc.get("delay")),
        "eta_seconds": _coerce_int(doc.get("eta_seconds")),
    }
    return ArrivalItem(**payload)


def _build_vehicle(doc: JSONDict, route_id: Optional[str]) -> Vehicle | None:
    vehicle_id = _ensure_str(doc.get("vehicle_id"))
    if not vehicle_id:
        return None
    payload = {
        "vehicle_id": vehicle_id,
        "trip_id": _ensure_str(doc.get("trip_id")),
        "route_id": route_id or _ensure_str(doc.get("route_id")),
        "lat": _coerce_float(doc.get("lat")),
        "lon": _coerce_float(doc.get("lon")),
        "speed": _coerce_float(doc.get("speed")),
        "bearing": _coerce_float(doc.get("bearing")),
        "label": _ensure_str(doc.get("label")),
        "updated_at": _coerce_int(doc.get("updated_at")),
        "ingested_at_ms": _coerce_int(doc.get("ingested_at_ms")),
    }
    return Vehicle(**payload)


def _route_id_for_doc(doc: JSONDict, trip_map: Dict[str, str]) -> Optional[str]:
    trip_id = _ensure_str(doc.get("trip_id"))
    if not trip_id:
        return None
    return trip_map.get(trip_id)


def _default_route_meta(route_id: str) -> Dict[str, str]:
    return {"route_long_name": route_id, "route_color": DEFAULT_ROUTE_COLOR}


def _build_widget_arrival(doc: JSONDict, route_meta: Dict[str, str]) -> WidgetArrival:
    eta_seconds = _coerce_int(doc.get("eta_seconds")) or 0
    return WidgetArrival(
        eta_seconds=eta_seconds,
        route_long_name=route_meta.get("route_long_name", ""),
        route_color=route_meta.get("route_color", DEFAULT_ROUTE_COLOR),
        to="TBD",
    )


# ---------------------------------------------------------------------------
# Helpers: database lookups
# ---------------------------------------------------------------------------

async def _fetch_trip_route_map(trip_ids: Set[str]) -> Dict[str, str]:
    """Return trip_id -> route_id mapping for the requested trips."""
    if not trip_ids:
        return {}

    schema = settings.gtfs_schema
    query = text(f"SELECT trip_id, route_id FROM {schema}.trips WHERE trip_id = ANY(:ids)")

    def _run(ids: Set[str]) -> Dict[str, str]:
        with get_session() as db:
            rows = db.execute(query, {"ids": list(ids)}).all()
            return {str(trip): str(route) for trip, route in rows if route}

    try:
        return await anyio.to_thread.run_sync(_run, trip_ids)
    except Exception:
        return {}


async def _fetch_routes_metadata(route_ids: Set[str]) -> Dict[str, Dict[str, Any]]:
    """Return route metadata keyed by route_id."""
    if not route_ids:
        return {}

    schema = settings.gtfs_schema
    query = text(
        f"SELECT route_id, route_long_name, route_color "
        f"FROM {schema}.routes WHERE route_id = ANY(:ids)"
    )

    def _run(ids: Set[str]) -> Dict[str, Dict[str, Any]]:
        with get_session() as db:
            rows = db.execute(query, {"ids": list(ids)}).all()
            result: Dict[str, Dict[str, Any]] = {}
            for route_id, long_name, color in rows:
                hex_color = (color or "").strip()
                if hex_color and not hex_color.startswith("#"):
                    hex_color = f"#{hex_color}"
                result[str(route_id)] = {
                    "route_long_name": long_name or "",
                    "route_color": hex_color or DEFAULT_ROUTE_COLOR,
                }
            return result

    try:
        return await anyio.to_thread.run_sync(_run, route_ids)
    except Exception:
        return {}


async def _fetch_stop_names(stop_ids: Set[str]) -> Dict[str, str]:
    """Return stop_id -> stop_name mapping."""
    if not stop_ids:
        return {}

    schema = settings.gtfs_schema
    query = text(f"SELECT stop_id, stop_name FROM {schema}.stops WHERE stop_id = ANY(:ids)")

    def _run(ids: Set[str]) -> Dict[str, str]:
        with get_session() as db:
            rows = db.execute(query, {"ids": list(ids)}).all()
            return {str(stop): str(name) for stop, name in rows}

    try:
        return await anyio.to_thread.run_sync(_run, stop_ids)
    except Exception:
        return {}


async def _fetch_representative_trip_stop_names(
    route_id: str,
    direction_id: Optional[int] = None,
) -> List[str]:
    """Return ordered stop names for a representative trip on the route."""
    if not route_id:
        return []

    schema = settings.gtfs_schema
    direction_clause = "AND direction_id = :direction_id" if direction_id is not None else ""
    query = text(
        f"""
        WITH route_trips AS (
            SELECT trip_id
            FROM {schema}.trips
            WHERE route_id = :route_id
            {direction_clause}
        ),
        longest_trip AS (
            SELECT trip_id
            FROM (
                SELECT st.trip_id,
                       COUNT(*) AS stop_cnt,
                       ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, st.trip_id) AS rn
                FROM {schema}.stop_times st
                JOIN route_trips rt USING (trip_id)
                GROUP BY st.trip_id
            ) ranked
            WHERE rn = 1
        )
        SELECT s.stop_name
        FROM {schema}.stop_times st
        JOIN longest_trip lt ON lt.trip_id = st.trip_id
        JOIN {schema}.stops s ON s.stop_id = st.stop_id
        ORDER BY st.stop_sequence
        """
    )

    params: Dict[str, Any] = {"route_id": route_id}
    if direction_id is not None:
        params["direction_id"] = direction_id

    def _run(q: Any, p: Dict[str, Any]) -> List[str]:
        with get_session() as db:
            rows = db.execute(q, p).all()
            return [str(row[0]) for row in rows]

    try:
        return await anyio.to_thread.run_sync(_run, query, params)
    except Exception:
        return []


async def _load_arrival_documents(
    r: redis.Redis,
    stop_ids: List[str],
    horizon_sec: int,
    per_stop_limit: int,
) -> Tuple[Dict[str, List[JSONDict]], int]:
    now_sec = _now_seconds()
    min_ts, max_ts = _arrival_window(now_sec, horizon_sec)
    prefix = settings.redis_key_prefix

    pipeline = r.pipeline()
    for stop_id in stop_ids:
        pipeline.zrangebyscore(
            f"{prefix}:stop:{stop_id}:arrivals",
            min_ts,
            max_ts,
            start=0,
            num=per_stop_limit,
            withscores=True,
        )

    results = await pipeline.execute()
    per_stop: Dict[str, List[JSONDict]] = {}
    for stop_id, rows in zip(stop_ids, results):
        per_stop[stop_id] = _deserialize_rows(rows or [], now_sec, per_stop_limit)

    return per_stop, now_sec


async def _trip_route_map_for_groups(groups: Dict[str, List[JSONDict]]) -> Dict[str, str]:
    trip_ids: Set[str] = set()
    for docs in groups.values():
        trip_ids.update(_trip_ids_from_docs(docs))
    if not trip_ids:
        return {}
    return await _fetch_trip_route_map(trip_ids)


async def _load_vehicle_documents(r: redis.Redis) -> List[JSONDict]:
    prefix = settings.redis_key_prefix
    vehicle_ids = await r.smembers(f"{prefix}:vehicles:all")

    if not vehicle_ids:
        return []

    pipeline = r.pipeline()
    for raw_id in vehicle_ids:
        vehicle_id = _ensure_str(raw_id)
        if not vehicle_id:
            continue
        pipeline.get(f"{prefix}:vehicle:{vehicle_id}")

    payloads = await pipeline.execute()
    documents: List[JSONDict] = []
    for payload in payloads:
        doc = _decode_json_bytes(payload)
        if doc:
            documents.append(doc)

    return documents


async def _build_route_stops_map(route_ids: Set[str]) -> Dict[str, List[str]]:
    tasks = {
        route_id: asyncio.create_task(_fetch_representative_trip_stop_names(route_id))
        for route_id in route_ids
    }
    stops_map: Dict[str, List[str]] = {}
    for route_id, task in tasks.items():
        try:
            stops_map[route_id] = await task
        except Exception:
            stops_map[route_id] = []
    return stops_map


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

async def get_health(r: redis.Redis) -> Dict[str, Any]:
    """Return Redis health information and vehicle position staleness."""
    ping = await r.ping()
    stale = await _is_feed_stale(
        r,
        f"{settings.redis_key_prefix}:vehicle_positions:raw",
        settings.vehicle_positions_staleness_s,
    )
    return {"ok": ping is True, "vehicle_positions_stale": stale}


async def get_stop_arrivals(
    r: redis.Redis,
    stop_id: str,
    limit: int,
    horizon_sec: int,
) -> Tuple[List[ArrivalItem], bool]:
    """Return arrivals for a single stop along with staleness info."""
    per_stop_docs, _ = await _load_arrival_documents(r, [stop_id], horizon_sec, limit)
    docs = per_stop_docs.get(stop_id, [])
    trip_map = await _trip_route_map_for_groups({stop_id: docs})

    arrivals: List[ArrivalItem] = []
    for doc in docs:
        route_id = _route_id_for_doc(doc, trip_map)
        if not route_id:
            continue
        arrivals.append(_build_arrival_item(doc, route_id))

    prefix = settings.redis_key_prefix
    stale = await _is_feed_stale(
        r,
        f"{prefix}:trip_updates:raw",
        settings.trip_updates_staleness_s,
    )
    return arrivals, stale


async def get_route_vehicles(
    r: redis.Redis,
    route_id: str,
) -> Tuple[List[Vehicle], bool]:
    """Return vehicles for a given route along with staleness info."""
    vehicles_raw = await _load_vehicle_documents(r)
    trip_map = await _fetch_trip_route_map(_trip_ids_from_docs(vehicles_raw))

    vehicles: List[Vehicle] = []
    for doc in vehicles_raw:
        mapped_route_id = _route_id_for_doc(doc, trip_map)
        if mapped_route_id != route_id:
            continue
        vehicle = _build_vehicle(doc, mapped_route_id)
        if vehicle:
            vehicles.append(vehicle)

    prefix = settings.redis_key_prefix
    stale = await _is_feed_stale(
        r,
        f"{prefix}:vehicle_positions:raw",
        settings.vehicle_positions_staleness_s,
    )
    return vehicles, stale


async def get_vehicle(r: redis.Redis, vehicle_id: str) -> Vehicle | None:
    """Return a single vehicle enriched with its route, if available."""
    prefix = settings.redis_key_prefix
    payload = await r.get(f"{prefix}:vehicle:{vehicle_id}")
    doc = _decode_json_bytes(payload)
    if not doc:
        return None

    trip_id = _ensure_str(doc.get("trip_id"))
    route_id: Optional[str] = None
    if trip_id:
        trip_map = await _fetch_trip_route_map({trip_id})
        route_id = trip_map.get(trip_id)

    return _build_vehicle(doc, route_id)


async def get_alerts(r: redis.Redis) -> AlertsResponse:
    """Return cached system alerts or an empty placeholder response."""
    prefix = settings.redis_key_prefix
    payload = await r.get(f"{prefix}:alerts")
    doc = _decode_json_bytes(payload)
    if doc is None:
        return AlertsResponse(as_of=_now_seconds(), alerts=[])

    as_of = _coerce_int(doc.get("as_of")) or _now_seconds()
    alerts = doc.get("alerts")
    alerts_list = alerts if isinstance(alerts, list) else []
    return AlertsResponse(as_of=as_of, alerts=alerts_list)


async def get_active_routes(r: redis.Redis) -> List[ActiveRoute]:
    """Return metadata for routes that currently have active vehicles."""
    vehicles_raw = await _load_vehicle_documents(r)
    if not vehicles_raw:
        return []

    trip_map = await _fetch_trip_route_map(_trip_ids_from_docs(vehicles_raw))
    route_counts: Counter[str] = Counter()
    for doc in vehicles_raw:
        route_id = _route_id_for_doc(doc, trip_map)
        if route_id:
            route_counts[route_id] += 1

    if not route_counts:
        return []

    active_route_ids = set(route_counts.keys())
    routes_meta, stops_map = await asyncio.gather(
        _fetch_routes_metadata(active_route_ids),
        _build_route_stops_map(active_route_ids),
    )

    routes: List[ActiveRoute] = []
    for route_id in sorted(active_route_ids):
        meta = routes_meta.get(route_id) or _default_route_meta(route_id)
        routes.append(
            ActiveRoute(
                id=route_id,
                name=meta.get("route_long_name") or route_id,
                color=_sanitize_color(meta.get("route_color")),
                stops=stops_map.get(route_id, []),
                active_vehicle_count=int(route_counts[route_id]),
            )
        )

    return routes


async def get_arrivals_widget(
    r: redis.Redis,
    stop_ids: List[str],
    horizon_sec: int = 45 * 60,
    per_stop_limit: int = 30,
) -> List[WidgetStop]:
    """Return widget-ready arrivals for multiple stops."""
    per_stop_docs, _ = await _load_arrival_documents(r, stop_ids, horizon_sec, per_stop_limit)
    trip_map = await _trip_route_map_for_groups(per_stop_docs)

    route_ids: Set[str] = set()
    for docs in per_stop_docs.values():
        for doc in docs:
            mapped_route = _route_id_for_doc(doc, trip_map)
            if mapped_route:
                route_ids.add(mapped_route)

    routes_meta_task = asyncio.create_task(_fetch_routes_metadata(route_ids))
    stop_names_task = asyncio.create_task(_fetch_stop_names(set(stop_ids)))
    routes_meta, stop_names = await asyncio.gather(routes_meta_task, stop_names_task)

    stops: List[WidgetStop] = []
    for stop_id in stop_ids:
        arrivals: List[WidgetArrival] = []
        for doc in per_stop_docs.get(stop_id, []):
            route_id = _route_id_for_doc(doc, trip_map)
            if not route_id:
                continue
            route_meta = routes_meta.get(route_id) or _default_route_meta(route_id)
            arrivals.append(_build_widget_arrival(doc, route_meta))

        stops.append(
            WidgetStop(
                stop_id=stop_id,
                stop_name=stop_names.get(stop_id, ""),
                arrivals=arrivals,
            )
        )

    return stops
