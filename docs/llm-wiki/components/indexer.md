# indexer
_updated: 2026-07-07 | relates: [[parser]], [[stable-uuid-and-hash-skip]], [[watcher]], [[all-sql-in-queries]]_

**File(s):** `backend/obsidian_manager/sync/indexer.py`
**Role:** Bridge [[parser]] output → SQLite. Two entry points: `index_file(path, vault_path, conn)` (one file, returns record id) and `reindex_all(vault_path, conn)` (walk vault, returns count).

**Non-obvious:**
- Resolves both `file_path` and `vault_path` to absolute before anything — id derivation depends on the absolute path (see [[stable-uuid-and-hash-skip]]).
- **Early-out:** if a row exists with the same `content_hash`, returns the existing id without re-parsing or writing. This is the idempotency guarantee that makes `reindex_all` cheap.
- One `index_file` call = `upsert_record` + `replace_links` + a single `conn.commit()`. Links are fully replaced, never diffed.
- `reindex_all` skips any path containing `.obsidian` in its parts. All SQL goes through `db/queries` per [[all-sql-in-queries]]. Called on startup and by the [[watcher]] on every file event.
