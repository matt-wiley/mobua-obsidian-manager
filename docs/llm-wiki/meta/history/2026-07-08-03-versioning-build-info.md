# 2026-07-08 Pass 03 — Versioning & Build-Info

_relates: [[index]]_

## What Changed
- New decision [[git-tag-versioning]] — one app version single-sourced from git tags (hatch-vcs); bump via `make release VERSION=x.y.z`; frontend keeps no version of its own.
- New component [[build-info-endpoint]] — `GET /api/meta` (`_buildinfo.py` + `api/meta.py`) and `BuildBadge.svelte` About modal. Captures the live-git-favoring resolution order, leading-`v` normalization, and Docker build-arg baking.
- INDEX: added both pages to Decisions/Components; new `versioning / build info` cluster; cross-ref git-tag-versioning → build-info-endpoint; file bindings for `_buildinfo.py`, `api/meta.py`, `BuildBadge.svelte`, `meta.ts`.

## Why
Session added a versioning mechanism + an in-UI build-info view (commit 13a1bf3). The non-obvious core — favoring live `git describe` over stale editable-install package metadata so the badge reflects what's actually running — was a mid-session correction worth preserving.

## Gaps Remaining
- Unchanged from pass 02: frontend stores, HTTP API surface (records/folders/config/sync routes), `col_widths` persistence, table view (DataTable/TableCell + quick-search), shared single sqlite connection.
- `frontend/package.json` `version` is now inert (documented in [[git-tag-versioning]]); could be removed entirely in a future cleanup.
