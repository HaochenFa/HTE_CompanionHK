# Runtime & Provider Verification Checklist

Reproducible commands for validating LangGraph runtime selection, Exa retrieval, and dependency health during demos.

## 1. Basic Health

```bash
curl -s http://localhost:8000/api/health | python3 -m json.tool
```

Expected: `{ "status": "ok", "service": "companionhk-api" }`

## 2. Dependency Status

```bash
curl -s http://localhost:8000/api/health/dependencies | python3 -m json.tool
```

Verify: `db`, `redis`, `chat_provider`, `safety_provider`, `weather`, `maps`, `exa`, `voice`, `runtime` keys present.

## 3. Runtime Selection

```bash
curl -s http://localhost:8000/api/health/runtime | python3 -m json.tool
```

Check fields:

- `runtime`: should be `"langgraph"` when `FEATURE_LANGGRAPH_ENABLED=True`, otherwise `"simple"`.
- `langgraph_enabled` / `langgraph_available`: confirm library availability.
- `checkpointer_backend`: should be `"memory"` when LangGraph is active.
- `feature_flags`: all sponsor and provider flags.
- `libraries`: `langchain_core` and `langgraph` availability.

## 4. Exa Retrieval Probe

```bash
# Default query
curl -s "http://localhost:8000/api/health/exa-probe" | python3 -m json.tool

# Custom query
curl -s "http://localhost:8000/api/health/exa-probe?query=best+dim+sum" | python3 -m json.tool
```

Check fields:

- `provider`: `"exa"` when configured, `"retrieval-stub"` otherwise.
- `result_count`: should be > 0 on success.
- `latency_ms`: time for the retrieval call.
- `degraded`: `true` when provider is unavailable or no results.
- `fallback_reason`: explains degradation.

## 5. Toggle Verification

### LangGraph toggle

```bash
# With LangGraph enabled
FEATURE_LANGGRAPH_ENABLED=True python -m uvicorn app.main:app --port 8000 &
curl -s http://localhost:8000/api/health/runtime | python3 -m json.tool
# Expect runtime: "langgraph"

# Without LangGraph
FEATURE_LANGGRAPH_ENABLED=False python -m uvicorn app.main:app --port 8001 &
curl -s http://localhost:8001/api/health/runtime | python3 -m json.tool
# Expect runtime: "simple"
```

### Exa toggle

```bash
# With Exa enabled
FEATURE_EXA_ENABLED=True EXA_API_KEY=... curl -s "http://localhost:8000/api/health/exa-probe"
# Expect provider: "exa", result_count > 0

# Without Exa
FEATURE_EXA_ENABLED=False curl -s "http://localhost:8000/api/health/exa-probe"
# Expect provider: "retrieval-stub", degraded: true
```

## 6. Clear History Verification

```bash
# Clear companion history for user
curl -s -X DELETE http://localhost:8000/api/chat/companion/history \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo-user", "role": "companion"}' | python3 -m json.tool
```

Expected: `cleared_message_count`, `cleared_memory_count`, `cleared_recommendation_count`, and a fresh `new_thread_id`.

## 7. TTS Verification

```bash
curl -s -X POST http://localhost:8000/api/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Hong Kong", "language": "en", "preferred_provider": "auto"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'provider={d[\"provider\"]} audio_len={len(d[\"audio_base64\"])} degraded={d[\"degraded\"]}')"
```

## 8. Readiness Probe

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/ready
```

Expected: `200` when DB and Redis are up, `503` otherwise.
