# 2026-07-13 Pass 05 — Canonical field options
_relates: [[index]]_

## What Changed
- Created decision [[canonical-field-options]] — fields can pin a fixed option list in `<vault>/.obsidian-manager/schema.yaml`, merged into `GET /folders/{folder}/schema`.
- Updated [[emergent-schema]] and [[frontmatter-type-inference]] `relates:` + inline mirrors to link the new exception.
- INDEX: new decision entry, schema-&-fields cluster member, cross-reference, and two file bindings (`schema_config.py`/`api/folders.py`, `FieldOptionsEditor.svelte`/`ColumnHeader.svelte`). Bumped to pass 05.
- wiki-health: 22→23 pages (5 decision); refreshed status + table-view gap note.

## Why
The enum option list was derived only from live data (`_detect_enum`), so a status no longer used by any file dropped out of the dropdown and could not be assigned to a new record (reported bug: can't create a file with `03 - Todo`). The fix introduces the first deliberate exception to the emergent schema — a declared, vault-stored option set — which is decision-grade knowledge that the code alone doesn't explain.

## Gaps Remaining
- Broader table-view subsystem (`DataTable`, `TableCell`) still undocumented beyond the options-editor entry point.
- Frontend stores still lack pages, though `schema` store now gained a `reload()` used by this feature.
