from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
import orjson
from sentence_transformers import SentenceTransformer

from src.app.core.config import settings

INDEX_PATH = settings.index_dir / "semantic.faiss"
META_PATH = settings.index_dir / "semantic_meta.json"


def _load_meta() -> Dict[str, Dict[str, Any]]:
    if not META_PATH.exists():
        return {}
    raw = orjson.loads(META_PATH.read_bytes())
    return {doc["doc_id"]: doc for doc in raw.get("documents", [])}


@lru_cache(maxsize=1)
def _meta_cache() -> Dict[str, Dict[str, Any]]:
    return _load_meta()


@lru_cache(maxsize=1)
def _index_cache() -> faiss.Index:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Semantic index missing at {INDEX_PATH}")
    return faiss.read_index(str(INDEX_PATH))


@lru_cache(maxsize=1)
def _model_cache() -> SentenceTransformer:
    return SentenceTransformer(settings.sbert_model)


def _embed_query(text: str) -> np.ndarray:
    model = _model_cache()
    embedding = model.encode([text], normalize_embeddings=True).astype("float32")
    return embedding


def search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search over stops/landmarks; returns docs with metadata."""
    if not query.strip():
        return []

    index = _index_cache()
    meta = _meta_cache()

    vec = _embed_query(query)
    scores, ids = index.search(vec, k)

    results: List[Dict[str, Any]] = []
    for score, doc_id in zip(scores[0], ids[0]):
        doc = meta.get(str(doc_id))
        if not doc:
            continue
        results.append(
            {
                "score": float(score),
                "doc_id": doc["doc_id"],
                "text": doc.get("text", ""),
                "metadata": doc.get("metadata", {}),
            }
        )
    return results

