import pandas as pd
from pathlib import Path
from collections import OrderedDict

GTFS_DIR = Path("data")   # change me!

# 1️⃣ load the four files we need
routes      = pd.read_csv(GTFS_DIR / "routes.txt")
trips       = pd.read_csv(GTFS_DIR / "trips.txt")
stop_times  = pd.read_csv(GTFS_DIR / "stop_times.txt")
stops       = pd.read_csv(GTFS_DIR / "stops.txt")

def stops_for_route(rid):
  # grab all trips on this route
  these_trips = trips[trips.route_id == rid]["trip_id"]
  # merge → stops, keep earliest stop_sequence seen for each stop
  combo = (stop_times[stop_times.trip_id.isin(these_trips)]
           .sort_values("stop_sequence")  # earliest first
           .drop_duplicates("stop_id"))
  return combo.merge(stops, on="stop_id") \
    .sort_values("stop_sequence")["stop_name"].tolist()


route_stop_lists = (
  routes[["route_id", "route_short_name", "route_long_name"]]
  .assign(ordered_stops=lambda df: df["route_id"].apply(stops_for_route))
)



ref = (
    stop_times.groupby("trip_id")["stop_id"].nunique()
              .reset_index(name="n_unique")
              .merge(trips[["trip_id","route_id","direction_id"]])
              .sort_values(["route_id","direction_id","n_unique"],
                           ascending=[True,True,False])
              .drop_duplicates(["route_id","direction_id"])
)

def ordered_stops_for(rid, did):
    # 1️⃣ reference trip
    ref_trip = ref.query("route_id==@rid & direction_id==@did")["trip_id"].iloc[0]
    spine = (stop_times.query("trip_id==@ref_trip")
                      .sort_values("stop_sequence")["stop_id"].tolist())

    # 2️⃣ iterate over the other trips
    for tid in trips.query("route_id==@rid & direction_id==@did")["trip_id"]:
        seq = (stop_times.query("trip_id==@tid")
                          .sort_values("stop_sequence")["stop_id"].tolist())
        # slide a two-stop window over this trip and make sure spine respects it
        for a, b in zip(seq, seq[1:]):
            if a in spine and b in spine:
                # already ordered correctly
                continue
            if a in spine and b not in spine:
                spine.insert(spine.index(a)+1, b)
            elif a not in spine and b in spine:
                spine.insert(spine.index(b), a)
            elif a not in spine and b not in spine:
                # both missing → append in observed order
                spine.append(a); spine.append(b)
    # dedupe while preserving order
    return list(OrderedDict.fromkeys(spine))

# build the table
route_dir_lists = []
for (rid, did) in trips[["route_id","direction_id"]].drop_duplicates().itertuples(index=False):
    route_dir_lists.append({
        "route_id": rid,
        "direction_id": did,
        "ordered_stops": ordered_stops_for(rid, did)
    })
route_dir_lists = pd.DataFrame(route_dir_lists) \
                   .merge(stops[["stop_id","stop_name"]], how="explode",
                          left_on="ordered_stops", right_on="stop_id") \
                   .groupby(["route_id","direction_id"]) \
                   .agg(ordered_stops=("stop_name", list)) \
                   .reset_index()

print(route_dir_lists.head(30).to_string())











