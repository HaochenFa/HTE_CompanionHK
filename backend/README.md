# CompanionHK Backend

FastAPI orchestration service for CompanionHK.

Current framework notes:

- `/chat` is role-aware and thread-aware (`role` + `thread_id`) for stateful session continuity.
- `/chat` now runs a smaller safety monitor flow (MiniMax + rules fallback) and returns enriched `safety` metadata.
- `/safety/evaluate` provides standalone risk/emotion scoring with the same monitor logic used by `/chat`.
- `/voice/tts` and `/voice/stt` expose voice provider orchestration with fallback.
- `/health/dependencies` and `/ready` provide dependency readiness checks for deployment probes.
- Runtime is feature-flagged:
  - `FEATURE_LANGGRAPH_ENABLED=false` -> `simple` runtime
  - `FEATURE_LANGGRAPH_ENABLED=true` -> LangGraph-capable runtime path
- Long-term memory strategy is controlled by:
  - `MEMORY_LONG_TERM_STRATEGY` (default: `hybrid_profile_retrieval`)
  - `MEMORY_RETRIEVAL_TOP_K`
- Persistence stack:
  - `SQLAlchemy 2.x` models + `Alembic` migrations,
  - `PostgreSQL` + `pgvector` for long-term memory and retrieval,
  - `Redis` for short-term role-scoped context windows.

Role contract:

- `role` values: `companion`, `local_guide`, `study_guide`
- thread continuity is scoped by (`user_id`, `role`, `thread_id`)

## Database Migrations

Run these commands from `backend/`:

- Create a migration:
  - `uv run alembic revision -m "describe change"`
- Apply latest schema:
  - `uv run alembic upgrade head`
- Roll back one migration:
  - `uv run alembic downgrade -1`

Initial schema migration is in `alembic/versions/8f327fc4442f_create_initial_schema.py`.
Detailed schema documentation: `../docs/architecture/database-schema.md`.

## Privacy Defaults

- Recommendation persistence does not store precise user current location by default.
- Coarse location metadata is stored for analytics/debugging (`user_location_geohash`, `user_location_region`).
- Precise recommended-place coordinates are stored for map and route UX.

## Health/Readiness Endpoints

- `GET /health`: liveness endpoint (process-level).
- `GET /health/dependencies`: returns per-dependency status (`db`, `redis`, providers).
- `GET /ready`: readiness endpoint for ECS/ALB probes.
  - returns `200` only when required dependencies (`db`, `redis`) are reachable,
  - returns `503` otherwise.

## Local Commands

### Option A: `venv` + `pip`

- Install:
  - `python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'`
- Run server:
  - `source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- Run tests:
  - `source .venv/bin/activate && pytest -q`

### Option B: `uv`

- Install/sync:
  - `uv sync --all-extras`
- Run server:
  - `uv run uvicorn app.main:app --reload --port 8000`
- Run tests:
  - `uv run pytest -q`

### Option C: `conda`

- Create/update environment:
  - `conda env create -f environment.yml || conda env update -f environment.yml --prune`
- Run server:
  - `conda run -n companionhk-backend uvicorn app.main:app --reload --port 8000`
- Run tests:
  - `conda run -n companionhk-backend pytest -q`
