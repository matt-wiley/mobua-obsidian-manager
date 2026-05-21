# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A "Notion Lite" web UI backed by an Obsidian vault. Markdown files are the **only** source of truth. SQLite is a rebuild-able index, never the primary data store. The full spec is in `docs/implementation-plan.md`.

## Development Commands

**Backend (Python 3.12+, `uv` for package management, run from `backend/`):**
```bash
uv run uvicorn main:app --reload            # Dev server (port 8000)
uv run pytest                               # Run all tests
uv run pytest tests/test_parser.py          # Run single test file
uv add <package>                            # Add a dependency
```

**Frontend (SvelteKit, in `frontend/`):**
```bash
npm run dev                     # Dev server (port 5173, proxies /api → backend)
npm run build && npm run preview # Production build
npm test                        # Run tests
```

Both processes must run simultaneously for the full app.

## Architecture

Three-layer stack: FastAPI backend → SQLite index → SvelteKit frontend.

### Core Data Flow

**Read:** SvelteKit → `GET /api/...` → FastAPI queries SQLite → response  
**Write:** SvelteKit → `PUT /records/{id}` → FastAPI → `writer.py` writes `.md` atomically → `watcher.py` detects change → `parser.py` + `indexer.py` update SQLite → SSE event → Svelte store → UI re-renders  
**Target latency:** < 500ms from Obsidian save to UI update

### Backend (`backend/`)

- `db/queries.py` — **all SQL lives here**. No raw SQL elsewhere.
- `db/connection.py` — single SQLite connection, WAL mode.
- `sync/parser.py` — `.md` file → `{ frontmatter, sections, links }` dict. Frontmatter via `python-frontmatter`; H2 sections by splitting on `^## `; wikilinks via `\[\[(.+?)\]\]` regex.
- `sync/indexer.py` — parser output → SQLite upsert. Generates stable UUIDs from file paths. Skips files where `content_hash` (MD5) is unchanged. Exposes `reindex_all(vault_path)` for startup and repair.
- `sync/writer.py` — SQLite record → `.md` file. Writes atomically via `.tmp` + `os.replace()`.
- `sync/watcher.py` — `watchdog` observer; skips `.obsidian/` and non-`.md` files.
- `api/events.py` — SSE endpoint at `GET /events`.

### Frontend (`frontend/src/`)

- `lib/api/` — **all fetch calls live here**. `client.ts` is the base wrapper; `records.ts` and `folders.ts` expose typed functions. No raw `fetch` outside these files.
- `lib/stores/` — `records`, `schema`, `drawer`, `sync`. The `drawer` store manages the slide-in panel state with replace-not-stack navigation.
- `lib/components/fields/` — one component per field type (`TextField`, `DateField`, `UrlField`, `EnumField`, `RelationField`, `MarkdownField`). Each receives `value`, `readonly`, `onSave(newValue)`. Click → edit mode; blur/Enter → save.
- `lib/components/table/` — TanStack Table wrapper. `TableCell` routes to the correct field component.
- `lib/components/page/` — full document view. `FieldBlock` = single frontmatter property. `SectionBlock` = H2 heading + CodeMirror 6 body.
- `lib/components/drawer/` — `Drawer.svelte` slides in from right (~480px); renders `PageView` for the active record. `Breadcrumb` drives replace-in-place navigation.
- `routes/[folder]/+page.svelte` — table view. `routes/[folder]/[record]/+page.svelte` — full page view.

### SQLite Schema

Three tables: `records` (id, folder_path, file_path, filename, frontmatter JSON, sections JSON, content_hash, updated_at), `links` (source_id, target_file, field_name), `col_widths` (folder_path, field_name, width).

Schema is **emergent**: folder = table concept, file = record, frontmatter keys + H2 headers = fields. `GET /folders/{folder}/schema` aggregates keys at query time — no `ALTER TABLE` ever.

### Key Conventions

- **Wikilink navigation:** click → `drawer.replace(record)` (opens drawer, replaces if already open); Cmd/Ctrl+click → full page view.
- **Type inference** (frontmatter values): YYYY-MM-DD pattern → `date`; `https://` prefix → `url`; numeric string → `number`; `[[...]]` → `relation`; else → `text`.
- **Relation field resolution:** `project:` field looks for a `Projects/` folder first; falls back to distinct enum values within the folder.
- **Column widths** are persisted in `col_widths` SQLite table (UI preference, not vault data).
- **`SyncBadge`** goes amber after 5s without a heartbeat SSE ping; red on watcher error.

## Configuration

`.env` in project root (or `backend/.env`): `VAULT_PATH`, `DB_PATH`, `PORT`. Frontend proxies `/api` to `http://localhost:8000` via `vite.config.ts`.
