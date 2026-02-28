# CompanionHK Foundation Architecture

This document captures the foundational framework decisions and extension points.

## Layers

- Frontend (`frontend/`): Next.js 16 App Router + TypeScript + Tailwind CSS 4 + shadcn/ui + Framer Motion.
- Backend (`backend/`): FastAPI route boundary and orchestration runtime selector.
- Data (`infra/`): local PostgreSQL + Redis for development parity.
- Provider Adapters (`backend/app/providers/`): swap-friendly interfaces for sponsor integrations.
- Runtime (`backend/app/runtime/`): `simple` runtime by default, LangGraph-capable runtime path behind feature flag.

## Frontend Architecture

- Multi-page routing:
  - `/welcome` — landing page.
  - `/login` — authentication (localStorage-based `AuthProvider`).
  - `/` — role selection home (protected).
  - `/chat/[role]` — role-scoped chat (`/chat/companion`, `/chat/guide`, `/chat/study`).
  - `/weather` — weather details page.
- State management: `AuthProvider` context + `WeatherProvider` context + local component state.
- Design system: CSS custom properties for weather-adaptive themes, role colors, safety colors.
- Chat features: image attachments, markdown rendering, thinking blocks, per-message TTS, auto-scroll.

## Request Path

1. User authenticates via `/login` and selects a role on `/`.
2. User navigates to `/chat/[role]` and submits a chat message.
3. Frontend calls backend `/chat/{role}` with `user_id`, `role`, `thread_id`, `message`.
4. Backend route delegates to `ChatOrchestrator`.
5. Orchestrator resolves runtime (`simple` or `langgraph`) from feature flag.
6. Orchestrator resolves configured provider adapter (`mock` or `MiniMax` path).
7. Safety monitor evaluates the message (MiniMax + rules fallback) and attaches `safety` metadata.
8. Orchestrator/runtime selects role-specific prompts and guardrails on the shared provider route.
9. Runtime executes generation and returns a normalized response payload.
10. For `local_guide` role, frontend also calls `/recommendations` with geo coordinates.

## Extension Hooks

- Role system hook:
  - role-specific prompt and policy registry for `companion`, `local_guide`, `study_guide`.
- Safety risk scoring hook:
  - two-tier evaluation (MiniMax model + rule-based fallback).
  - risk levels, emotion labels, policy actions, crisis banner triggers.
- Short-term memory hook:
  - Redis with TTL, scoped by (`user_id`, `role`, `thread_id`).
  - LangGraph checkpoints when LangGraph runtime is enabled.
- Long-term memory hook:
  - hybrid profile (Postgres) + retrieval (pgvector) memory.
  - embedding via LangChain (MiniMax) or deterministic hash fallback.
- Recommendation orchestration hook:
  - Google Maps places + routes, weather context, preference scoring, optional Exa retrieval.
- Voice adapter path:
  - ElevenLabs + Cantonese.ai with provider fallback.
- Weather context hook:
  - `WeatherProvider` in frontend with localStorage caching.
  - Open-Meteo backend adapter with degraded fallback.

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
- Frontend role spaces are URL-routed (`/chat/companion`, `/chat/guide`, `/chat/study`).
