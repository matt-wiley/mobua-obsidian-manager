# Project Wiki Index
_updated: 2026-07-13 (pass 05)_

## Project in One Paragraph
mobua-obsidian-manager is a "Notion Lite" web UI over an Obsidian vault. `.md` files are the **only** source of truth ([[markdown-source-of-truth]]); SQLite is a rebuildable index. Stack: FastAPI backend → SQLite (WAL) → SvelteKit frontend. Writes go UI → `writer.py` (atomic `.md` write) → `watcher.py` → `parser.py` + `indexer.py` → SQLite → SSE → Svelte store → re-render, targeting <500ms from save to UI. The schema is emergent ([[emergent-schema]]): folder = table, file = record, frontmatter keys + H2 headings = fields.

## Schema
→ see [[schema]] (meta/schema.md) — 4 content types: decision, pattern, concept, component.

## Decisions
- [[markdown-source-of-truth]] — `.md` is canonical; SQLite is rebuildable.
- [[atomic-md-writes]] — tmp + `os.replace`; never write in place.
- [[live-file-surgical-writes]] — updates read the live file + splice; never regenerate from the index.
- [[git-tag-versioning]] — one app version from git tags; bump via `make release`.
- [[canonical-field-options]] — fields can pin a fixed option list in-vault; the one exception to emergent schema.

## Patterns
- [[all-sql-in-queries]] — all backend SQL in `db/queries.py`.
- [[all-fetch-in-lib-api]] — all frontend fetch in `lib/api/`.
- [[one-component-per-field-type]] — one field component per type, uniform props.
- [[frontmatter-type-inference]] — value → field type, order-sensitive.
- [[stable-uuid-and-hash-skip]] — uuid5-from-path id + MD5 skip-unchanged.

## Concepts
- [[emergent-schema]] — schema computed at query time, no `ALTER TABLE`.
- [[wikilink-navigation]] — click → drawer replace; Cmd-click → full page.
- [[relation-field-resolution]] — folder-first, enum fallback.
- [[sync-badge-states]] — green/amber(5s)/red sync health.
- [[atomic-write-delete-debounce]] — 0.5s debounce survives atomic-write delete+create.
- [[backend-package-layout]] — backend is the single `obsidian_manager/` package (stale dup removed & CLAUDE.md paths fixed 2026-07-07).

## Components
- [[parser]] — `.md` → dict; sections/links/type inference.
- [[indexer]] — parsed dict → SQLite upsert; idempotent.
- [[writer]] — record → rendered `.md`, atomic.
- [[watcher]] — watchdog → indexer → SSE; delete-debounce + guardian.
- [[sse-event-flow]] — `/events` push chain + heartbeat.
- [[build-info-endpoint]] — `/api/meta` + About badge; live-git-favoring version resolution.
- [[vault-registry]] — multi-workspace lifecycle; per-vault DB; non-destructive remove.

## Concept Clusters
- **write path**: [[markdown-source-of-truth]], [[atomic-md-writes]], [[live-file-surgical-writes]], [[writer]], [[atomic-write-delete-debounce]]
- **sync / read path**: [[watcher]], [[indexer]], [[sse-event-flow]], [[sync-badge-states]]
- **schema & fields**: [[emergent-schema]], [[frontmatter-type-inference]], [[one-component-per-field-type]], [[relation-field-resolution]], [[canonical-field-options]]
- **identity**: [[stable-uuid-and-hash-skip]], [[parser]]
- **layering conventions**: [[all-sql-in-queries]], [[all-fetch-in-lib-api]]
- **versioning / build info**: [[git-tag-versioning]], [[build-info-endpoint]]
- **workspaces**: [[vault-registry]], [[watcher]], [[sse-event-flow]]

## Cross-References
- [[atomic-md-writes]] → [[atomic-write-delete-debounce]]: the atomic swap fires delete+create, which the watcher must debounce.
- [[markdown-source-of-truth]] → [[stable-uuid-and-hash-skip]]: rebuildable DB forces path-derived ids, not autoincrement.
- [[markdown-source-of-truth]] → [[live-file-surgical-writes]]: "index is rebuildable" means writes must trust the file, not the index — regenerating from the index caused field-edit data loss.
- [[frontmatter-type-inference]] → [[emergent-schema]]: inferred types are what make a query-time schema possible.
- [[canonical-field-options]] → [[emergent-schema]]: pinned option lists are the one deliberate exception — schema stays emergent unless a field opts into a declared set.
- [[watcher]] → [[sse-event-flow]] → [[sync-badge-states]]: change events flow to the UI; heartbeats keep the badge green.
- [[git-tag-versioning]] → [[build-info-endpoint]]: the tag is the source; `/api/meta` resolves and exposes it, favoring live git over stale install metadata.
- [[vault-registry]] → [[markdown-source-of-truth]]: removing a workspace only stops the watcher + drops the registry entry; the source `.md` files are never touched (rebuildable index makes this safe).
- [[vault-registry]] → [[watcher]]: each active vault owns one watcher; `activate` starts it, `deactivate` stops+joins it.

## File ↔ Concept Bindings
- `backend/obsidian_manager/sync/parser.py` → [[parser]], [[frontmatter-type-inference]]
- `backend/obsidian_manager/sync/indexer.py` → [[indexer]], [[stable-uuid-and-hash-skip]]
- `backend/obsidian_manager/sync/writer.py` → [[writer]], [[atomic-md-writes]], [[live-file-surgical-writes]]
- `backend/obsidian_manager/api/records.py` → [[live-file-surgical-writes]]
- `backend/obsidian_manager/sync/watcher.py` → [[watcher]], [[atomic-write-delete-debounce]]
- `backend/obsidian_manager/api/events.py` → [[sse-event-flow]]
- `backend/obsidian_manager/db/queries.py` → [[all-sql-in-queries]], [[emergent-schema]]
- `backend/obsidian_manager/schema_config.py`, `backend/obsidian_manager/api/folders.py` → [[canonical-field-options]]
- `frontend/src/lib/components/table/FieldOptionsEditor.svelte`, `frontend/src/lib/components/table/ColumnHeader.svelte` → [[canonical-field-options]]
- `frontend/src/lib/api/` → [[all-fetch-in-lib-api]]
- `frontend/src/lib/components/fields/` → [[one-component-per-field-type]], [[relation-field-resolution]]
- `frontend/src/lib/components/shared/SyncBadge.svelte` → [[sync-badge-states]]
- `backend/obsidian_manager/_buildinfo.py`, `backend/obsidian_manager/api/meta.py` → [[build-info-endpoint]], [[git-tag-versioning]]
- `frontend/src/lib/components/shared/BuildBadge.svelte`, `frontend/src/lib/api/meta.ts` → [[build-info-endpoint]]
- `backend/obsidian_manager/vault.py`, `backend/obsidian_manager/api/config.py` → [[vault-registry]]
- `frontend/src/lib/api/config.ts`, `frontend/src/routes/+page.svelte`, `frontend/src/routes/setup/+page.svelte` → [[vault-registry]]

## Known Gaps
- Frontend stores (`records`, `schema`, `drawer`) not yet documented as their own pages.
- `col_widths` persistence and column-resize UI undocumented.
- `api/records.py` / `api/folders.py` HTTP surface (routes, payloads) not yet captured.
