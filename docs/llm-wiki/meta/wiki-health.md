# Wiki Health
_updated: 2026-07-08 (pass 03)_

wiki_path: ./docs/llm-wiki/

## Current Status
Healthy (pass 03, 2026-07-08). 21 pages across 4 types (4 decision, 5 pattern, 6 concept, 6 component). All pages ≤100 lines. INDEX reachable to every page in ≤2 hops. `relates:`↔inline mirrors verified consistent. Pass 03 added versioning/build-info coverage ([[git-tag-versioning]], [[build-info-endpoint]]).

## Known Gaps
- Frontend stores (`records`, `schema`, `drawer`, `sync`) not documented as pages.
- HTTP API surface (`api/records.py`, `api/folders.py`, `api/config.py`, `api/sync.py`) — routes/payloads uncaptured.
- `col_widths` / column-resize persistence undocumented.
- Table view (TanStack wrapper: `DataTable`, `TableCell`, `ColumnHeader`) + recent quick-search box (commit d982b81) undocumented.
- Pre-existing pytest failures from `.local/test-vault/` fixture drift (baseline 9 failed / 15 errors) — unrelated to code, worth a separate fixture resync.
- Single shared `sqlite3.Connection` across watcher + API threads (`db/connection.py`) — a known robustness smell, now non-fatal for data loss (see [[live-file-surgical-writes]]) but undocumented as its own page.

## Next Review Trigger
After the next significant feature or when store/API pages are added; or if any content type crosses its 8-entry sub-index threshold.

## History
Full pass log in [[history]] (meta/history/).
