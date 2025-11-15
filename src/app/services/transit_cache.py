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
from src.app.utils.json import jload

JSONDict = Dict[str, Any]
DEFAULT_ROUTE_COLOR = "#666666"
_STALE_TTL_FRACTION = 4


# ---------------------------------------------------------------------------
# Helpers: general utilities
# ---------------------------------------------------------------------------

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
) -> Tuple[List[JSONDict], bool]:
    """Return arrivals for a single stop along with staleness info."""
    now_sec = int(time.time())
    prefix = settings.redis_key_prefix
    key = f"{prefix}:stop:{stop_id}:arrivals"
    min_timestamp = now_sec - 3600
    max_timestamp = now_sec + horizon_sec

    raw_entries = await r.zrangebyscore(
        key,
        min_timestamp,
        max_timestamp,
        start=0,
        num=limit,
        withscores=True,
    )

    documents: List[JSONDict] = []
    trip_ids: Set[str] = set()
    for payload, score in raw_entries:
        doc = _deserialize_arrival(payload, score, now_sec)
        if not doc:
            continue
        trip_id = doc.get("trip_id")
        if trip_id:
            trip_ids.add(str(trip_id))
        documents.append(doc)

    trip_map = await _fetch_trip_route_map(trip_ids)
    arrivals: List[JSONDict] = []
    for doc in documents:
        trip_id = doc.get("trip_id")
        if not trip_id:
            continue
        route_id = trip_map.get(str(trip_id))
        if not route_id:
            continue
        doc["route_id"] = route_id
        arrivals.append(doc)

    stale = await _is_feed_stale(
        r,
        f"{prefix}:trip_updates:raw",
        settings.trip_updates_staleness_s,
    )
    return arrivals, stale


async def get_route_vehicles(r: redis.Redis, route_id: str) -> Tuple[List[JSONDict], bool]:
    """Return vehicles for a given route along with staleness info."""
    prefix = settings.redis_key_prefix
    all_set_key = f"{prefix}:vehicles:all"
    ids = await r.smembers(all_set_key)

    vehicles_raw: List[JSONDict] = []
    trip_ids: Set[str] = set()

    if ids:
        pipeline = r.pipeline()
        for vid in ids:
            vehicle_id = vid.decode("utf-8") if isinstance(vid, (bytes, bytearray)) else vid
            pipeline.get(f"{prefix}:vehicle:{vehicle_id}")
        responses = await pipeline.execute()
        for payload in responses:
            doc = _decode_json_bytes(payload)
            if not doc:
                continue
            vehicles_raw.append(doc)
            trip_id = doc.get("trip_id")
            if trip_id:
                trip_ids.add(str(trip_id))

    trip_map = await _fetch_trip_route_map(trip_ids)
    vehicles: List[JSONDict] = []
    for vehicle in vehicles_raw:
        trip_id = vehicle.get("trip_id")
        if not trip_id:
            continue
        mapped_route_id = trip_map.get(str(trip_id))
        if mapped_route_id == route_id:
            vehicle["route_id"] = mapped_route_id
            vehicles.append(vehicle)

    stale = await _is_feed_stale(
        r,
        f"{prefix}:vehicle_positions:raw",
        settings.vehicle_positions_staleness_s,
    )
    return vehicles, stale


async def get_vehicle(r: redis.Redis, vehicle_id: str) -> JSONDict | None:
    """Return a single vehicle enriched with its route, if available."""
    prefix = settings.redis_key_prefix
    payload = await r.get(f"{prefix}:vehicle:{vehicle_id}")
    doc = _decode_json_bytes(payload)
    if not doc:
        return None

    trip_id = doc.get("trip_id")
    if trip_id:
        trip_map = await _fetch_trip_route_map({str(trip_id)})
        route_id = trip_map.get(str(trip_id))
        if route_id:
            doc["route_id"] = route_id
    return doc


async def get_alerts(r: redis.Redis) -> JSONDict:
    """Return cached system alerts or an empty placeholder response."""
    prefix = settings.redis_key_prefix
    payload = await r.get(f"{prefix}:alerts")
    doc = _decode_json_bytes(payload)
    if doc is None:
        return {"as_of": int(time.time()), "alerts": []}
    return doc


async def get_active_routes(r: redis.Redis) -> List[JSONDict]:
    """Return metadata for routes that currently have active vehicles."""
    prefix = settings.redis_key_prefix
    all_set_key = f"{prefix}:vehicles:all"
    vehicle_ids = await r.smembers(all_set_key)

    trip_ids: Set[str] = set()
    vehicle_trip_ids: List[str] = []

    if vehicle_ids:
        pipeline = r.pipeline()
        for raw_id in vehicle_ids:
            vehicle_id = raw_id.decode("utf-8") if isinstance(raw_id, (bytes, bytearray)) else str(raw_id)
            pipeline.get(f"{prefix}:vehicle:{vehicle_id}")

        payloads = await pipeline.execute()
        for payload in payloads:
            doc = _decode_json_bytes(payload)
            if not doc:
                continue
            trip_id = doc.get("trip_id")
            if not trip_id:
                continue
            trip_str = str(trip_id)
            trip_ids.add(trip_str)
            vehicle_trip_ids.append(trip_str)

    if not trip_ids:
        return []

    trip_map = await _fetch_trip_route_map(trip_ids)
    route_counts: Counter[str] = Counter()
    for trip_id in vehicle_trip_ids:
        route_id = trip_map.get(trip_id)
        if route_id:
            route_counts[route_id] += 1

    active_route_ids = set(route_counts.keys())
    if not active_route_ids:
        return []

    routes_meta = await _fetch_routes_metadata(active_route_ids)

    stops_map: Dict[str, List[str]] = {}
    for route_id in active_route_ids:
        stops_map[route_id] = await _fetch_representative_trip_stop_names(route_id)

    routes: List[JSONDict] = []
    for route_id in sorted(active_route_ids):
        meta = routes_meta.get(route_id) or {
            "route_long_name": route_id,
            "route_color": DEFAULT_ROUTE_COLOR,
        }
        raw_color = meta.get("route_color") or DEFAULT_ROUTE_COLOR
        color = raw_color.lstrip("#") or DEFAULT_ROUTE_COLOR.lstrip("#")
        routes.append(
            {
                "id": route_id,
                "name": meta.get("route_long_name") or route_id,
                "color": color,
                "stops": stops_map.get(route_id, []),
                "active_vehicle_count": int(route_counts[route_id]),
            }
        )

    return routes


async def get_arrivals_widget(
    r: redis.Redis,
    stop_ids: List[str],
    horizon_sec: int = 45 * 60,
    per_stop_limit: int = 30,
) -> Dict[str, JSONDict]:
    """Return widget-ready arrivals for multiple stops."""
    now_sec = int(time.time())
    prefix = settings.redis_key_prefix
    min_timestamp = now_sec - 3600
    max_timestamp = now_sec + horizon_sec

    trips_to_map: Set[str] = set()
    per_stop_docs: Dict[str, List[JSONDict]] = {}

    pipeline = r.pipeline()
    for stop_id in stop_ids:
        pipeline.zrangebyscore(
            f"{prefix}:stop:{stop_id}:arrivals",
            min_timestamp,
            max_timestamp,
            start=0,
            num=per_stop_limit,
            withscores=True,
        )
    results = await pipeline.execute()

    for stop_id, rows in zip(stop_ids, results):
        docs: List[JSONDict] = []
        for payload, score in rows:
            doc = _deserialize_arrival(payload, score, now_sec)
            if not doc:
                continue
            trip_id = doc.get("trip_id")
            if not trip_id:
                continue
            trips_to_map.add(str(trip_id))
            docs.append(doc)

        docs.sort(key=lambda item: item.get("eta_seconds", float("inf")))
        per_stop_docs[stop_id] = docs[:per_stop_limit]

    trip_map = await _fetch_trip_route_map(trips_to_map)

    needed_route_ids: Set[str] = set()
    for docs in per_stop_docs.values():
        for doc in docs:
            mapped_route = trip_map.get(str(doc.get("trip_id", "")))
            if mapped_route:
                needed_route_ids.add(mapped_route)

    routes_meta_task = asyncio.create_task(_fetch_routes_metadata(needed_route_ids))
    stop_names_task = asyncio.create_task(_fetch_stop_names(set(stop_ids)))
    routes_meta, stop_names = await asyncio.gather(routes_meta_task, stop_names_task)

    widget_payload: Dict[str, JSONDict] = {}
    for stop_id in stop_ids:
        arrivals_out: List[JSONDict] = []
        for doc in per_stop_docs.get(stop_id, []):
            trip_id = doc.get("trip_id")
            if not trip_id:
                continue
            route_id = trip_map.get(str(trip_id))
            if not route_id:
                continue
            route_meta = routes_meta.get(route_id) or {
                "route_long_name": "",
                "route_color": DEFAULT_ROUTE_COLOR,
            }
            arrivals_out.append(
                {
                    "eta_seconds": int(doc.get("eta_seconds") or 0),
                    "route_long_name": route_meta["route_long_name"],
                    "route_color": route_meta["route_color"],
                    "to": "TBD",
                }
            )

        widget_payload[stop_id] = {
            "stop_id": stop_id,
            "stop_name": stop_names.get(stop_id, ""),
            "arrivals": arrivals_out,
        }

    return widget_payload
