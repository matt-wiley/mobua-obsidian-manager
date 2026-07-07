# All fetch calls live in lib/api/
_updated: 2026-07-07 | relates: [[all-sql-in-queries]], [[one-component-per-field-type]]_

**Rule:** No raw `fetch` outside `frontend/src/lib/api/`. `client.ts` is the base wrapper; `records.ts`, `folders.ts`, `config.ts` expose typed functions. Components and stores call those, never `fetch` directly.

**Where:** `frontend/src/lib/api/`. Consumers: `lib/stores/*`, route `+page.svelte` files, and the field components (see [[one-component-per-field-type]]) whose `onSave` calls land here.

**Why:** Single place for base URL, error handling, and response typing. The Vite dev proxy sends `/api` → `http://localhost:8000`; keeping all requests behind the wrapper means that assumption lives in exactly one layer. Backend mirror is [[all-sql-in-queries]].
