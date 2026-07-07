# watcher
_updated: 2026-07-07 | relates: [[indexer]], [[atomic-write-delete-debounce]], [[sse-event-flow]], [[sync-badge-states]]_

**File(s):** `backend/obsidian_manager/sync/watcher.py`
**Role:** `watchdog` observer over the vault. Every relevant file event drives the [[indexer]], then fires an optional `on_change(event_dict)` callback that feeds the [[sse-event-flow]].

**Non-obvious:**
- **Relevance filter:** only non-directory `*.md` paths that aren't under `.obsidian/`. Everything else is ignored at the top of each handler.
- **Delete debounce:** deletes are deferred 0.5s and cancelled by a following create/modify — the defense against atomic-write false deletes. Full detail in [[atomic-write-delete-debounce]].
- **Moves** (`on_moved`) = delete source row + index dest; ids are path-derived so a move is genuinely a new record.
- **Guardian thread:** `_start_guardian` runs a daemon loop that every 5s checks `observer.is_alive()` and rebuilds a fresh `Observer` + handler if it died. A watcher crash degrades sync but doesn't kill it — and surfaces to the UI via [[sync-badge-states]].
- `on_change` events are `record_changed` / `record_deleted` dicts carrying `folder_path` + `record_id`.
