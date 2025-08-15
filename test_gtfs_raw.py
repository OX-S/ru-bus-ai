#!/usr/bin/env python3
"""
gtfs_rt_raw_dump.py — Fetch and dump a GTFS-realtime .pb feed in several raw-ish formats.

Setup:
  pip install requests gtfs-realtime-bindings protobuf
"""

# =========================
# 🔧 CONFIG — EDIT THESE
# =========================
SOURCE = "https://passio3.com/rutgers/passioTransit/gtfs/realtime/tripUpdates.pb"  # URL or local path to .pb

# What to output
PRINT_SUMMARY      = True     # quick counts & a few samples
PRINT_TEXTPROTO    = True     # full text-format (protobuf debug) to stdout
PRINT_HEXDUMP      = False    # hex dump of first bytes to stdout
WRITE_JSON_FULL    = True     # write full JSON to disk
JSON_OUT_PATH      = "feed_full_tripUpdates.json"

# Optional: save the raw bytes to a file for later inspection
SAVE_RAW_TO        = None     # e.g. "raw.pb" or None

# HTTP options (only used when SOURCE is http/https)
REQUEST_TIMEOUT    = 30
VERIFY_TLS         = True
REQUEST_HEADERS    = {
    "Accept": "application/x-protobuf, application/octet-stream, */*",
    "User-Agent": "gtfs-rt-raw-dump/1.0",
    # "Authorization": "Bearer <TOKEN>",
}
HTTP_PARAMS        = {
    # e.g. "key": "API_KEY"
}
HTTP_AUTH          = None     # ("user", "pass") for basic auth, else None
# =========================

import sys
import json
import binascii
from datetime import datetime, timezone

import requests
from google.protobuf.message import DecodeError
from google.protobuf import text_format
from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2


def human_time(ts: int | None) -> str:
    if not ts:
        return "-"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return str(ts)


def load_bytes(source: str) -> bytes:
    if source.startswith(("http://", "https://")):
        r = requests.get(
            source,
            headers=REQUEST_HEADERS,
            params=HTTP_PARAMS,
            auth=HTTP_AUTH,
            timeout=REQUEST_TIMEOUT,
            verify=VERIFY_TLS,
        )
        r.raise_for_status()
        data = r.content
    else:
        with open(source, "rb") as f:
            data = f.read()

    # Gzip sniff (some servers serve gzipped .pb with wrong headers)
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


def hexdump_preview(b: bytes, n: int = 256) -> None:
    preview = b[:n]
    hexstr = binascii.hexlify(preview).decode("ascii")
    grouped = " ".join(hexstr[i:i+2] for i in range(0, len(hexstr), 2))
    print(f"--- HEXDUMP (first {len(preview)} bytes) ---")
    print(grouped)
    print("--- END HEXDUMP ---\n")


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

    n_trip = n_veh = n_alert = 0
    for e in feed.entity:
        n_trip  += e.HasField("trip_update")
        n_veh   += e.HasField("vehicle")
        n_alert += e.HasField("alert")
    print(f"Entities: total={len(feed.entity)}  trip_updates={n_trip}  vehicles={n_veh}  alerts={n_alert}\n")

    shown_t = shown_v = shown_a = 0
    for e in feed.entity:
        if e.HasField("trip_update") and shown_t < limit:
            tu = e.trip_update
            trip = tu.trip
            print("-- TripUpdate --")
            print(f"  entity_id: {e.id or '-'}")
            print(f"  trip_id:   {trip.trip_id or '-'}   route_id: {trip.route_id or '-'}   start_date: {trip.start_date or '-'}")
            print(f"  updated:   {human_time(getattr(tu, 'timestamp', None))}\n")
            shown_t += 1
        if e.HasField("vehicle") and shown_v < limit:
            v = e.vehicle
            trip = v.trip
            pos = v.position
            veh_id = v.vehicle.id if v.HasField("vehicle") and v.vehicle.id else "-"
            print("-- VehiclePosition --")
            print(f"  entity_id: {e.id or '-'}   vehicle_id: {veh_id}")
            print(f"  trip_id:   {trip.trip_id or '-'}   route_id: {trip.route_id or '-'}")
            print(f"  coords:    lat={getattr(pos, 'latitude', '-')} lon={getattr(pos, 'longitude', '-')} bearing={getattr(pos, 'bearing', '-')}")
            print(f"  timestamp: {human_time(getattr(v, 'timestamp', None))}\n")
            shown_v += 1
        if e.HasField("alert") and shown_a < limit:
            a = e.alert
            header = next((t.text for t in a.header_text.translation if getattr(t, "text", None)), "")
            print("-- Alert --")
            print(f"  entity_id: {e.id or '-'}")
            print(f"  cause/effect: {getattr(a, 'cause', '-')} / {getattr(a, 'effect', '-')}")
            if a.active_period:
                start = a.active_period[0].start
                end   = a.active_period[0].end if a.active_period[0].end else None
                print(f"  active:    {human_time(start)} -> {human_time(end)}")
            if header:
                print(f"  header:    {header[:200] + ('…' if len(header) > 200 else '')}")
            print()
            shown_a += 1


def dump_textproto(feed: gtfs_realtime_pb2.FeedMessage) -> None:
    # Full protobuf text-format dump (aka debug string) — shows exactly which fields are present.
    print("=== FULL TEXT-PROTO DUMP (protobuf text format) ===")
    print(text_format.MessageToString(feed))
    print("=== END TEXT-PROTO DUMP ===\n")


def write_full_json(feed: gtfs_realtime_pb2.FeedMessage, out_path: str) -> None:
    # JSON with original proto field names and enum names, including default values.
    data = MessageToDict(
        feed,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] Wrote JSON dump to {out_path}")


def main():
    # 1) get bytes
    try:
        raw = load_bytes(SOURCE)
    except requests.RequestException as e:
        sys.exit(f"[!] HTTP error: {e}")
    except FileNotFoundError:
        sys.exit(f"[!] File not found: {SOURCE}")

    if PRINT_HEXDUMP:
        hexdump_preview(raw, n=256)

    # 2) parse protobuf
    feed = parse_feed(raw)

    # 3) outputs
    if PRINT_SUMMARY:
        summarize(feed, limit=5)
        print()

    if PRINT_TEXTPROTO:
        dump_textproto(feed)

    if WRITE_JSON_FULL:
        try:
            write_full_json(feed, JSON_OUT_PATH)
            print('a')
        except Exception as e:
            sys.exit(f"[!] Failed to write JSON: {e}")


if __name__ == "__main__":
    main()
