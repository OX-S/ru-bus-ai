from __future__ import annotations
from config import settings
from gtfs_loader import nightly_rebuild
from build_route_index import build_route_index
from build_semantic_index import build_semantic_index

def main():
    print("=== Rutgers GTFS nightly refresh ===")
    nightly_rebuild()
    if settings.build_faiss:
        print("=== Building route FAISS index ===")
        build_route_index()
        print("=== Building semantic FAISS index ===")
        build_semantic_index()
    print("=== Done ===")

if __name__ == "__main__":
    main()
