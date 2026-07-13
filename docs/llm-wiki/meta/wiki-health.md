# Wiki Health
_updated: 2026-07-13 (pass 05)_

wiki_path: ./docs/llm-wiki/

## Current Status
Healthy (pass 05, 2026-07-13). 23 pages across 4 types (5 decision, 5 pattern, 6 concept, 7 component). All pages ≤100 lines. INDEX reachable to every page in ≤2 hops. `relates:`↔inline mirrors verified consistent. Pass 05 added [[canonical-field-options]] — the first deliberate exception to emergent schema: a field can pin a fixed option list in `<vault>/.obsidian-manager/schema.yaml`, merged into the schema endpoint so retired enum values stay selectable.

## Known Gaps
- Frontend stores (`records`, `schema`, `drawer`, `sync`) not documented as pages.
- HTTP API surface (`api/records.py`, `api/folders.py`, `api/sync.py`) — routes/payloads uncaptured (`api/config.py` now covered by [[vault-registry]]).
- `col_widths` / column-resize persistence undocumented.
- Table view (TanStack wrapper: `DataTable`, `TableCell`, `ColumnHeader`) + recent quick-search box (commit d982b81) undocumented (the `⋯` options-editor entry point is now noted via [[canonical-field-options]]).
- Pre-existing pytest failures from `.local/test-vault/` fixture drift (baseline 9 failed / 15 errors) — unrelated to code, worth a separate fixture resync.
- CLAUDE.md itself still describes a single `VAULT_PATH`; it predates the multi-vault refactor now captured in [[vault-registry]] — worth reconciling.

## Next Review Trigger
After the next significant feature or when store/API pages are added; or if any content type crosses its 8-entry sub-index threshold.

## History
Full pass log in [[history]] (meta/history/).
