from __future__ import annotations
from typing import Sequence, Tuple, Optional
import psycopg
from config import settings

def _connect():
    return psycopg.connect(settings.dsn())

def get_representative_routes() -> Sequence[Tuple]:
    sql = f"""
    SELECT route_id, route_short_name, route_long_name
    FROM "{settings.gtfs_schema}".routes
    ORDER BY route_short_name NULLS LAST, route_long_name;
    """
    with _connect() as con, con.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_representative_trip_stops(route_id: str, *, direction_id: Optional[int] = None) -> Sequence[Tuple]:
    direction_clause = "AND direction_id = %s" if direction_id is not None else ""
    params = [route_id] + ([direction_id] if direction_id is not None else [])
    sql = f"""
    WITH route_trips AS (
        SELECT trip_id
        FROM "{settings.gtfs_schema}".trips
        WHERE route_id = %s
        {direction_clause}
    ),
    longest_trip AS (
        SELECT trip_id FROM (
            SELECT st.trip_id,
                   COUNT(*) AS stop_cnt,
                   ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, st.trip_id) AS rn
            FROM "{settings.gtfs_schema}".stop_times st
            JOIN route_trips rt USING (trip_id)
            GROUP BY st.trip_id
        ) ranked
        WHERE rn = 1
    )
    SELECT s.stop_id, s.stop_name, s.stop_lat, s.stop_lon, st.stop_sequence
    FROM "{settings.gtfs_schema}".stop_times st
    JOIN longest_trip lt ON lt.trip_id = st.trip_id
    JOIN "{settings.gtfs_schema}".stops s ON s.stop_id = st.stop_id
    ORDER BY st.stop_sequence;  -- integer now
    """
    with _connect() as con, con.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
