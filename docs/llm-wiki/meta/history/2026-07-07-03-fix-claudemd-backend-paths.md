# 2026-07-07 Pass 03 — Fix CLAUDE.md backend paths
_relates: [[index]]_

## What Changed
- `CLAUDE.md`: Backend section header `backend/` → `backend/obsidian_manager/`, plus a note that bullets are relative to that package root (mirrors the Frontend section's `frontend/src/` convention).
- `CLAUDE.md`: dev command `uvicorn main:app` → `uvicorn obsidian_manager.main:app` (the real launch target per the Makefile).
- Wiki: updated [[backend-package-layout]] (caveat → doc-convention note), and closed the CLAUDE.md-paths gap in INDEX.md and wiki-health.md.

## Why
The bullets (`db/queries.py`, `sync/parser.py`, ...) were never individually wrong — the doc's convention is header-root + relative bullets. Only the header root and the absolute uvicorn module path were stale after the code moved into the `obsidian_manager` package. Minimal, convention-consistent fix rather than prefixing every bullet.

## Gaps Remaining
- Pre-existing pytest fixture drift (`.local/test-vault/`) still unfixed.
- Frontend stores / HTTP API surface / table view still undocumented.
- Changes staged, not committed (per standing preference).
