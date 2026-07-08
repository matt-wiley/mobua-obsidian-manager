# Build-Info Endpoint & About Badge
_updated: 2026-07-08 | relates: [[git-tag-versioning]], [[sync-badge-states]], [[all-fetch-in-lib-api]]_

**File(s):** `backend/obsidian_manager/_buildinfo.py`, `backend/obsidian_manager/api/meta.py`, `frontend/src/lib/api/meta.ts`, `frontend/src/lib/components/shared/BuildBadge.svelte`
**Role:** `GET /api/meta` → `{version, commit, build_date}`; `BuildBadge` shows `v{version}` beside [[sync-badge-states]] and opens an About modal. Realizes [[git-tag-versioning]] at runtime.

**Non-obvious:**
- **Resolution order (`get_build_info`, cached once):** `BUILD_VERSION` env → **live `git describe --tags --always --dirty`** → package metadata → `0+unknown`. Live git is deliberately preferred *over* package metadata: an editable/`uv` install bakes a **stale** hatch-vcs version (e.g. an old `0.1.1.dev1+g…`) that lies about what's actually running. Git wins so the badge reflects the real checkout, `-dirty` and all. (This was a mid-session correction — "favor up-to-date info.")
- **Leading `v` stripped** in the backend (`version.removeprefix("v")`) so the value is source-agnostic — git tags carry `v0.1.0`, metadata carries `0.1.0`. The UI re-adds the single `v`; forgetting this double-prints `vv…`.
- **Docker bakes `BUILD_VERSION`/`BUILD_COMMIT`/`BUILD_DATE`** as `ARG`→`ENV` (Dockerfile) fed by `make docker` from `git describe` / `rev-parse` / `date -u`. Required because `.git` is **absent** in the runtime image, so the git fallbacks return `None` there.
- `_git()` runs with `cwd = package dir` and a 2s timeout, swallowing all errors → build info is best-effort, never fatal. `BuildBadge` stays silent (renders nothing) if `/api/meta` is unreachable.
- `meta.ts` is a normal `lib/api/` client, following [[all-fetch-in-lib-api]].
