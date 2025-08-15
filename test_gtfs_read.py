#!/usr/bin/env python3
"""
gtfs_rt_dump_constants.py — Fetch and pretty-print a GTFS-realtime .pb feed
with simple hard-coded settings.

Setup:
  pip install requests gtfs-realtime-bindings protobuf
"""

# =========================
# 🔧 CONFIG — EDIT THESE
# =========================
SOURCE = "https://passio3.com/rutgers/passioTransit/gtfs/realtime/tripUpdates.pb"  # URL or local path to .pb
LIMIT = 10                                           # examples per entity type to print
JSON_OUT = None                                     # e.g. "feed.json" or None to skip
SAVE_RAW_TO = None                                  # e.g. "raw.pb" to save bytes, else None

# HTTP options (only used when SOURCE is http/https)
REQUEST_TIMEOUT = 30
VERIFY_TLS = True
REQUEST_HEADERS = {
    "Accept": "application/x-protobuf, application/octet-stream, */*",
    "User-Agent": "gtfs-rt-dump/1.0",
    # "Authorization": "Bearer <TOKEN>",  # uncomment if needed
}
HTTP_PARAMS = {
    # e.g. "key": "API_KEY"
}
HTTP_AUTH = None  # set to ("username", "password") for basic auth, else None
# =========================


import io
import json
import sys
from datetime import datetime, timezone

import requests
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2


def human_time(ts: int | None) -> str:
    if not ts:
        return "-"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return str(ts)


def load_bytes(source: str) -> bytes:
    # If it's an HTTP(S) URL, fetch it; otherwise treat as local file path.
    if source.startswith(("http://", "https://")):
        resp = requests.get(
            source,
            headers=REQUEST_HEADERS,
            params=HTTP_PARAMS,
            auth=HTTP_AUTH,
            timeout=REQUEST_TIMEOUT,
            verify=VERIFY_TLS,
        )
        resp.raise_for_status()
        data = resp.content
    else:
        with open(source, "rb") as f:
            data = f.read()

    # Some servers gzip the protobuf but don't set headers. Sniff & decompress.
    if len(data) >= 2 and data[:2] == b"\x1f\x8b":
        import gzip
        try:
            data = gzip.decompress(data)
        except Exception:
            pass

    if SAVE_RAW_TO:
        try:
            with open(SAVE_RAW_TO, "wb") as f:
                f.write(data)
            print(f"[i] Saved raw bytes to {SAVE_RAW_TO}")
        except Exception as e:
            print(f"[!] Couldn't save raw bytes: {e}", file=sys.stderr)

    return data


def parse_feed(raw: bytes) -> gtfs_realtime_pb2.FeedMessage:
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(raw)
    except DecodeError as e:
        sys.exit(f"[!] Failed to parse protobuf: {e}")
    return feed


def summarize(feed: gtfs_realtime_pb2.FeedMessage, limit: int = 5) -> None:
    hdr = feed.header
    print("=== GTFS-realtime Feed ===")
    print(f"Version:   {hdr.gtfs_realtime_version or 'unknown'}")
    print(f"Timestamp: {human_time(hdr.timestamp)} (unix={hdr.timestamp or '-'})")
    inc = getattr(hdr, "incrementality", None)
    print(f"Incrementality: {inc if inc is not None else '-'}")
    print()

    # Count entities by type
    n_trip = n_veh = n_alert = 0
    for e in feed.entity:
        if e.HasField("trip_update"):
            n_trip += 1
        if e.HasField("vehicle"):
            n_veh += 1
        if e.HasField("alert"):
            n_alert += 1

    print(f"Entities: total={len(feed.entity)}  trip_updates={n_trip}  vehicles={n_veh}  alerts={n_alert}\n")

    shown_trip = shown_veh = shown_alert = 0

    for e in feed.entity:
        if e.HasField("trip_update") and shown_trip < limit:
            tu = e.trip_update
            trip = tu.trip
            print("-- TripUpdate --")
            print(f"  entity_id: {e.id or '-'}")
            print(f"  trip_id:   {trip.trip_id or '-'}   route_id: {trip.route_id or '-'}   start_date: {trip.start_date or '-'}")
            print(f"  updated:   {human_time(getattr(tu, 'timestamp', None))}")
            if tu.stop_time_update:
                stu = tu.stop_time_update[0]
                arr = getattr(stu.arrival, "time", None) if stu.HasField("arrival") else None
                dep = getattr(stu.departure, "time", None) if stu.HasField("departure") else None
                print(f"  first_stu: stop_id={stu.stop_id or '-'} arrival={human_time(arr)} departure={human_time(dep)}")
            print()
            shown_trip += 1
            continue

        if e.HasField("vehicle") and shown_veh < limit:
            v = e.vehicle
            pos = v.position
            veh_id = v.vehicle.id if v.HasField("vehicle") and v.vehicle.id else "-"
            print("-- VehiclePosition --")
            print(f"  entity_id:   {e.id or '-'}   vehicle_id: {veh_id}")
            print(f"  trip_id:     {v.trip.trip_id or '-'}   route_id: {v.trip.route_id or '-'}")
            lat = getattr(pos, "latitude", "-")
            lon = getattr(pos, "longitude", "-")
            bearing = getattr(pos, "bearing", "-")
            print(f"  coordinates: lat={lat} lon={lon} bearing={bearing}")
            status = getattr(v, "current_status", None)
            print(f"  current_stop: {getattr(v, 'stop_id', '-') }   status: {status if status is not None else '-'}")
            print(f"  timestamp:   {human_time(getattr(v, 'timestamp', None))}")
            print()
            shown_veh += 1
            continue

        if e.HasField("alert") and shown_alert < limit:
            a = e.alert
            header = ""
            if a.header_text.translation:
                for t in a.header_text.translation:
                    if getattr(t, "text", None):
                        header = t.text
                        break
            ap_start = human_time(a.active_period[0].start) if a.active_period else "-"
            ap_end = human_time(a.active_period[0].end) if a.active_period and a.active_period[0].end else "-"
            cause = getattr(a, "cause", None)
            effect = getattr(a, "effect", None)
            print("-- Alert --")
            print(f"  entity_id: {e.id or '-'}")
            print(f"  cause:     {cause if cause is not None else '-'}   effect: {effect if effect is not None else '-'}")
            print(f"  active:    {ap_start} -> {ap_end}")
            if header:
                print(f"  header:    {header[:200] + ('…' if len(header) > 200 else '')}")
            print()
            shown_alert += 1


def dump_json(feed: gtfs_realtime_pb2.FeedMessage, path: str) -> None:
    data = MessageToDict(
        feed,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # 1) fetch or read bytes
    try:
        raw = load_bytes(SOURCE)
    except requests.RequestException as e:
        sys.exit(f"[!] HTTP error fetching feed: {e}")
    except FileNotFoundError:
        sys.exit(f"[!] File not found: {SOURCE}")

    # 2) parse protobuf
    feed = parse_feed(raw)

    # 3) print summary
    summarize(feed, limit=LIMIT)

    # 4) optional JSON dump
    if JSON_OUT:
        try:
            dump_json(feed, JSON_OUT)
            print(f"[✓] Wrote full JSON to: {JSON_OUT}")
        except Exception as e:
            sys.exit(f"[!] Failed to write JSON: {e}")


if __name__ == "__main__":
    main()
