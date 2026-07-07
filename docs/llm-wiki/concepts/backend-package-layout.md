# Backend package layout
_updated: 2026-07-07 | relates: [[all-sql-in-queries]]_

**The backend is a single package: `backend/obsidian_manager/`.** Confirmed by `backend/pyproject.toml` (`packages = ["obsidian_manager"]`, entry point `obsidian_manager.__main__:main`) and by every test importing `from obsidian_manager.…`. Internal imports are **relative** (`from ..config import …`, `from .db import queries`).

**App entry:** `obsidian_manager.main:app` (FastAPI). There is no top-level `backend/main.py`, `backend/vault.py`, or `backend/config.py` — those live inside the package.

**Doc convention:** `CLAUDE.md`'s Backend section header gives the package root (`backend/obsidian_manager/`) and its bullets (`db/queries.py`, `sync/parser.py`, ...) are relative to it — same style as the Frontend section (`frontend/src/` → `lib/api/`). So a bullet like `db/queries.py` means `backend/obsidian_manager/db/queries.py`. Conventions like [[all-sql-in-queries]] apply to the package. (Header + dev command corrected 2026-07-07; previously the header said `backend/` and the uvicorn target omitted the module path.)

**History:** A duplicate pre-refactor flat tree (`backend/db|api|sync|models`, absolute-import style, non-importable) was removed 2026-07-07. If old paths resurface, they're from before that cleanup.
