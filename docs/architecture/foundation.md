# CompanionHK Foundation Architecture

This document captures the foundational framework decisions and extension points.

## Layers

- Frontend (`frontend/`): Next.js App Router + TypeScript + MUI.
- Backend (`backend/`): FastAPI route boundary and orchestration runtime selector.
- Data (`infra/`): local PostgreSQL + Redis for development parity.
- Provider Adapters (`backend/app/providers/`): swap-friendly interfaces for sponsor integrations.
- Runtime (`backend/app/runtime/`): `simple` runtime today, LangGraph-capable runtime path behind feature flag.

## Request Path

1. User submits a chat message in a selected role space with `role` and `thread_id`.
2. Frontend calls backend `/chat`.
3. Backend route delegates to `ChatOrchestrator`.
4. Orchestrator resolves runtime (`simple` or `langgraph`) from feature flag.
5. Orchestrator resolves configured provider adapter (`mock` or `MiniMax` path).
6. Orchestrator/runtime selects role-specific prompts and guardrails on the shared provider route.
7. Runtime executes generation and returns a normalized response payload.

## Extension Hooks

- Role system hook:
  - role-specific prompt and policy registry for `companion`, `local_guide`, `study_guide`.
- Safety risk scoring hook (next slice).
- Short-term memory hook (`role` + `thread_id` + Redis/LangGraph checkpoints) (next slices).
- Long-term memory hook (hybrid profile + retrieval memory) (next slices).
- Recommendation orchestration hook (next slices).
- Voice adapter path with fallback (later slices).

## Feature Flag Rule

Provider activation and fallback decisions are controlled by environment flags, not hard-coded branching in route handlers.

## Memory Design Alignment

- Profile memory: durable user preferences/facts in Postgres.
- Retrieval memory: pgvector-backed semantic search for fuzzy recall and extra materials.
- Keep profile writes explicit and auditable; retrieval corpus can include optional external materials.

## Role Isolation Rule

- Conversation continuity is scoped by (`user_id`, `role`, `thread_id`).
- Each role space keeps independent conversational context and memory windows.
- The model/provider route stays shared; behavior differences are prompt/policy-driven per role.
