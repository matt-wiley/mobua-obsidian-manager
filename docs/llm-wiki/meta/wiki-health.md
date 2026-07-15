# Wiki Health
_updated: 2026-07-15 (pass 07)_

wiki_path: ./docs/llm-wiki/

## Current Status
Healthy (pass 07, 2026-07-15). 25 pages across 4 types (6 decision, 5 pattern, 6 concept, 8 component). All pages ≤100 lines. INDEX reachable to every page in ≤2 hops. `relates:`↔inline mirrors consistent. Pass 07 added [[drawer]] (component) and [[settings-in-drawer]] (decision); updated [[wikilink-navigation]] and INDEX for the settings-in-drawer refactor (commits c4fb46b, fda2cf2). Also covers the hljs CSS specificity fix (commit b39cc5c) — not a wiki page but documented in code comments.

## Known Gaps
- **Parser preamble-drop**: content before the first `## ` heading is silently discarded and invisible in the UI. Documented in [[parser]]; not yet fixed.
- Frontend stores (`records`, `schema`, `sync`) not documented as pages. (`drawer` now covered.)
- HTTP API surface (`api/records.py`, `api/folders.py`, `api/sync.py`) — routes/payloads uncaptured (`api/config.py` now covered by [[vault-registry]]).
- `col_widths` / column-resize persistence undocumented.
- Table view (TanStack wrapper: `DataTable`, `TableCell`, `ColumnHeader`) + recent quick-search box (commit d982b81) undocumented (the `⋯` options-editor entry point is now noted via [[canonical-field-options]]).
- Pre-existing pytest failures from `.local/test-vault/` fixture drift (baseline 9 failed / 15 errors) — unrelated to code, worth a separate fixture resync.
- CLAUDE.md itself still describes a single `VAULT_PATH`; it predates the multi-vault refactor now captured in [[vault-registry]] — worth reconciling.

## Next Review Trigger
After the next significant feature or when store/API pages are added; or if any content type crosses its 8-entry sub-index threshold.

## History
Full pass log in [[history]] (meta/history/).
