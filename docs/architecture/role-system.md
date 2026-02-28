# CompanionHK Role System

This document defines the MVP multi-role behavior for chat.

## Roles

- `companion`
  - Purpose: emotional companionship and supportive daily check-ins.
  - Tone: warm, empathetic, non-judgmental.
- `local_guide`
  - Purpose: local lifestyle and tour guidance for Hong Kong users.
  - Tone: practical, context-aware, routing/recommendation oriented.
- `study_guide`
  - Purpose: studying support, planning, and concept reinforcement.
  - Tone: structured, encouraging, educational.

## API Contract

Canonical chat requests include:

- `user_id`
- `message`
- `role` (`companion` | `local_guide` | `study_guide`)
- `thread_id` (optional; backend can generate default)

Role-specific chat aliases are also available:

- `POST /chat/companion`
- `POST /chat/guide`
- `POST /chat/study`

Role-specific alias payload:

- `user_id`
- `message`
- `thread_id` (optional)

History retrieval endpoints:

- `GET /chat/history?user_id&role&thread_id&limit`
- `GET /chat/companion/history?user_id&thread_id&limit`
- `GET /chat/guide/history?user_id&thread_id&limit`
- `GET /chat/study/history?user_id&thread_id&limit`

Chat responses continue to return a normalized payload with:

- request metadata (`request_id`, `runtime`, `provider`)
- `thread_id`
- generated `reply`
- `safety` result

## Role-Scoped Threading

Thread continuity is scoped by:

- (`user_id`, `role`, `thread_id`)

Rules:

- Each role space has independent conversation history.
- Switching roles does not reuse prior role context.
- Short-term memory/checkpoints should key by role-scoped thread identity.

## Frontend Role Routing

Roles are URL-routed in the frontend via `src/features/chat/role-routing.ts`:

- `/chat/companion` -> `companion`
- `/chat/guide` -> `local_guide`
- `/chat/study` -> `study_guide`

Role selection happens on the home page (`/`). Selecting a role navigates to `/chat/[slug]`. Role switching within chat also uses URL navigation (not tab switching within a single page).

Each role page hydrates its message history from the backend on mount via `GET /chat/{role}/history`.

The `local_guide` role additionally renders a recommendations panel with Google Maps canvas when recommendation data is available.

## Shared Model Route with Role Prompts

MVP uses one primary chat model/provider route.

Role differences are handled through role-specific prompt/policy selection:

- shared runtime/provider infrastructure,
- role-specific system prompt,
- role-specific response style and constraints.

## Safety Alignment

Safety policies apply to all roles:

- dangerous self-harm or harmful instructions are refused,
- supportive and de-escalating language remains required,
- crisis banner/escalation behavior remains available independent of role.
