# Stable UUID from path + MD5 hash-skip
_updated: 2026-07-07 | relates: [[markdown-source-of-truth]], [[indexer]], [[watcher]]_

**Rule:** Record identity and change-detection both derive from the file, not the DB:
- **id** = `uuid.uuid5(uuid.NAMESPACE_URL, str(absolute_file_path))` — deterministic. Same path always yields the same id.
- **skip** = compare `content_hash` (`hashlib.md5` of file bytes) against the stored row; if equal, do nothing and return the existing id.

**Where:** the [[indexer]] — `backend/obsidian_manager/sync/indexer.py` (`_stable_uuid`, `_md5`, `index_file`).

**Why:** Because [[markdown-source-of-truth]] makes the DB rebuildable, ids can't be autoincrement — they must survive a full `reindex_all`. uuid5-from-path guarantees that. The MD5 skip makes reindex cheap and idempotent: re-walking the whole vault only touches rows whose bytes actually changed, avoiding write churn and needless SSE events.

**Gotcha:** id is keyed on the **absolute path**. Moving/renaming a file changes its id — the [[watcher]] handles this as delete-old + index-new on `on_moved`, not an in-place update.
