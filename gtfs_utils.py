import duckdb

def get_representative_trip_stops(route_id, database_path='gtfs.duckdb', direction_id=0):
    con = duckdb.connect(database_path)

    query = """
        WITH route_trips AS (
            SELECT trip_id
            FROM   trips
            WHERE  route_id = ?
        ),
        longest_trip AS (
            SELECT trip_id
            FROM (
                SELECT
                    st.trip_id,
                    COUNT(*)                         AS stop_cnt,
                    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rn
                FROM   stop_times st
                JOIN   route_trips rt USING (trip_id)
                GROUP  BY st.trip_id
            ) ranked
            WHERE rn = 1         
        )
        SELECT
            s.stop_id,
            s.stop_name,
            s.stop_lat,
            s.stop_lon,
            st.stop_sequence
        FROM   stop_times  st
        JOIN   longest_trip lt  ON lt.trip_id = st.trip_id
        JOIN   stops        s   ON s.stop_id  = st.stop_id
        ORDER  BY st.stop_sequence;
    """

    result = con.execute(query, [route_id]).fetchall()
    con.close()
    return result


def get_representative_routes(database_path='gtfs.duckdb'):
    con = duckdb.connect(database_path)

    query = """
    SELECT route_id, route_short_name, route_long_name
    FROM routes
    ORDER BY route_short_name, route_long_name;
    """

    result = con.execute(query).fetchall()
    con.close()
    return result


if __name__ == "__main__":
    # stops = get_representative_trip_stops(route_id=41752)
    # for stop in stops:
    #     print(stop)

    routes = get_representative_routes()
    for route in routes:
        print(route)
