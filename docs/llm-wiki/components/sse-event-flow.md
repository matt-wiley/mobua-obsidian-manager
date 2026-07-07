# sse-event-flow
_updated: 2026-07-07 | relates: [[watcher]], [[sync-badge-states]]_

**File(s):** `backend/obsidian_manager/api/events.py` → `frontend/src/lib/stores/sync.svelte.ts`
**Role:** Push-side of the read path. `GET /events` (SSE) is how a vault change reaches the UI without polling.

**Non-obvious:**
- The full live-update chain: file save → [[watcher]] → [[indexer]] updates SQLite → watcher's `on_change` → SSE event on `/events` → `sync`/`records` store → Svelte reactive re-render. Target budget: **<500ms** from Obsidian save to UI update.
- The endpoint also emits periodic **heartbeat pings** independent of file activity — this is what keeps [[sync-badge-states]] green. Without them the client can't distinguish "idle" from "connection dead," which is exactly why the badge goes amber after 5s of silence.
- Event payloads mirror the watcher's `on_change` dicts (`record_changed` / `record_deleted` with `folder_path` + `record_id`), so the frontend can invalidate just the affected folder/record.
