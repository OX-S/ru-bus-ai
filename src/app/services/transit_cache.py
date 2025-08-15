# src/app/services/transit_cache.py
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Tuple, Set

import anyio
import redis.asyncio as redis
from sqlalchemy import text

from src.app.utils.json import jload
from src.app.core.config import settings
from src.app.db.session import get_session

# ---------- Internals ----------

async def _feed_staleness_ms(r: redis.Redis, raw_key: str, threshold_sec: int) -> bool:
    ttl = await r.ttl(raw_key)
    if ttl is None or ttl < 0:
        return True
    return ttl < max(1, threshold_sec // 4)

async def _trip_to_route_map_psql(trip_ids: Set[str]) -> Dict[str, str]:
    """Fetch trip_id -> route_id from static GTFS in Postgres.
    Any missing/NULL route_id entries are simply omitted.
    Runs in a worker thread to avoid blocking the event loop.
    """
    if not trip_ids:
        return {}

    schema = settings.gtfs_schema
    q = text(f"SELECT trip_id, route_id FROM {schema}.trips WHERE trip_id = ANY(:trip_ids)")

    def _run_query(ids: Set[str]) -> Dict[str, str]:
        # Run in a sync SQLAlchemy session
        with get_session() as db:
            rows = db.execute(q, {"trip_ids": list(ids)}).all()
            out: Dict[str, str] = {}
            for trip_id, route_id in rows:
                if route_id:
                    out[str(trip_id)] = str(route_id)
            return out

    return await anyio.to_thread.run_sync(_run_query, trip_ids)

# ---------- Public service funcs ----------

async def get_health(r: redis.Redis) -> Dict[str, Any]:
    ping = await r.ping()
    stale = await _feed_staleness_ms(
        r, f"{settings.redis_key_prefix}:vehicle_positions:raw", settings.vehicle_positions_staleness_s
    )
    return {"ok": ping is True, "vehicle_positions_stale": stale}

async def get_stop_arrivals(
    r: redis.Redis,
    stop_id: str,
    limit: int,
    horizon_sec: int,
) -> Tuple[List[Dict[str, Any]], bool]:
    now_sec = int(time.time())
    key = f"{settings.redis_key_prefix}:stop:{stop_id}:arrivals"
    min_t = now_sec - 3600
    max_t = now_sec + horizon_sec

    raw = await r.zrangebyscore(key, min_t, max_t, start=0, num=limit, withscores=True)

    # Build docs with ETA
    docs: List[Dict[str, Any]] = []
    trip_ids: Set[str] = set()
    for member_bytes, score in raw:
        try:
            doc = jload(member_bytes)
        except Exception:
            continue
        eta = max(0, int(score) - now_sec) if isinstance(score, (int, float)) else None
        doc = {**doc, "eta_seconds": eta}
        # collect trip ids for enrichment
        tid = doc.get("trip_id")
        if tid:
            trip_ids.add(str(tid))
        docs.append(doc)

    # Enrich route_id from Postgres; drop any arrivals whose trip_id does not resolve
    mapping = await _trip_to_route_map_psql(trip_ids)
    out: List[Dict[str, Any]] = []
    for d in docs:
        tid = d.get("trip_id")
        if not tid:
            # No trip_id → cannot map → ignore per user's instruction
            continue
        rid = mapping.get(str(tid))
        if not rid:
            # trip_id doesn't resolve to a route_id → ignore
            continue
        d["route_id"] = rid
        out.append(d)

    stale = await _feed_staleness_ms(
        r, f"{settings.redis_key_prefix}:trip_updates:raw", settings.trip_updates_staleness_s
    )
    return out, stale

async def get_route_vehicles(r: redis.Redis, route_id: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Return vehicles whose trip_id maps (via Postgres) to the requested route_id.
    We intentionally ignore vehicles whose trip_id does not resolve.
    """
    # Read all vehicles, then filter by DB mapping.
    # Rutgers fleet size is small, this is fine and avoids trusting possibly-wrong cache sets.
    all_set_key = f"{settings.redis_key_prefix}:vehicles:all"
    ids = await r.smembers(all_set_key)

    vehicles_raw: List[Dict[str, Any]] = []
    trip_ids: Set[str] = set()

    if ids:
        p = r.pipeline()
        for vid in ids:
            v = vid.decode("utf-8") if isinstance(vid, (bytes, bytearray)) else vid
            p.get(f"{settings.redis_key_prefix}:vehicle:{v}")
        vals = await p.execute()
        for val in vals:
            if not val:
                continue
            try:
                doc = jload(val)
            except Exception:
                continue
            vehicles_raw.append(doc)
            tid = doc.get("trip_id")
            if tid:
                trip_ids.add(str(tid))

    # Build trip -> route map and filter
    mapping = await _trip_to_route_map_psql(trip_ids)
    vehicles: List[Dict[str, Any]] = []
    for v in vehicles_raw:
        tid = v.get("trip_id")
        if not tid:
            continue
        rid = mapping.get(str(tid))
        if rid == route_id:
            v["route_id"] = rid  # normalize to DB route_id
            vehicles.append(v)

    stale = await _feed_staleness_ms(
        r, f"{settings.redis_key_prefix}:vehicle_positions:raw", settings.vehicle_positions_staleness_s
    )
    return vehicles, stale

async def get_vehicle(r: redis.Redis, vehicle_id: str) -> Dict[str, Any] | None:
    b = await r.get(f"{settings.redis_key_prefix}:vehicle:{vehicle_id}")
    if not b:
        return None
    doc = jload(b)

    # Enrich single vehicle's route_id from DB if possible
    tid = doc.get("trip_id")
    if tid:
        mapping = await _trip_to_route_map_psql({str(tid)})
        rid = mapping.get(str(tid))
        if rid:
            doc["route_id"] = rid
    return doc

async def get_alerts(r: redis.Redis) -> Dict[str, Any]:
    b = await r.get(f"{settings.redis_key_prefix}:alerts")
    if not b:
        return {"as_of": int(time.time()), "alerts": []}
    return jload(b)


async def _psql_trip_to_route(trip_ids: Set[str]) -> Dict[str, str]:
    """trip_id -> route_id from static GTFS. Always returns a dict."""
    if not trip_ids:
        return {}
    schema = settings.gtfs_schema
    q = text(f"SELECT trip_id, route_id FROM {schema}.trips WHERE trip_id = ANY(:ids)")

    def _run(ids: Set[str]) -> Dict[str, str]:
        with get_session() as db:
            rows = db.execute(q, {"ids": list(ids)}).all()
            return {str(t): str(r) for t, r in rows if r}

    try:
        return await asyncio.to_thread(_run, trip_ids)
    except Exception:
        # Optionally log here
        return {}

async def _psql_routes_meta(route_ids: Set[str]) -> Dict[str, Dict[str, Any]]:
    """route_id -> {route_long_name, route_color}; always returns a dict."""
    if not route_ids:
        return {}
    schema = settings.gtfs_schema
    q = text(
        f"SELECT route_id, route_long_name, route_color "
        f"FROM {schema}.routes WHERE route_id = ANY(:ids)"
    )

    def _run(ids: Set[str]) -> Dict[str, Dict[str, Any]]:
        with get_session() as db:
            rows = db.execute(q, {"ids": list(ids)}).all()
            out: Dict[str, Dict[str, Any]] = {}
            for rid, long_name, color in rows:
                hexcol = (color or "").strip()
                if hexcol and not hexcol.startswith("#"):
                    hexcol = f"#{hexcol}"
                out[str(rid)] = {
                    "route_long_name": long_name or "",
                    "route_color": hexcol or "#666666",
                }
            return out

    try:
        return await asyncio.to_thread(_run, route_ids)
    except Exception:
        return {}


async def _psql_stop_names(stop_ids: Set[str]) -> Dict[str, str]:
    """stop_id -> stop_name; always returns a dict."""
    if not stop_ids:
        return {}
    schema = settings.gtfs_schema
    q = text(f"SELECT stop_id, stop_name FROM {schema}.stops WHERE stop_id = ANY(:ids)")

    def _run(ids: Set[str]) -> Dict[str, str]:
        with get_session() as db:
            rows = db.execute(q, {"ids": list(ids)}).all()
            return {str(s): str(n) for s, n in rows}

    try:
        return await asyncio.to_thread(_run, stop_ids)
    except Exception:
        return {}

async def get_arrivals_widget(
    r: redis.Redis,
    stop_ids: list[str],
    horizon_sec: int = 45 * 60,
    per_stop_limit: int = 30,
) -> Dict[str, Dict[str, Any]]:
    """
    Returns arrivals for multiple stops enriched with static GTFS.

    Output per stop_id:
    {
      "stop_id": "...",
      "stop_name": "...",
      "arrivals": [
        { "eta_seconds": 120, "route_long_name": "...", "route_color": "#RRGGBB", "to": "TBD" }
      ]
    }

    Only include arrivals whose trip_id resolves to a route_id in Postgres.
    """
    now_sec = int(time.time())
    min_t = now_sec - 3600
    max_t = now_sec + horizon_sec
    prefix = settings.redis_key_prefix

    # 1) Fetch arrivals from Redis in bulk
    trips_to_map: Set[str] = set()
    per_stop_raw: Dict[str, list[Dict[str, Any]]] = {}
    pipe = r.pipeline()
    for sid in stop_ids:
        pipe.zrangebyscore(
            f"{prefix}:stop:{sid}:arrivals",
            min_t,
            max_t,
            start=0,
            num=per_stop_limit,
            withscores=True,
        )
    results = await pipe.execute()

    for sid, rows in zip(stop_ids, results):
        docs: list[Dict[str, Any]] = []
        for member_bytes, score in rows:
            try:
                doc = jload(member_bytes)
            except Exception:
                continue
            tid = doc.get("trip_id")
            if not tid:
                continue
            eta = max(0, int(score) - now_sec) if isinstance(score, (int, float)) else None
            doc["eta_seconds"] = eta
            trips_to_map.add(str(tid))
            docs.append(doc)

        docs.sort(key=lambda d: (d.get("eta_seconds") or 0))
        per_stop_raw[sid] = docs[:per_stop_limit]

    # 2) Enrich from Postgres (guard against None)
    t2r = await _psql_trip_to_route(trips_to_map) or {}

    needed_route_ids: Set[str] = set()
    for docs in per_stop_raw.values():
        for d in docs:
            rid = t2r.get(str(d.get("trip_id", "")))
            if rid:
                needed_route_ids.add(rid)

    routes_meta = await _psql_routes_meta(needed_route_ids) or {}
    stop_names = await _psql_stop_names(set(stop_ids)) or {}

    # 3) Build output (drop unmapped trips)
    out: Dict[str, Dict[str, Any]] = {}
    for sid in stop_ids:
        arrivals_out: list[Dict[str, Any]] = []
        for d in per_stop_raw.get(sid, []):
            rid = t2r.get(str(d.get("trip_id", "")))
            if not rid:
                continue
            meta = routes_meta.get(rid) or {"route_long_name": "", "route_color": "#666666"}
            arrivals_out.append({
                "eta_seconds": int(d.get("eta_seconds") or 0),
                "route_long_name": meta["route_long_name"],
                "route_color": meta["route_color"],
                "to": "TBD",
            })
        out[sid] = {
            "stop_id": sid,
            "stop_name": stop_names.get(sid, ""),
            "arrivals": arrivals_out,
        }
    return out
