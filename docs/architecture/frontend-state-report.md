# Frontend Current State Report

Date: 2026-03-01
Scope: `frontend/` only

## 1. Stack and App Surface

- Framework: Next.js 16 App Router (`next@16.1.6`) with TypeScript 5.9 strict mode.
- UI kit: Tailwind CSS 4.2 + shadcn/ui (Radix UI 1.4) + Framer Motion 12.34.
- Icons: Lucide React 0.575.
- Content rendering: `react-markdown` 10.1 + `remark-gfm` + `rehype-sanitize`.
- Route surface:
  - `/welcome` — landing page (redirects to `/` if already logged in).
  - `/login` — authentication page (login/signup toggle).
  - `/` — home / role selection (requires auth, redirects to `/welcome` if not logged in).
  - `/chat/[role]` — dynamic chat pages (`/chat/companion`, `/chat/guide`, `/chat/study`).
  - `/weather` — weather details page.
  - Global layout from `src/app/layout.tsx`.
  - No custom `not-found.tsx`, `error.tsx`, or middleware.

## 2. Authentication

- `AuthProvider` context (`src/lib/auth-context.tsx`) with localStorage-based state.
- Supports login and signup toggle on `/login` page.
- Protected routes redirect unauthenticated users to `/welcome`.
- User identity propagated to chat API calls (replaces prior hardcoded `demo-user`).

## 3. Design System and Theming

- Design system lives in `src/app/globals.css` with CSS custom properties.
- Weather-adaptive themes: `clear-day`, `clear-night`, `rain`, `cloudy`, `snow`, `fog`, `drizzle`, `thunderstorm`, `partly-cloudy`, and more (10+ states).
- Role-specific colors: `--role-companion`, `--role-local-guide`, `--role-study-guide`.
- Safety colors: `--safety-bg`, `--safety-border`, `--safety-text`.
- Glassmorphism utility classes.
- Animation keyframes: `bubble-in`, `typing-dot`, `float`, `shimmer`.
- Typography: Nunito (headings) + Nunito Sans (body).
- Framer Motion presets in `src/lib/motion-config.ts`.

## 4. Components

### shadcn/ui primitives (`src/components/ui/`)

`button`, `card`, `input`, `badge`, `alert`, `avatar`, `scroll-area`, `collapsible` — 8 components built on Radix UI.

### Weather components (`src/components/`)

- `weather-provider.tsx` — React context with browser geolocation, backend weather API call, localStorage caching.
- `weather-background.tsx` — animated weather-themed page background.
- `weather-island.tsx` — compact weather display widget.
- `weather-details-panel.tsx` — expanded weather information panel.

### Safety component

- `safety-banner.tsx` — crisis resources banner triggered by `safety.show_crisis_banner`. Displays verified Hong Kong hotlines (The Samaritans HK: 2896 0000, Suicide Prevention Services: 2382 0000, The Samaritan Befrienders HK: 2389 2222, Emergency: 999). Dismissible, weather-adaptive styling.

### Chat feature (`src/features/chat/`)

- `chat-shell.tsx` — main chat interface (~1420 lines). Multi-role with per-role message state, thread management, message hydration from API.
- `assistant-message-parser.ts` — parses assistant responses including thinking blocks.
- `role-routing.ts` — maps URL slugs to canonical role values and back.
- `types.ts` — TypeScript types for messages, roles, safety metadata.

### Recommendations feature (`src/features/recommendations/`)

- `recommendation-list.tsx` — renders ranked recommendation cards.
- `recommendation-card.tsx` — individual place card with rationale, distance/time, rating.
- `map-canvas.tsx` — Google Maps JavaScript API canvas with markers for recommended places.
- `types.ts` — recommendation TypeScript types.

## 5. State Management

- **AuthProvider** (`src/lib/auth-context.tsx`): localStorage auth state, user identity.
- **WeatherProvider** (`src/components/weather-provider.tsx`): weather data with browser geolocation and localStorage caching.
- **Local state in ChatShell**: `useState` for `messagesByRole`, `safetyByRole`, `showCrisisBannerByRole`, input, loading, errors, per-role thread IDs.
- **Recommendations state**: keyed by `assistantRequestId` within ChatShell.
- No Redux, Zustand, or other global state library.

## 6. Chat Features

- Multi-role chat with separate histories per role.
- Thread management per role (`threadIdRef` keyed by role).
- Message hydration from backend API on mount / role switch.
- Image attachments (JPEG/PNG/WebP, max 5MB) sent as part of chat requests.
- Markdown rendering with sanitization for assistant messages.
- Collapsible thinking blocks from assistant reasoning.
- Per-message TTS button with provider selection (`auto`, `elevenlabs`, `cantoneseai`).
- Auto-scroll with floating action button.
- Role switching via URL navigation (`/chat/companion`, `/chat/guide`, `/chat/study`).
- Clear history with confirmation dialog.
- Typing indicators and message timestamps.
- Role-specific icons and empty states.
- Error handling and loading states throughout.

## 7. API Integration Layer (`src/lib/api/`)

- `base-url.ts` — resolves `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).
- `chat.ts` — `POST /chat/{role}` (send message), `GET /chat/{role}/history` (fetch history), `DELETE /chat/{role}/history` (clear).
- `voice.ts` — `POST /voice/tts` with preferred provider selection.
- `recommendations.ts` — `POST /recommendations`, `POST /recommendations/history`.
- `weather.ts` — `GET /weather` with latitude/longitude.

All use `fetch` with error handling and TypeScript types.

## 8. Data Flow and Runtime Contracts

- Frontend API base URL: `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` for client-side map rendering.
- Chat contract: request includes `user_id`, `role`, `thread_id`, `message`, optional `image`; response includes `reply`, `safety` metadata, `request_id`.
- Recommendation contract: request includes user query and geo coordinates; response includes ranked places + weather context.
- Weather contract: GET endpoint consumed by `WeatherProvider` for theme adaptation and weather UI.

## 9. Testing

- Test runner: Vitest 4.0 with `@testing-library/react`, `jest-dom`, `user-event`.
- Test files: `chat-shell.test.tsx`, `recommendations.test.tsx`.
- Test setup: `src/test/setup.ts`.
- No committed Playwright/E2E browser test configuration.

## 10. Gaps and Risks

1. No custom `not-found.tsx` or `error.tsx` — failures degrade to generic Next.js pages.
2. No automated browser/E2E tests in repository.
3. Auth is localStorage-based — not production-ready (acceptable for hackathon).
4. No WebSocket support for real-time streaming.
5. No offline/service-worker support.
6. Voice input (STT) UI not yet implemented — only TTS playback is wired.
