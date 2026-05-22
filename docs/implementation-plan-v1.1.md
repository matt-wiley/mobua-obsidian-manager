# Implementation Plan v1.1

This document captures the known gaps and deferred work from the v1.0 implementation (phases 0–10) as a structured backlog for v1.1. Each item describes a concrete problem observed in the working system, its root cause, and the targeted fix. No new architectural layers are introduced — all fixes extend existing patterns.

**Priority note:** Item 1 (cross-folder wikilink resolution) has the highest day-to-day impact and should be addressed first.

---

## 1. Cross-folder wikilink resolution

### Problem

Relation field wikilinks in the table view only resolve if the linked record is in the currently loaded folder. Cross-folder links — the common case (e.g., a Task linking to a Projects record) — render as unresolved, non-clickable text. `WikiLink.svelte` searches `recordsStore.records`, which only holds the current folder's records, so any record outside that folder is never found.

### Fix

When `RelationField` exits edit mode (after calling `GET /records/{id}/relations/{field}`), cache the matched `RelationOption` and pass the resolved `VaultRecord` to `WikiLink` for view mode. This avoids introducing any new API endpoints and reuses data already returned by the existing relations endpoint.

### Affected files

- `frontend/src/lib/components/fields/RelationField.svelte`
- `frontend/src/lib/components/shared/WikiLink.svelte`

---

## 2. EnumField in table view

### Problem

The schema endpoint returns `field_type: "text"` for low-cardinality string fields. `TableCell` renders these as `TextField` instead of `EnumField`, so users cannot pick from a dropdown of existing values when editing inline in the table. There is currently no signal in the schema response to distinguish a free-text field from one with a small, stable set of values.

### Fix

Extend `GET /folders/{folder}/schema` to include an `options: string[]` array for text fields, populated with distinct non-null values across all records in the folder. Update the `SchemaField` TypeScript type on the frontend to include the optional `options` property. Update `TableCell` to render `EnumField` instead of `TextField` when `options` is non-empty and cardinality is below a threshold (e.g., 10 or fewer distinct values).

### Affected files

- `backend/api/folders.py`
- `backend/db/queries.py` — add `get_distinct_values(conn, folder_path, field_name)`
- `frontend/src/lib/api/folders.ts` — update `SchemaField` type
- `frontend/src/lib/components/table/TableCell.svelte`

---

## 3. Cross-folder drawer edits go stale

### Problem

When the drawer shows a record from a different folder than the current table view, edits in the drawer succeed at the API level but the drawer's record object does not update via SSE. The SSE handler only calls `invalidate()` when the incoming event's folder matches the active table folder, so drawer records from other folders are never refreshed after a `record_changed` event fires.

### Fix

The SSE handler in `+layout.svelte` should also update `drawerStore.record` when the incoming event's record ID matches the currently open drawer record. Add a `syncRecord(updated: VaultRecord)` method to `drawerStore`. After a successful `recordsStore.update()`, call `drawerStore.syncRecord(updated)` — or have the SSE handler fetch and refresh the drawer record directly when a matching `record_changed` event fires for a record not in the current folder.

### Affected files

- `frontend/src/lib/stores/drawer.svelte.ts`
- `frontend/src/routes/+layout.svelte`
- `frontend/src/lib/stores/records.svelte.ts`

---

## 4. No vault path onboarding

### Problem

If `VAULT_PATH` is not set or points to a non-existent directory, the backend starts without error but all API calls fail with opaque HTTP errors. The frontend renders a blank or broken state with no actionable guidance for the user. First-time setup and misconfiguration are effectively silent failures.

### Fix

**Backend:** Add a `GET /health` endpoint that returns `{ "configured": true }` when `VAULT_PATH` is set and points to a valid directory, and `{ "configured": false, "detail": "VAULT_PATH is not set" }` (or equivalent) otherwise.

**Frontend:** On the home page (`routes/+page.svelte`), call `GET /health` before attempting to load folders. If the response contains `configured: false`, or if the health check request itself fails, render an onboarding screen explaining that `VAULT_PATH` must be set in `.env` at the project root and the backend must be restarted.

### Affected files

- `backend/api/health.py` (new file) or `backend/api/records.py`
- `frontend/src/routes/+page.svelte`
