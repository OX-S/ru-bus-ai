# Rutgers Bus LLM

A production-grade Rutgers transit assistant that pairs real-time GTFS feeds with retrieval-augmented generation. The system continuously ingests Rutgers vehicle positions, GTFS static schedules, and curated semantic knowledge, builds FAISS indexes, and exposes both an API (FastAPI) and a Vite/React UI.

## Why this project matters
- Real-time ML retrieval: FAISS indexes built from GTFS data + hand-curated semantics enable grounding for LLM responses.
- Distributed ingest: async GTFS-rt worker parses protobuf feeds and keeps Redis caches consistent via locks and TTLs.
- Typed FastAPI services: redis + Postgres backed APIs deliver widget-friendly payloads for arrivals, active routes, and alerts.
- Hybrid routing: semantic retrieval augments the LLM router so it can answer free text, trigger arrivals widgets, or summarize system status.
- Frontend playground: the UI showcases arrivals and route widgets to exercise the API and inspect router decisions.

## Data and ML pipelines
### Static GTFS snapshot
- `nightly_gtfs_refresh.py` downloads Rutgers Passio GTFS, extracts the core `.txt` files, and loads them into DuckDB for cheap analytical queries.
- `src/tasks/nightly_refresh.py` orchestrates a full refresh by rebuilding GTFS, then kicking off FAISS index builders when `BUILD_FAISS=true`.

### Real-time GTFS-rt ingestion
- `data/ru-bus-gtfsrt/gtfs_rt_ingestor.py` streams vehicle positions, trip updates, and alerts.
- Async aiohttp downloads with conditional requests (ETag/Last-Modified) and a Redis-based distributed lock prevent duplicate workers.
- Each feed is parsed with `gtfs-realtime` protos, normalized, and stored in Redis (per-stop sorted sets for arrivals, hash-style route/vehicle keys, TTL-based staleness signals).

### Route retrieval FAISS (`build_route_index.py`)
1. Query DuckDB via `gtfs_utils.get_representative_routes` and `get_representative_trip_stops` to get canonical stop sequences.
2. Render descriptive docs like `Route 41752 (A): ... Ordered stops ...`.
3. Embed docs with `SentenceTransformer('all-MiniLM-L6-v2')`, normalized for cosine similarity.
4. Persist to a FAISS `IndexIDMap2(IndexFlatIP)` keyed by `route_id`, plus a JSON metadata file for RAG answers.

### Semantic knowledge FAISS (`src/tasks/build_semantic_index.py`)
1. Pull live stop metadata + serving routes from Postgres (`gtfs` schema) so documents stay in sync.
2. Overlay curated annotations from `data/semantic/semantic_knowledge.json` (nicknames, landmarks, campus info).
3. Generate documents via `build_stop_documents` and `build_landmark_documents` (`src/app/schemas/semantic.py`).
4. Encode with the same SBERT model, build a FAISS cosine index, and store `semantic_meta.json` for downstream lookup.

### LLM routing + retrieval (`src/app/services/llm_router.py`)
- Semantic hits are resolved into enriched context strings (stop name, route list) by `transit_lookup` queries.
- Router prompts a chat-completions endpoint with a constrained JSON schema; the LLM chooses between `chat_message`, `bus_arrivals`, or `active_routes` widgets.
- If the LLM requests arrivals but omits stop IDs, the router falls back to the semantic hits discovered earlier.

## Backend services (FastAPI)
- `src/app/services/transit_cache.py` translates Redis payloads into typed models, de-duplicates trips, exposes staleness, and powers arrivals widgets + active route listings.
- `/api/v1/transit` serves arrivals, vehicle lookups, and system alerts.
- `/api/v1/widgets` assembles multi-stop arrival cards and active route summaries, guarding each call with a Postgres health check.
- Settings (`src/app/core/config.py`) rely on `.env`, enabling deployment-specific LLM endpoints, Redis URLs, and DB settings.

## Frontend (Vite + React)
- `ui/rutgers-bus-gpt` contains Tailwind-powered widgets (`ActiveRoutesWidget`, `BusArrivalsWidget`, etc.) used when iterating on the UX of chat responses.
- `npm run dev` launches the Vite dev server pointed at the FastAPI backend.

## Local development
1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -U pip fastapi uvicorn[standard] redis sentence-transformers faiss-cpu duckdb psycopg[binary] sqlalchemy orjson requests tqdm anyio pydantic-settings
   cd ui/rutgers-bus-gpt && npm install && cd -
   ```
2. **Provision infra**
   - Postgres with the Rutgers GTFS schema (`src/tasks/config.py` will build schemas).
   - Redis (or run `docker compose up` inside `data/ru-bus-gtfsrt`).
3. **Refresh static data + indexes**
   ```bash
   python src/tasks/nightly_refresh.py
   ```
4. **Start the GTFS-rt ingestor**
   ```bash
   cd data/ru-bus-gtfsrt
   python gtfs_rt_ingestor.py
   ```
5. **Run the API**
   ```bash
   uvicorn src.app.main:app --reload
   ```
6. **Launch the UI**
   ```bash
   cd ui/rutgers-bus-gpt
   npm run dev
   ```

## Automation + monitoring
- Re-run `src/tasks/nightly_refresh.py` nightly (cron/GitHub Actions) to keep static GTFS + embeddings fresh.
- Redis TTLs + `_is_feed_stale` in `transit_cache.py` expose staleness flags to the UI, so riders see when feeds fall behind.
- Lightweight scripts like `test_gtfs_read.py` exercise ingestion in CI.

## Repository layout
```
.
|- src/app                # FastAPI app (api, services, schemas, utils)
|- src/tasks              # Offline jobs (GTFS refresh, FAISS builders)
|- data/semantic          # Curated knowledge overlays
|- data/ru-bus-gtfsrt     # Redis + realtime ingestor tooling
|- ui/rutgers-bus-gpt     # React/Tailwind frontend playground
|- routes.faiss / routes_meta.json  # Route retrieval index artifacts
`- data/index/semantic.*  # Semantic FAISS artifacts
```

## Talking points for recruiters
- Built an end-to-end ML retrieval stack (ingestion -> embeddings -> LLM router) with measurable latency guarantees.
- Implemented semantic overlays that merge static GTFS facts with curated knowledge so SBERT embeddings reflect campus vernacular.
- Designed robust Redis caching for GTFS-rt with TTL-based staleness detection, distributed locks, and protobuf parsing at 15s cadence.
- Delivered typed FastAPI + React widgets so stakeholders can test retrieval quality without diving into notebooks.
