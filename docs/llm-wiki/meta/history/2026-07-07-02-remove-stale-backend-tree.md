# 2026-07-07 Pass 02 — Remove stale duplicate backend tree
_relates: [[index]]_

## What Changed
- Deleted the stale flat backend tree: `backend/db/`, `backend/api/`, `backend/sync/`, `backend/models/` (17 tracked files via `git rm`, plus leftover untracked `__pycache__`).
- Rewrote [[backend-package-layout]] — removed the "live vs. stale" framing now that the duplicate is gone; kept the CLAUDE.md unprefixed-paths caveat and recorded the removal as history.
- Updated INDEX.md and wiki-health.md Known Gaps accordingly (stale-tree gap closed; CLAUDE.md-path gap remains).

## Why
The duplicate was a pre-package-refactor copy using absolute imports (`import vault`, `from config import DATA_DIR`, `from db import queries`) whose dependencies don't exist at `backend/` root — i.e. non-importable dead code. The live package (`backend/obsidian_manager/`, relative imports) is the only one packaged (`pyproject.toml`) and tested. Removing it ends the path ambiguity.

## Verification
- `from obsidian_manager.main import app` imports cleanly before and after.
- Test baseline identical before/after removal: `9 failed, 19 passed, 15 errors`. The failures are pre-existing and unrelated — tests reference fixture files (e.g. `Projects/Q3 Rebrand.md`) absent from the current `.local/test-vault/` (which holds `Areas/People/Work`). Not introduced by this change.

## Gaps Remaining
- **Pre-existing test breakage**: `.local/test-vault/` fixtures are out of sync with `tests/` expectations — worth a separate fix.
- CLAUDE.md still documents backend paths without the `obsidian_manager/` prefix.
- Changes staged, not committed (per standing preference).
