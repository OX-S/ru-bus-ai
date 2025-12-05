from __future__ import annotations

from typing import Dict, List, Optional

import psycopg

from src.app.core.config import settings


def _connect() -> psycopg.Connection:
    return psycopg.connect(settings.dsn())


def get_stop(stop_id: str) -> Optional[Dict[str, object]]:
    sql = f"""
    SELECT stop_id, stop_name, stop_lat, stop_lon
    FROM "{settings.gtfs_schema}".stops
    WHERE stop_id = %s
    """
    with _connect() as con, con.cursor() as cur:
        cur.execute(sql, (stop_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "stop_id": row[0],
            "name": row[1],
            "lat": row[2],
            "lon": row[3],
        }


def get_routes_for_stop(stop_id: str) -> List[Dict[str, object]]:
    sql = f"""
    SELECT DISTINCT r.route_id, r.route_short_name, r.route_long_name, r.route_color
    FROM "{settings.gtfs_schema}".stop_times st
    JOIN "{settings.gtfs_schema}".trips t ON t.trip_id = st.trip_id
    JOIN "{settings.gtfs_schema}".routes r ON r.route_id = t.route_id
    WHERE st.stop_id = %s
    ORDER BY r.route_short_name NULLS LAST, r.route_long_name, r.route_id
    """
    with _connect() as con, con.cursor() as cur:
        cur.execute(sql, (stop_id,))
        rows = cur.fetchall()
    routes: List[Dict[str, object]] = []
    for row in rows:
        routes.append(
            {
                "route_id": row[0],
                "short_name": row[1],
                "long_name": row[2],
                "color": row[3],
            }
        )
    return routes

