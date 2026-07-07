# Wiki Health
_updated: 2026-07-07_

wiki_path: ./docs/llm-wiki/

## Current Status
Initialized 2026-07-07. 18 pages across 4 types (2 decision, 5 pattern, 6 concept, 5 component). All pages ≤100 lines. INDEX reachable to every page in ≤2 hops. `relates:`↔inline mirrors verified consistent.

## Known Gaps
- Frontend stores (`records`, `schema`, `drawer`, `sync`) not documented as pages.
- HTTP API surface (`api/records.py`, `api/folders.py`, `api/config.py`, `api/sync.py`) — routes/payloads uncaptured.
- `col_widths` / column-resize persistence undocumented.
- Table view (TanStack wrapper: `DataTable`, `TableCell`, `ColumnHeader`) + recent quick-search box (commit d982b81) undocumented.
- Pre-existing pytest failures from `.local/test-vault/` fixture drift (baseline 9 failed / 15 errors) — unrelated to code, worth a separate fixture resync.

## Next Review Trigger
After the next significant feature or when store/API pages are added; or if any content type crosses its 8-entry sub-index threshold.

## History
Full pass log in [[history]] (meta/history/).
