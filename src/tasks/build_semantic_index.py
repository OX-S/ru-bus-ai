from __future__ import annotations

import numpy as np
import orjson
from typing import Any, Dict, List, Sequence, Tuple

import faiss
import psycopg
from sentence_transformers import SentenceTransformer

from config import settings
from src.app.schemas.semantic import (
    LandmarkSemanticInfo,
    SemanticIndexDocument,
    StopSemanticInfo,
    build_landmark_documents,
    build_stop_documents,
)

SEMANTIC_INDEX_PATH = settings.index_dir / "semantic.faiss"
SEMANTIC_META_PATH = settings.index_dir / "semantic_meta.json"
SEMANTIC_DATA_PATH = settings.repo_root / "data" / "semantic" / "semantic_knowledge.json"


def _connect() -> psycopg.Connection:
    return psycopg.connect(settings.dsn())


def _fetch_dynamic_stops() -> List[Dict[str, Any]]:
    sql = f"""
    SELECT
        s.stop_id,
        COALESCE(NULLIF(s.stop_name, ''), s.stop_id) AS stop_name,
        s.stop_lat,
        s.stop_lon,
        COALESCE(
            array_agg(DISTINCT r.route_id ORDER BY r.route_id),
            ARRAY[]::text[]
        ) AS routes_serving
    FROM "{settings.gtfs_schema}"."stops" s
    LEFT JOIN "{settings.gtfs_schema}"."stop_times" st ON st.stop_id = s.stop_id
    LEFT JOIN "{settings.gtfs_schema}"."trips" t ON t.trip_id = st.trip_id
    LEFT JOIN "{settings.gtfs_schema}"."routes" r ON r.route_id = t.route_id
    GROUP BY s.stop_id, s.stop_name, s.stop_lat, s.stop_lon
    ORDER BY s.stop_id;
    """
    with _connect() as con, con.cursor() as cur:
        cur.execute(sql)
        columns = [col.name for col in cur.description]
        rows = cur.fetchall()

    result: List[Dict[str, Any]] = []
    for row in rows:
        values: Dict[str, Any] = dict(zip(columns, row))
        routes = values.get("routes_serving") or []
        values["routes_serving"] = [r for r in routes if r]
        result.append(values)
    return result


def _load_semantic_overlay() -> Tuple[Dict[str, StopSemanticInfo], List[LandmarkSemanticInfo]]:
    if not SEMANTIC_DATA_PATH.exists():
        print(f"Semantic data file {SEMANTIC_DATA_PATH} not found; skipping overlays.")
        return {}, []

    raw = orjson.loads(SEMANTIC_DATA_PATH.read_bytes())
    stops = raw.get("stops", [])
    landmarks = raw.get("landmarks", [])

    stop_map: Dict[str, StopSemanticInfo] = {}
    for stop in stops:
        try:
            info = StopSemanticInfo(**stop)
        except Exception as exc:
            print(f"Warning: could not parse stop overlay {stop.get('stop_id')}: {exc}")
            continue
        stop_map[info.stop_id] = info

    landmark_items: List[LandmarkSemanticInfo] = []
    for landmark in landmarks:
        try:
            info = LandmarkSemanticInfo(**landmark)
        except Exception as exc:
            print(f"Warning: could not parse landmark {landmark.get('landmark_id')}: {exc}")
            continue
        landmark_items.append(info)

    return stop_map, landmark_items


def _merge_stops(
    dynamic_rows: Sequence[Dict[str, Any]],
    overlay_map: Dict[str, StopSemanticInfo],
) -> List[StopSemanticInfo]:
    merged: List[StopSemanticInfo] = []
    for row in dynamic_rows:
        stop_id = row["stop_id"]
        base_data: Dict[str, Any] = {
            "stop_id": stop_id,
            "official_name": row["stop_name"] or stop_id,
            "lat": float(row["stop_lat"]) if row["stop_lat"] is not None else None,
            "lon": float(row["stop_lon"]) if row["stop_lon"] is not None else None,
            "routes_serving": row["routes_serving"],
        }

        try:
            base = StopSemanticInfo(**base_data)
        except Exception as exc:
            print(f"Warning: skipped stop {stop_id} because base data invalid: {exc}")
            continue

        overlay = overlay_map.get(stop_id)
        if overlay:
            base = base.model_copy(
                update={
                    k: v
                    for k, v in overlay.model_dump(
                        exclude={"stop_id"},
                        exclude_none=True,
                    ).items()
                    if k != "stop_id"
                }
            )

        merged.append(base)
    return merged


def _build_semantic_documents() -> List[SemanticIndexDocument]:
    dynamic_rows = _fetch_dynamic_stops()
    overlay_map, landmarks = _load_semantic_overlay()
    stops = _merge_stops(dynamic_rows, overlay_map)
    stop_docs = build_stop_documents(stops)
    landmark_docs = build_landmark_documents(landmarks)
    return stop_docs + landmark_docs


def _embed_documents(documents: Sequence[SemanticIndexDocument]) -> np.ndarray:
    if not documents:
        return np.empty((0, 0), dtype="float32")

    model = SentenceTransformer(settings.sbert_model)
    embeddings = model.encode(
        [doc.text for doc in documents],
        show_progress_bar=True,
        batch_size=64,
        normalize_embeddings=True,
    ).astype("float32")
    return embeddings


def _write_index(
    documents: Sequence[SemanticIndexDocument],
    embeddings: np.ndarray,
) -> None:
    if not documents or embeddings.size == 0:
        print("No semantic documents to index.")
        return

    dim = len(embeddings[0])
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(SEMANTIC_INDEX_PATH))

    meta = [
        {
            "doc_id": doc.id,
            "text": doc.text,
            "metadata": doc.metadata,
        }
        for doc in documents
    ]
    SEMANTIC_META_PATH.write_bytes(orjson.dumps({"documents": meta}, option=orjson.OPT_INDENT_2))


def build_semantic_index() -> None:
    print("Building semantic FAISS index...")
    documents = _build_semantic_documents()
    embeddings = _embed_documents(documents)
    _write_index(documents, embeddings)
    print(f"Wrote {len(documents)} semantic documents to {SEMANTIC_INDEX_PATH}")


if __name__ == "__main__":
    build_semantic_index()
