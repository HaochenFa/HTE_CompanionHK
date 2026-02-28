# CompanionHK Foundation Architecture

This document captures the foundational framework decisions and extension points.

## Layers

- Frontend (`frontend/`): Next.js App Router + TypeScript + MUI.
- Backend (`backend/`): FastAPI route boundary and orchestration runtime selector.
- Data (`infra/`): local PostgreSQL + Redis for development parity.
- Provider Adapters (`backend/app/providers/`): swap-friendly interfaces for sponsor integrations.
- Runtime (`backend/app/runtime/`): `simple` runtime today, LangGraph-capable runtime path behind feature flag.

## Request Path

1. User submits a chat message in frontend chat shell with `thread_id`.
2. Frontend calls backend `/chat`.
3. Backend route delegates to `ChatOrchestrator`.
4. Orchestrator resolves runtime (`simple` or `langgraph`) from feature flag.
5. Orchestrator resolves configured provider adapter (`mock` or `MiniMax` path).
6. Runtime executes generation and returns a normalized response payload.

## Extension Hooks

- Safety risk scoring hook (next slice).
- Short-term memory hook (`thread_id` + Redis/LangGraph checkpoints) (next slices).
- Long-term memory hook (hybrid profile + retrieval memory) (next slices).
- Recommendation orchestration hook (next slices).
- Voice adapter path with fallback (later slices).

## Feature Flag Rule

Provider activation and fallback decisions are controlled by environment flags, not hard-coded branching in route handlers.

## Memory Design Alignment

- Profile memory: durable user preferences/facts in Postgres.
- Retrieval memory: pgvector-backed semantic search for fuzzy recall and extra materials.
- Keep profile writes explicit and auditable; retrieval corpus can include optional external materials.
