# 2026-07-15 Pass 07 — Drawer settings mode + hljs theme fix
_relates: [[index]]_

## What Changed
- New page: [[drawer]] (component) — two modes, CSS inheritance gotcha, live record sync, schema lazy-load.
- New page: [[settings-in-drawer]] (decision) — why drawer over `/settings` route.
- Updated [[wikilink-navigation]] — added settings mode reference and links to [[drawer]], [[settings-in-drawer]].
- Updated INDEX: new Decisions and Components entries, new "UI panels" cluster, two new Cross-References, updated File↔Concept Bindings, Known Gaps cleanup.
- Updated wiki-health to pass 07 (25 pages: 6 decision, 5 pattern, 6 concept, 8 component).

## Why
Three commits landed this session: `b39cc5c` (hljs CSS specificity fix — `code:not(.hljs)` + removed background overrides), `c4fb46b` (settings moved into drawer panel; `drawerStore` gains `mode` + `openSettings()`; `/settings` route deleted), `fda2cf2` (font-family fix on `.drawer` — it's outside `.app-shell`).

## Gaps Remaining
- `records`, `schema`, `sync` frontend stores still undocumented.
- HTTP API surface, column-resize, table view still undocumented.
