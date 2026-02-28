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

Chat requests include:

- `user_id`
- `message`
- `role` (`companion` | `local_guide` | `study_guide`)
- `thread_id` (optional; backend can generate default)

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
