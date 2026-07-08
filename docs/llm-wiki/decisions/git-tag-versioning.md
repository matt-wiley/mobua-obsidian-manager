# Git-Tag Single-Source Versioning
_updated: 2026-07-08 | relates: [[build-info-endpoint]]_

**Decision:** One app version for the whole stack, single-sourced from git tags (hatch-vcs). Bump = create an annotated tag via `make release VERSION=x.y.z`.
**Why:** The backend already derived its version from tags (`pyproject.toml`: `dynamic = ["version"]`, `[tool.hatch.version] source = "vcs"`, `root = ".."`). A second hand-maintained number would drift — `frontend/package.json` still literally read `0.0.1`. Tagging is the standard, no-duplicate path.
**Consequence:**
- "Releasing" = tagging. `make release` validates semver, creates `vX.Y.Z` annotated, prints the `git push origin vX.Y.Z` hint. No version string is edited by hand.
- The frontend keeps **no** version of its own. `package.json`'s `version` is inert (private package, never published) — the UI shows whatever the backend's [[build-info-endpoint]] (`/api/meta`) reports, so there is exactly one number.
- Backend and frontend ship from the same commit (`make build` compiles the SvelteKit static into the wheel), so the backend's git state faithfully represents the running browser bundle too.
