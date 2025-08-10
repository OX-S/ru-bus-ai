from __future__ import annotations

import re
import requests
import zipfile
from pathlib import Path

import psycopg
from tqdm import tqdm

from config import settings

GTFS_FILES: list[str] = [
    "agency.txt", "stops.txt", "routes.txt", "trips.txt",
    "stop_times.txt", "calendar.txt", "calendar_dates.txt", "shapes.txt",
]

def _sanitize_col(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\W+", "_", s)
    s = re.sub(r"^(\d)", r"c_\1", s)
    return s.strip("_") or "col"

def _read_header(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8-sig") as f:
        line = f.readline().rstrip("\n\r")
    cols = [_sanitize_col(c.strip()) for c in line.split(",")]
    # dedupe
    seen = {}
    out = []
    for c in cols:
        n = seen.get(c, 0) + 1
        seen[c] = n
        out.append(c if n == 1 else f"{c}_{n}")
    return out

def download_gtfs_zip(url: str, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dst, "wb") as f, tqdm(total=total or None, unit="B", unit_scale=True, desc="download") as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
    return dst

def extract_zip(zip_path: Path, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    for old in target_dir.glob("*.txt"):
        old.unlink()
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(target_dir)

def _alter_to_int(cur: psycopg.Cursor, table: str, col: str):
    cur.execute(f"""
        ALTER TABLE {settings.gtfs_schema}."{table}"
        ALTER COLUMN "{col}" TYPE integer
        USING NULLIF("{col}", '')::integer
    """)

def _alter_to_date_yyyymmdd(cur: psycopg.Cursor, table: str, col: str):
    cur.execute(f"""
        ALTER TABLE {settings.gtfs_schema}."{table}"
        ALTER COLUMN "{col}" TYPE date
        USING CASE
            WHEN "{col}" ~ '^\d{{8}}$' THEN to_date("{col}", 'YYYYMMDD')
            WHEN "{col}" = '' THEN NULL
            
        END
    """)

def rebuild_postgres_from_dir(txt_dir: Path):
    dsn = settings.dsn()
    schema = settings.gtfs_schema

    with psycopg.connect(dsn, autocommit=True) as con:
        with con.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            db, usr = cur.fetchone()
            print(f"• Connected to DB={db} as {usr}")

            cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE;')
            cur.execute(f'CREATE SCHEMA "{schema}";')

            for fname in GTFS_FILES:
                csv_path = txt_dir / fname
                if not csv_path.exists():
                    print(f"  ! Skipping missing {fname}")
                    continue

                table = fname.replace(".txt", "")
                cols = _read_header(csv_path)
                col_defs = ", ".join(f'"{c}" text' for c in cols)
                cur.execute(f'CREATE TABLE "{schema}"."{table}" ({col_defs});')

                with open(csv_path, "rb") as f:
                    copy_sql = f'COPY "{schema}"."{table}" FROM STDIN WITH (FORMAT csv, HEADER true)'
                    with cur.copy(copy_sql) as cp:
                        while True:
                            chunk = f.read(1024 * 1024)
                            if not chunk:
                                break
                            cp.write(chunk)

                cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                n = cur.fetchone()[0]
                print(f"  • Loaded {fname} → {schema}.{table} ({n} rows)")

            print("• Typing critical columns…")
            for (tbl, col, fn) in [
                ("stop_times", "stop_sequence", _alter_to_int),
                ("shapes", "shape_pt_sequence", _alter_to_int),
                ("routes", "route_type", _alter_to_int),
            ]:
                try:
                    fn(cur, tbl, col)
                except Exception as e:
                    print(f"  ! Could not type {tbl}.{col}: {e}")

            for (tbl, col) in [("calendar", "start_date"),
                               ("calendar", "end_date"),
                               ("calendar_dates", "date")]:
                try:
                    _alter_to_date_yyyymmdd(cur, tbl, col)
                except Exception as e:
                    print(f"  ! Could not type {tbl}.{col}: {e}")

            print("• Creating indexes…")
            idx_sql = [
                f'CREATE INDEX IF NOT EXISTS gtfs_stops_stop_id_idx ON "{schema}"."stops" ("stop_id");',
                f'CREATE INDEX IF NOT EXISTS gtfs_routes_route_id_idx ON "{schema}"."routes" ("route_id");',
                f'CREATE INDEX IF NOT EXISTS gtfs_trips_trip_id_idx  ON "{schema}"."trips" ("trip_id");',
                f'CREATE INDEX IF NOT EXISTS gtfs_trips_route_id_idx ON "{schema}"."trips" ("route_id");',
                f'CREATE INDEX IF NOT EXISTS gtfs_stop_times_trip_seq_idx ON "{schema}"."stop_times" ("trip_id", "stop_sequence");',
                f'CREATE INDEX IF NOT EXISTS gtfs_calendar_service_id_idx ON "{schema}"."calendar" ("service_id");',
                f'CREATE INDEX IF NOT EXISTS gtfs_calendar_dates_idx    ON "{schema}"."calendar_dates" ("service_id", "date");',
                f'CREATE INDEX IF NOT EXISTS gtfs_shapes_id_seq_idx      ON "{schema}"."shapes" ("shape_id", "shape_pt_sequence");',
            ]
            for sql in idx_sql:
                try:
                    cur.execute(sql)
                except Exception as e:
                    print(f"  ! Index skipped: {e}")

            try:
                cur.execute(f'ANALYZE "{schema}"')
            except Exception as e:
                print(f"  ! ANALYZE skipped: {e}")

def nightly_rebuild():
    zip_path = settings.data_dir / "google_transit.zip"
    print("• Downloading GTFS …")
    download_gtfs_zip(settings.gtfs_url, zip_path)
    print("• Extracting …")
    extract_zip(zip_path, settings.data_dir)
    print("• Loading into Postgres …")
    rebuild_postgres_from_dir(settings.data_dir)
