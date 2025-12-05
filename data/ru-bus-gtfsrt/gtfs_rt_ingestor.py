import asyncio
import os
import time
import uuid
import logging
from typing import Optional, Dict, Any, List, Tuple

import aiohttp
import redis.asyncio as redis
from pydantic import BaseModel
from dotenv import load_dotenv

import orjson

from google.transit import gtfs_realtime_pb2

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def jdump(obj) -> bytes:
    return orjson.dumps(obj)

def jload(b: bytes):
    return orjson.loads(b)

class Settings(BaseModel):
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    VEHICLE_POSITIONS_URL: Optional[str] = os.getenv("VEHICLE_POSITIONS_URL")
    TRIP_UPDATES_URL: Optional[str] = os.getenv("TRIP_UPDATES_URL")
    ALERTS_URL: Optional[str] = os.getenv("ALERTS_URL")
    REFRESH_SECONDS: int = int(os.getenv("REFRESH_SECONDS", "15"))
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX", "gtfsrt")
    LOCK_KEY: str = os.getenv("LOCK_KEY", "gtfsrt:ingestor:lock")
    LOCK_TTL_SECONDS: int = int(os.getenv("LOCK_TTL_SECONDS", "45"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
    USER_AGENT: str = os.getenv("USER_AGENT", "RU-Bus-LLM-GTFSrt-Ingestor/1.0")
    VERIFY_TLS: bool = os.getenv("VERIFY_TLS", "true").lower() == "true"

S = Settings()

class FeedHTTPState:
    def __init__(self):
        self.etag: Optional[str] = None
        self.last_modified: Optional[str] = None

async def acquire_lock(r: redis.Redis, key: str, ttl: int, token: str) -> bool:
    return await r.set(key, token, nx=True, ex=ttl) is True

async def refresh_lock(r: redis.Redis, key: str, ttl: int, token: str) -> bool:
    val = await r.get(key)
    if val and val.decode("utf-8") == token:
        return await r.expire(key, ttl)
    return False

def now_ms() -> int:
    return int(time.time() * 1000)

async def fetch_feed(session: aiohttp.ClientSession, url: str, state: FeedHTTPState) -> Optional[bytes]:
    headers = {"User-Agent": S.USER_AGENT}
    if state.etag:
        headers["If-None-Match"] = state.etag
    if state.last_modified:
        headers["If-Modified-Since"] = state.last_modified

    try:
        timeout = aiohttp.ClientTimeout(total=S.REQUEST_TIMEOUT_SECONDS)
        async with session.get(url, headers=headers, timeout=timeout, ssl=S.VERIFY_TLS) as resp:
            if resp.status == 304:
                logging.debug(f"{url} not modified (304)")
                return None
            resp.raise_for_status()
            state.etag = resp.headers.get("ETag") or state.etag
            state.last_modified = resp.headers.get("Last-Modified") or state.last_modified
            data = await resp.read()
            logging.info(f"Fetched {url} [{len(data)} bytes]")
            return data
    except Exception as e:
        logging.warning(f"Fetch failed for {url}: {e}")
        return None

async def store_raw(r: redis.Redis, key: str, blob: bytes, ttl: int = 60):
    p = r.pipeline()
    p.set(key, blob)
    p.pexpire(key, ttl * 1000)
    await p.execute()

# ----------------------------
# VehiclePositions processor (no mapping, no label fallback)
# ----------------------------
async def process_vehicle_positions(r: redis.Redis, blob: bytes):
    prefix = S.REDIS_KEY_PREFIX
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(blob)

    route_to_vehicle_ids: Dict[str, List[str]] = {}
    all_vehicle_ids: List[str] = []
    ts_ms = now_ms()

    p = r.pipeline()
    total = 0
    with_route = 0

    for ent in feed.entity:
        if not ent.HasField("vehicle"):
            continue
        total += 1
        veh = ent.vehicle

        # vehicle_id
        vehicle_id = (getattr(getattr(veh, "vehicle", None), "id", "") or ent.id or "").strip()
        if not vehicle_id:
            continue  # can't store without id

        # strictly from feed only
        trip_id = (veh.trip.trip_id or "").strip() if veh.HasField("trip") else ""
        route_id = (veh.trip.route_id or "").strip() if veh.HasField("trip") else ""

        pos = veh.position if veh.HasField("position") else None
        lat = getattr(pos, "latitude", None) if pos else None
        lon = getattr(pos, "longitude", None) if pos else None
        speed = getattr(pos, "speed", None) if pos else None
        bearing = getattr(pos, "bearing", None) if pos else None
        ts = getattr(veh, "timestamp", None)

        vehicle_doc = {
            "vehicle_id": vehicle_id,
            "trip_id": trip_id or None,
            "route_id": route_id or None,
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "bearing": bearing,
            "updated_at": ts or (ts_ms // 1000),
            "ingested_at_ms": ts_ms,
        }

        # Store per-vehicle
        p.set(f"{prefix}:vehicle:{vehicle_id}", jdump(vehicle_doc))
        p.expire(f"{prefix}:vehicle:{vehicle_id}", 120)
        all_vehicle_ids.append(vehicle_id)

        # Only maintain per-route set if route_id is present in the feed
        if route_id:
            with_route += 1
            route_to_vehicle_ids.setdefault(route_id, []).append(vehicle_id)

    # Global set
    gk = f"{prefix}:vehicles:all"
    p.delete(gk)
    if all_vehicle_ids:
        p.sadd(gk, *all_vehicle_ids)
    p.expire(gk, 60)

    # Per-route sets (feed-provided route_id only)
    for route_id, vids in route_to_vehicle_ids.items():
        k = f"{prefix}:route:{route_id}:vehicles"
        p.delete(k)
        if vids:
            p.sadd(k, *vids)
        p.expire(k, 60)

    await p.execute()
    logging.info(f"Vehicles total={total}, with_route={with_route}, routes={len(route_to_vehicle_ids)}")

# ----------------------------
# TripUpdates processor (no mapping)
# ----------------------------
async def process_trip_updates(r: redis.Redis, blob: bytes):
    # Key: {prefix}:stop:{stop_id}:arrivals (ZSET; member JSON has trip_id & route_id as-is from feed)
    # \"\"\"
    prefix = S.REDIS_KEY_PREFIX
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(blob)

    per_stop: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}

    for ent in feed.entity:
        if not ent.HasField("trip_update"):
            continue
        tu = ent.trip_update
        trip_id = tu.trip.trip_id if tu.trip else ""
        route_id = tu.trip.route_id if tu.trip else ""

        for stu in tu.stop_time_update:
            stop_id = stu.stop_id
            arrival = stu.arrival.time if stu.HasField("arrival") and hasattr(stu.arrival, "time") else None
            departure = stu.departure.time if stu.HasField("departure") and hasattr(stu.departure, "time") else None
            when = arrival or departure
            if not stop_id or not when:
                continue
            delay = None
            if stu.HasField("arrival") and hasattr(stu.arrival, "delay"):
                delay = stu.arrival.delay
            elif stu.HasField("departure") and hasattr(stu.departure, "delay"):
                delay = stu.departure.delay

            doc = {
                "trip_id": (trip_id or None),
                "route_id": (route_id or None),
                "stop_sequence": getattr(stu, "stop_sequence", None),
                "arrival": arrival,
                "departure": departure,
                "delay_s": delay,
            }
            per_stop.setdefault(stop_id, []).append((when, doc))

    p = r.pipeline()
    for stop_id, items in per_stop.items():
        key = f"{prefix}:stop:{stop_id}:arrivals"
        p.delete(key)
        items.sort(key=lambda x: x[0])
        if items:
            mapping = {}
            for when, doc in items:
                mapping[jdump(doc)] = when
            p.zadd(key, mapping)
        p.expire(key, 90)
    await p.execute()
    logging.info(f"Processed arrivals for {len(per_stop)} stops.")

# ----------------------------
# Alerts processor
# ----------------------------
async def process_alerts(r: redis.Redis, blob: bytes):
    prefix = S.REDIS_KEY_PREFIX
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(blob)

    alerts: List[Dict[str, Any]] = []
    for ent in feed.entity:
        if not ent.HasField("alert"):
            continue
        al = ent.alert
        effect = al.effect if hasattr(al, "effect") else None
        cause = al.cause if hasattr(al, "cause") else None
        active_periods = [
            {"start": p.start, "end": p.end} for p in getattr(al, "active_period", [])
        ]
        header = " ".join([t.text for t in getattr(al.header_text, "translation", [])]) if al.header_text else ""
        desc = " ".join([t.text for t in getattr(al.description_text, "translation", [])]) if al.description_text else ""
        informed = []
        for ie in getattr(al, "informed_entity", []):
            informed.append({
                "route_id": getattr(ie, "route_id", None),
                "stop_id": getattr(ie, "stop_id", None),
                "trip_id": getattr(ie, "trip", None) and getattr(ie.trip, "trip_id", None),
            })
        alerts.append({
            "id": ent.id,
            "effect": effect,
            "cause": cause,
            "active_period": active_periods,
            "header": header.strip(),
            "description": desc.strip(),
            "informed": informed,
        })

    key = f"{prefix}:alerts"
    await r.set(key, jdump({"alerts": alerts, "as_of": int(time.time())}))
    await r.expire(key, 300)
    logging.info(f"Processed {len(alerts)} alerts.")

# ----------------------------
# Main loop
# ----------------------------
async def run():
    r = redis.from_url(S.REDIS_URL, decode_responses=False)
    token = str(uuid.uuid4())

    http_states: Dict[str, FeedHTTPState] = {}
    for name in ["VEHICLE_POSITIONS_URL", "TRIP_UPDATES_URL", "ALERTS_URL"]:
        url = getattr(S, name)
        if url:
            http_states[name] = FeedHTTPState()

    if not http_states:
        logging.error("No feed URLs configured. Set VEHICLE_POSITIONS_URL and/or TRIP_UPDATES_URL/ALERTS_URL.")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            have_lock = await acquire_lock(r, S.LOCK_KEY, S.LOCK_TTL_SECONDS, token)
            if not have_lock:
                logging.debug("Another ingestor holds the lock. Sleeping...")
                await asyncio.sleep(S.REFRESH_SECONDS)
                continue

            await refresh_lock(r, S.LOCK_KEY, S.LOCK_TTL_SECONDS, token)

            try:
                if S.VEHICLE_POSITIONS_URL:
                    data = await fetch_feed(session, S.VEHICLE_POSITIONS_URL, http_states["VEHICLE_POSITIONS_URL"])
                    if data:
                        await store_raw(r, f"{S.REDIS_KEY_PREFIX}:vehicle_positions:raw", data, ttl=S.REFRESH_SECONDS*4)
                        await process_vehicle_positions(r, data)

                if S.TRIP_UPDATES_URL:
                    data = await fetch_feed(session, S.TRIP_UPDATES_URL, http_states["TRIP_UPDATES_URL"])
                    if data:
                        await store_raw(r, f"{S.REDIS_KEY_PREFIX}:trip_updates:raw", data, ttl=S.REFRESH_SECONDS*4)
                        await process_trip_updates(r, data)

                if S.ALERTS_URL:
                    data = await fetch_feed(session, S.ALERTS_URL, http_states["ALERTS_URL"])
                    if data:
                        await store_raw(r, f"{S.REDIS_KEY_PREFIX}:alerts:raw", data, ttl=S.REFRESH_SECONDS*8)
                        await process_alerts(r, data)

            except Exception as e:
                logging.exception(f"Ingest loop error: {e}")

            await refresh_lock(r, S.LOCK_KEY, S.LOCK_TTL_SECONDS, token)
            await asyncio.sleep(S.REFRESH_SECONDS)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
