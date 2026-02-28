# CompanionHK Manual E2E Guide (Local Production Preview)

This guide helps contributors configure, test, and run CompanionHK locally in a production-like way before deploying online.

## Goal

- Validate the full stack locally (frontend + backend + Postgres + Redis).
- Catch configuration issues early (env vars, provider flags, API routing).
- Run both automated tests and manual E2E checks before deployment.

## 1) Prerequisites

- `Node.js` 20+ and `npm`
- `Python` 3.11+
- One Python workflow: `venv` (recommended), `uv`, or `conda`
- `Docker` + `docker compose`

Optional but recommended for richer Local Guide preview:

- `GOOGLE_MAPS_API_KEY` (backend places + routes)
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (frontend map canvas)

## 2) Configure Environment

From repo root:

```bash
cp .env.example .env
```

Edit `.env` as needed.

Minimum keys for baseline local preview:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- `BACKEND_HOST=0.0.0.0`
- `BACKEND_PORT=8000`
- `FRONTEND_ORIGIN=http://localhost:3000`
- `CHAT_PROVIDER=mock`
- `FEATURE_WEATHER_ENABLED=true`
- `FEATURE_GOOGLE_MAPS_ENABLED=true`

Notes:

- If Google Maps keys are empty, Local Guide still works with degraded fallback recommendations.
- Open-Meteo does not require an API key by default.

## 3) Start Local Infra (Postgres + Redis)

From repo root:

```bash
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
```

Expected: both `companionhk-postgres` and `companionhk-redis` show as running/healthy.

## 4) Apply Database Migrations

From repo root:

```bash
cd backend
uv run alembic upgrade head
cd ..
```

If you use `venv`/`conda`, activate that backend environment first and run:

```bash
cd backend
alembic upgrade head
cd ..
```

## 5) Install Dependencies

### Backend (choose one)

`venv`:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cd ..
```

`uv`:

```bash
cd backend
uv sync --all-extras
cd ..
```

`conda`:

```bash
cd backend
conda env create -f environment.yml || conda env update -f environment.yml --prune
cd ..
```

### Frontend

```bash
cd frontend
npm install
cd ..
```

## 6) Run Automated Tests (Pre-E2E Gate)

Backend:

- `venv`: `cd backend && source .venv/bin/activate && pytest -q`
- `uv`: `cd backend && uv run pytest -q`
- `conda`: `cd backend && conda run -n companionhk-backend pytest -q`

Frontend:

```bash
cd frontend && npm run test
```

If tests fail, fix them before manual E2E.

## 7) Run App Locally (Production-Like Preview)

Open two terminals.

Terminal A (backend, no reload):

- `venv`: `cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `uv`: `cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `conda`: `cd backend && conda run -n companionhk-backend uvicorn app.main:app --host 0.0.0.0 --port 8000`

Terminal B (frontend, production mode):

```bash
cd frontend
npm run build
npm run start
```

Open `http://localhost:3000` — you will land on the welcome page.

Quick API smoke checks:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/health
```

Expected:

- Both return healthy status payload.
- Routes work with and without `/api/` prefix.

## 8) Manual E2E Checklist

Use the UI at `http://localhost:3000`.

### A. Auth flow

1. You should land on `/welcome` (landing page).
2. Click "Get Started" to navigate to `/login`.
3. Enter a username and submit.
4. You should be redirected to `/` (role selection page).
5. Refresh the page — auth should persist (localStorage).

Expected:

- Unauthenticated users cannot access `/` or `/chat/*` routes.
- Login state persists across page refreshes.

### B. Multi-role chat continuity and separation

1. Select `Companion` role — navigates to `/chat/companion`.
2. Send: "I feel stressed after work."
3. Go back to role selection and select `Study Guide` — navigates to `/chat/study`.
4. Send: "Help me make a 3-day study plan for calculus."
5. Go back and select `Local Guide` — navigates to `/chat/guide`.
6. Send: "Recommend a quiet cafe in Central."
7. Navigate between role pages.

Expected:

- Each role keeps its own conversation history.
- Messages do not leak between roles.
- History hydrates correctly on role page revisit.

### C. Backend chat contract sanity

Run:

```bash
curl -s -X POST http://localhost:8000/chat/companion \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"manual-e2e-user",
    "thread_id":"manual-e2e-thread",
    "message":"hello"
  }'
```

Expected:

- Response includes `request_id`, `thread_id`, `reply`, and `safety` metadata.

### D. Image attachment in chat

1. In any chat role, click the attachment/image button.
2. Select a JPEG, PNG, or WebP image (under 5MB).
3. Send a message with the image attached.

Expected:

- Image preview appears in the sent message.
- Backend processes the image and returns a reply.
- No frontend errors.

### E. Local Guide recommendations + weather context

1. In `Local Guide` (`/chat/guide`), send a place-oriented request (e.g., "Outdoor walk near Tsim Sha Tsui").
2. Verify recommendation cards appear.
3. If Google Maps keys are configured, verify the map canvas renders with markers.

Expected:

- 3-5 recommendations are returned.
- Each recommendation includes rationale text.
- Distance/time hints appear when route data is available.
- Weather context is shown.

### F. Weather page

1. Navigate to `/weather`.

Expected:

- Current weather conditions display (temperature, condition).
- Weather-adaptive background renders.

### G. Safety banner

1. In any role, send a message expressing severe distress.

Expected:

- Crisis resources banner appears with Hong Kong hotlines.
- Banner is dismissible.
- Assistant responds with supportive, de-escalating language.

### H. Degraded fallback behavior (resilience check)

Temporarily set in `.env`:

- `FEATURE_WEATHER_ENABLED=false`
- `FEATURE_GOOGLE_MAPS_ENABLED=false`

Restart backend and repeat Local Guide request.

Expected:

- Chat remains usable.
- Recommendations still render with fallback content.
- No frontend crash.

### I. Optional live Google Maps canvas check

If both keys are set:

- `GOOGLE_MAPS_API_KEY`
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`

Expected:

- Map renders markers for recommended places.
- Recommendation links open the corresponding place in Google Maps.

### J. Voice TTS playback

1. In any chat, receive an assistant message.
2. Click the TTS (speaker) button on the message.

Expected:

- Audio plays back the assistant message.
- Provider selection works (auto, elevenlabs, cantoneseai).
- Loading and error states are handled.

## 9) Shutdown and Cleanup

Stop app servers with `Ctrl+C`, then:

```bash
docker compose -f infra/docker-compose.yml down
```

To remove local volumes too:

```bash
docker compose -f infra/docker-compose.yml down -v
```

## 10) Definition of Done Before Deploy

- Automated tests pass (`pytest -q`, `npm run test`).
- Manual checklist A-J passes (at minimum A-E and G).
- No critical console/backend runtime errors during E2E flow.
- Production-like local run (`npm run build && npm run start`) succeeds.
