# Frontend Current State Report

Date: 2026-02-28
Scope: `frontend/` only

## 1. Stack and App Surface

- Framework: Next.js App Router (`next@16`) with TypeScript strict mode.
- UI kit: MUI (`@mui/material`) + Emotion.
- Route surface is currently minimal:
  - `/` from `src/app/page.tsx`
  - global layout from `src/app/layout.tsx`
  - no custom `not-found.tsx`, `error.tsx`, or middleware.

## 2. Design and UX Implementation

- Root page renders a centered card container with `ChatShell`.
- Theme is weather-adaptive via `CompanionThemeProvider`:
  - Reads browser geolocation (with timeout fallback to Hong Kong coordinates).
  - Calls backend weather API and maps weather context to palette.
- Core interaction model in `ChatShell`:
  - Role tabs: `companion`, `local_guide`, `study_guide`.
  - Role-scoped local state (`messagesByRole`) and role-scoped thread ids.
  - Sends `/chat` for all roles; for `local_guide`, also requests `/recommendations`.
  - Renders recommendation cards and optional map canvas.

## 3. Data Flow and Runtime Contracts

- Frontend API base URL:
  - `NEXT_PUBLIC_API_BASE_URL` if present, else `http://localhost:8000`.
- Chat contract:
  - request: `user_id`, `role`, `thread_id`, `message`
  - response: includes `reply` and `safety` metadata.
- Recommendation contract:
  - request includes user query and geo coordinates.
  - response includes ranked places + weather context.
- Weather contract:
  - GET endpoint used only for theme context.

## 4. Testing Coverage Snapshot

- Unit/integration-style component tests exist for:
  - chat flow and role-scoped continuity,
  - recommendation rendering path,
  - theme provider weather loading call.
- Missing automated browser/E2E route checks in repository:
  - no committed Playwright config/spec for deterministic screenshoting or route health.

## 5. Gaps and Risks

1. Safety UI gap:
   - `ChatResponse.safety` is typed but not surfaced in `ChatShell` (no crisis banner UX yet).
2. Operational reproducibility gap:
   - screenshot workflow is ad hoc (`playwright-cli` artifacts only), not codified.
3. Route resiliency UX gap:
   - no custom `not-found.tsx`/`error.tsx`, so failures degrade to generic Next pages.
4. Route coverage gap:
   - only one route currently exists; no dedicated pages for role spaces.
5. Identity/threading simplification:
   - hardcoded `userId = "demo-user"` is MVP-acceptable but not production-ready.

## 6. Why `/` Should Render

Given current source, `/` should return a rendered page (not 404) because:

- `src/app/page.tsx` exports the root page component.
- `src/app/layout.tsx` wraps children without conditional routing.
- there are no rewrites, middleware redirects, or basePath configuration in `next.config.ts`.

If a 404 appears at `/`, the likely issue is runtime/process targeting (wrong server/port/project instance) rather than missing route code.
