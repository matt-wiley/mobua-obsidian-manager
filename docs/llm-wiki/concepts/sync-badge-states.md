# SyncBadge states
_updated: 2026-07-07 | relates: [[watcher]], [[sse-event-flow]]_

`lib/components/shared/SyncBadge.svelte` reflects live sync health, driven by the `sync` store off the SSE stream (see [[sse-event-flow]]):

- **green / normal** — receiving heartbeat pings.
- **amber** — no heartbeat SSE ping for **5 seconds**. Signals the stream may be stalled; not necessarily fatal.
- **red** — the [[watcher]] reported an error event.

The 5s amber threshold is why the backend emits periodic heartbeat pings on `GET /events` even when nothing changed — silence is indistinguishable from a dead connection otherwise. This is the user-visible tail of the write→UI latency budget (target <500ms from vault save to UI update).
