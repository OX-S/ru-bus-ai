#!/usr/bin/env python
"""
Nightly GTFS refresh for Rutgers Passio feed.
• Downloads latest zip
• Rebuilds DuckDB from scratch
"""

import os, shutil, zipfile, tempfile, datetime, pathlib, requests, duckdb
from tqdm import tqdm                         # progress bar

URL          = "https://passio3.com/rutgers/passioTransit/gtfs/google_transit.zip"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR     = PROJECT_ROOT / "data"

ZIP_PATH     = PROJECT_ROOT / "google_transit.zip"   # ← store alongside data/
DB_PATH      = PROJECT_ROOT / "gtfs.duckdb"

GTFS_FILES = [               # GTFS spec core files you care about
    "agency.txt", "stops.txt", "routes.txt", "trips.txt",
    "stop_times.txt", "calendar.txt", "calendar_dates.txt",
    "shapes.txt"
]

def download_zip(url: str, dst: pathlib.Path) -> pathlib.Path:
    """Stream download to disk with progress bar."""
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dst, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
    return dst

def extract_zip(zip_path: pathlib.Path, target_dir: pathlib.Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    # delete only previous TXT payload
    for old in target_dir.glob("*.txt"):
        old.unlink()
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(target_dir)


def rebuild_duckdb(db_path: pathlib.Path, txt_dir: pathlib.Path):
    """Create fresh DB and load every GTFS *.txt"""
    if db_path.exists():
        db_path.unlink()            # start clean
    con = duckdb.connect(db_path)
    for fname in GTFS_FILES:
        table = fname.replace(".txt", "")
        csv_file = txt_dir / fname
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('{csv_file}', HEADER=TRUE)")
    con.close()

def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[{ts}] Starting Rutgers GTFS refresh…")

    DATA_DIR.mkdir(exist_ok=True)
    zip_path = DATA_DIR / "google_transit.zip"

    print("  • Downloading latest feed …")
    download_zip(URL, zip_path)

    print("  • Extracting …")
    extract_zip(zip_path, DATA_DIR)

    print("  • Rebuilding DuckDB …")
    rebuild_duckdb(DB_PATH, DATA_DIR)

    print(f"Done. Fresh DB at {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
