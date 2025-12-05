# Rutgers Bus LLM

Retrieval-augmented Rutgers transit assistant that fuses GTFS-rt streams, static GTFS snapshots, and curated semantic overlays to power a FastAPI backend plus React widgets.

## Highlights
- Real-time ML retrieval: FAISS indexes for both routes and stops/landmarks.
- Resilient data stack: DuckDB + Postgres + Redis keep static and live feeds aligned.
- LLM router with semantic grounding chooses when to answer vs surface widgets.
- Demo-ready UI: arrivals and active-route widgets showcase the API without notebooks.

## Data + ML flow (TL;DR)
- **Static refresh** (`nightly_gtfs_refresh.py`, `src/tasks/nightly_refresh.py`): download Rutgers GTFS, rebuild DuckDB/Postgres, and trigger FAISS builders when `BUILD_FAISS=true`.
- **Realtime ingest** (`data/ru-bus-gtfsrt/gtfs_rt_ingestor.py`): aiohttp + protobuf parser with Redis distributed lock, per-stop sorted sets, route-level vehicle maps, TTL staleness.
- **Route embeddings** (`build_route_index.py`): canonical stop sequences → SBERT embeddings (all-MiniLM-L6-v2) → cosine FAISS ID map + doc metadata.
- **Semantic embeddings** (`src/tasks/build_semantic_index.py`): merge live GTFS stops with `data/semantic/semantic_knowledge.json`, build stop/landmark docs, encode, persist FAISS + metadata for `semantic_search.py`.
- **LLM routing** (`src/app/services/llm_router.py`): semantic hits enrich prompts, model must emit JSON selecting `chat_message`, `bus_arrivals`, or `active_routes`; fallback stop IDs applied when missing.

## Running it locally
1. **Install deps**
   ```bash
   python -m venv .venv && source .venv/bin/activate  # .\.venv\Scripts\activate on Windows
   pip install -U pip fastapi uvicorn[standard] redis sentence-transformers faiss-cpu duckdb psycopg[binary] sqlalchemy orjson requests tqdm anyio pydantic-settings
   cd ui/rutgers-bus-gpt && npm install && cd -
   ```
2. **Infra**: Postgres with Rutgers GTFS schema + Redis (or `docker compose up` under `data/ru-bus-gtfsrt`).
3. **Bootstrap data**
   ```bash
   python src/tasks/nightly_refresh.py
   cd data/ru-bus-gtfsrt && python gtfs_rt_ingestor.py
   ```
4. **Serve**
   ```bash
   uvicorn src.app.main:app --reload
   cd ui/rutgers-bus-gpt && npm run dev
   ```

## Repository map
```
.
|- src/app                # FastAPI API/services/schemas
|- src/tasks              # GTFS refresh + FAISS builders
|- data/ru-bus-gtfsrt     # Redis + GTFS-rt worker
|- data/semantic          # Curated overlays
|- ui/rutgers-bus-gpt     # React widgets
|- routes.faiss / routes_meta.json
`- data/index/semantic.faiss / semantic_meta.json
```

## Recruiter soundbites
- Built ingestion -> embeddings -> LLM routing with measurable staleness/latency checks.
- Added semantic overlays so embeddings reflect Rutgers slang and landmarks.
- Delivered Redis-backed FastAPI + demo UI so the system can be evaluated in seconds.
