# Rutgers Bus AI

Rutgers transit AI assistant that uses both static GTFS and GTFS-rt transit feeds, Redis Cache, Postgres DB, FAISS retrieval, and a Vite/React web app so students get grounded, conversational answers.

## What's inside
- **Retrieval-aware routing.** `src/app/services/llm_router.py` uses semantic hits plus a tight JSON schema to decide when to answer directly versus show the appropriate chat widget.
- **Dual FAISS indexes.** `build_route_index.py` and `src/tasks/build_semantic_index.py` create route documents and stop/landmark documents, letting the LLM ground on both the static GTFS feed and student nicknames before responding.
- **FastAPI services.** Redis caches from the GTFS-rt ingestor and Postgres queries are wrapped in typed modules like `transit_cache.py`, then exposed under `/api/v1`.
- **Full web experience.** `ui/rutgers-bus-gpt` is a Vite + React 19 + Tailwind site with routed pages.

## Data and ML flow
1. **Static refresh.** `nightly_gtfs_refresh.py` plus `src/tasks/nightly_refresh.py` download the Rutgers GTFS static feed, rebuild the Postgres `gtfs` schema, and kick off FAISS builders.
2. **Realtime ingest.** `data/ru-bus-gtfsrt/gtfs_rt_ingestor.py` runs with aiohttp, parses protobuf vehicle/trip feeds, coordinates with a Redis distributed lock, and writes normalized JSON plus sorted-set arrivals with TTL-based staleness checks.
3. **Route embeddings.** `build_route_index.py` stores each route's canonical stop order as vectors in a cosine FAISS ID map with JSON metadata for retrieval-augmented answers.
4. **Semantic knowledge.** `src/tasks/build_semantic_index.py` merges live GTFS stops with `data/semantic/semantic_knowledge.json` overlays so the system understands student slang and landmarks (think "the quads" or "Livi Plaza"). The combined docs are embedded once and queried via `semantic_search.py`.

## Running it locally
1. **Install dependencies**
   ```bash
   python -m venv .venv && source .venv/bin/activate  # .\.venv\Scripts\activate on Windows
   pip install -U pip fastapi uvicorn[standard] redis sentence-transformers faiss-cpu psycopg[binary] sqlalchemy orjson requests tqdm anyio pydantic-settings
   cd ui/rutgers-bus-gpt && npm install && cd -
   ```
2. **Provision infra** - Postgres with the Rutgers GTFS schema (see `src/tasks/config.py`) and Redis (`docker compose up` inside `data/ru-bus-gtfsrt` works).
3. **Bootstrap data**
   ```bash
   python src/tasks/nightly_refresh.py
   cd data/ru-bus-gtfsrt && python gtfs_rt_ingestor.py
   ```
4. **Serve the backend**
   ```bash
   uvicorn src.app.main:app --reload
   ```
5. **Launch the web app**
   ```bash
   cd ui/rutgers-bus-gpt
   npm run dev
   ```