# Vault Registry (Multi-Workspace)

_updated: 2026-07-13 | relates: [[markdown-source-of-truth]], [[watcher]], [[sse-event-flow]], [[all-fetch-in-lib-api]], [[all-sql-in-queries]]_

**File(s):** `backend/obsidian_manager/vault.py`, `backend/obsidian_manager/api/config.py`, `frontend/src/lib/api/config.ts`, `frontend/src/routes/+page.svelte`, `frontend/src/routes/setup/+page.svelte`

**Role:** Manages N concurrently-active vaults ("workspaces" in the UI). Supersedes the single `VAULT_PATH` model CLAUDE.md still describes — that env var is now only a default/seed, not the runtime shape.

**Non-obvious:**
- **Dual state per vault.** Runtime state is the in-memory `_vaults` dict in `vault.py` (holds the live `observer` handle). Durable state is `DATA_DIR/vaults.json` (id/name/path only), written by `config.py`. The two are kept in sync by hand — every add/remove touches both. `_vaults` is authoritative for "is it active right now"; `vaults.json` is authoritative for "what to re-activate on startup".
- **One DB file per vault**, `DATA_DIR/{vault_id}.db` — not a single shared index. `activate()` calls `init_db(vault_id, ...)` and the connection is keyed by `vault_id`; queries must route by vault. See [[all-sql-in-queries]].
- **`vault_id`** comes from `_vault.unique_id(name)` — derived from the display name, not the path. Renaming implications live there.
- **`activate()`** does the full bring-up: init per-vault DB → `reindex_all` → `start_watcher` ([[watcher]]). The watcher's `on_change` is wrapped to stamp `vault_id` onto every event before `events.broadcast`, so [[sse-event-flow]] stays multi-vault aware.
- **Removal is non-destructive** — the whole point of the DELETE path. `deactivate()` only stops+joins the watcher observer and `close_db(vault_id)`; `DELETE /config/vaults/{id}` then drops the entry from `vaults.json`. The **source vault directory and its `.md` files are never touched** ([[markdown-source-of-truth]]), and the `{vault_id}.db` index file is left on disk (harmless; re-adding reindexes from scratch).
- **UI wiring:** `+page.svelte` (Workspaces home) lists vaults and has the per-card remove control with an inline "Remove?/Cancel" confirm — no native `confirm()`. `setup/+page.svelte` adds one. All calls go through `lib/api/config.ts` (`getConfig`/`addVault`/`removeVault`), per [[all-fetch-in-lib-api]].

**HTTP surface:** `GET /config` → `{vault_configured, vaults:[{id,name,path}]}` · `POST /config/vault` {name,path} → 201 entry (validates path exists + is dir) · `DELETE /config/vaults/{id}` → 204 (404 if unknown).
