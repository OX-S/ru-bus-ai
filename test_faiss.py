import faiss, orjson, numpy as np
from sentence_transformers import SentenceTransformer

index     = faiss.read_index("routes.faiss")
meta      = orjson.loads(open("routes_meta.json","rb").read())
embedder  = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search_routes(query: str, top_k: int = 5):
    q_vec = embedder.encode([query], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(q_vec, top_k)
    results = []
    for route_id, score in zip(ids[0], scores[0]):
        if route_id == -1: continue
        results.append({"route_id": int(route_id),
                        "score": float(score),
                        "doc":  meta[str(route_id)]})
    return results

print(search_routes("Which routes go from the student activities center to the yard?"))
