# -------------------------------------------------------------------
# 0.  IMPORT YOUR HELPERS
# -------------------------------------------------------------------
from gtfs_utils import (       # ← or whatever module/filename they live in
    get_representative_routes,
    get_representative_trip_stops,
)
from nightly_gtfs_refresh import DB_PATH
import duckdb, faiss, orjson, pathlib, pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
INDEX_PATH   = PROJECT_ROOT / "routes.faiss"
ID_MAP_PATH  = PROJECT_ROOT / "routes_meta.json"

# ---------------------------------------------------------------
# 1.  FETCH DATA WITH YOUR EXISTING METHODS
# ---------------------------------------------------------------
routes = get_representative_routes(database_path=str(DB_PATH))
# Expected: list[tuple] with (route_id, route_short_name, route_long_name)

records = []          # will become a pandas-friendly list of dicts

for route in routes:
    route_id, short_name, long_name = route
    dir_id = 0

    # many Rutgers routes are bidirectional; index both if available
    # for dir_id in (0, 1):
    stops = get_representative_trip_stops(
        route_id=route_id,
        database_path=str(DB_PATH),
    )
    if not stops:          # some feeds have only dir 0 → skip missing dir 1
        continue

    ordered_stops = sorted(stops, key=lambda x: x[4])
    stop_names    = [s[1] for s in ordered_stops]

    doc = (
        f"Route {route_id}{f' (dir {dir_id})' if dir_id else ''} "
        f"({short_name or long_name}): {long_name}. "
        f"Ordered stops: " + " → ".join(stop_names) + "."
    )

    records.append({
        "route_id" : route_id if dir_id == 0 else int(f"{route_id}{dir_id}"),
            # ensure unique key for each direction (e.g. 371990, 371991)
        "doc"      : doc
    })

# Convert to DataFrame for the embedding block that follows
import pandas as pd
routes_df = pd.DataFrame.from_records(records)

# --------------------------- 2. Make "route-doc" strings ------------- #
# def make_doc(row) -> str:
#     stops_str = " → ".join(stop['stop_name'] for stop in row['ordered_stops'])
#     return (
#         f"Route {row.route_id} ({row.short}): {row.route_long_name}. "
#         f"Ordered stops: {stops_str}."
#     )
#
# routes_df["doc"] = routes_df.apply(make_doc, axis=1)

# --------------------------- 3. Embeddings --------------------------- #
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
embeddings = model.encode(
    routes_df["doc"].tolist(),
    show_progress_bar=True,
    batch_size=64,
    normalize_embeddings=True
).astype("float32")  # FAISS needs float32

# --------------------------- 4. Build FAISS -------------------------- #
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)             # cosine sim (because we normalized)
id_index = faiss.IndexIDMap2(index)        # lets us attach route_id’s as keys
id_index.add_with_ids(embeddings, routes_df["route_id"].astype("int64").values)
faiss.write_index(id_index, str(INDEX_PATH))

# store metadata -> easier to pop docs for RAG answers
with open(ID_MAP_PATH, "wb") as f:
    f.write(orjson.dumps(
        dict(zip(routes_df["route_id"].astype(str), routes_df["doc"])),
        option=orjson.OPT_INDENT_2
    ))

print(f"Created {INDEX_PATH}   ({id_index.ntotal} routes)")
