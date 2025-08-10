from __future__ import annotations

import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings
from gtfs_queries import get_representative_routes, get_representative_trip_stops


def build_route_index():
    routes = get_representative_routes()
    records = []

    for route_id, short_name, long_name in routes:
        stops = get_representative_trip_stops(route_id=route_id)
        if not stops:
            continue
        ordered_stops = sorted(stops, key=lambda x: x[4])  # stop_sequence is int in DB
        stop_names = [s[1] for s in ordered_stops]
        title = short_name or long_name or str(route_id)
        doc = f"Route {route_id} ({title}): {long_name}. Ordered stops: " + " → ".join(stop_names) + "."
        records.append({"route_id": int(str(route_id)), "doc": doc})

    if not records:
        print("No routes found; skipping FAISS build.")
        return

    # embeddings
    model = SentenceTransformer(settings.sbert_model)
    texts = [r["doc"] for r in records]
    emb = model.encode(texts, show_progress_bar=True, batch_size=64, normalize_embeddings=True).astype("float32")

    # faiss
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    id_index = faiss.IndexIDMap2(index)
    ids = np.array([r["route_id"] for r in records], dtype="int64")
    id_index.add_with_ids(emb, ids)

    out_dir = settings.index_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    faiss_path = out_dir / "routes.faiss"
    meta_path  = out_dir / "routes_meta.json"

    faiss.write_index(id_index, str(faiss_path))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({str(r["route_id"]): r["doc"] for r in records}, f, ensure_ascii=False, indent=2)

    print(f"Created {faiss_path}  ({id_index.ntotal} routes)")
