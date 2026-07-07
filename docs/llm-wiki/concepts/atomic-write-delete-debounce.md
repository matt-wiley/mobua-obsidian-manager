# Atomic-write delete debounce
_updated: 2026-07-07 | relates: [[atomic-md-writes]], [[watcher]], [[stable-uuid-and-hash-skip]]_

A subtle gotcha at the seam between [[atomic-md-writes]] and the [[watcher]]. The atomic swap (`tmp` → `os.replace` → `.md`) surfaces to `watchdog` as a **`deleted` then `created`** pair on the same path — not a single modify. Naively deleting the DB row on the `deleted` event would drop a record that still exists on disk.

**Defense:** `_VaultHandler` never deletes synchronously. On `on_deleted` it schedules a `threading.Timer` (`_DELETE_DEBOUNCE_S = 0.5`s). A subsequent `on_created`/`on_modified` for the same path calls `_cancel_pending_delete`. When the timer does fire (`_do_delete`), it re-checks `Path(path).exists()` — if the file is back, it re-indexes instead of deleting.

So a real deletion only commits when the path is still gone 0.5s later. `on_moved` is handled separately as delete-source + index-dest (ids are path-derived — see [[stable-uuid-and-hash-skip]]).
