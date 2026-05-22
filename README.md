# Obsidian Manager

A "Notion Lite" web UI backed by an Obsidian vault. Markdown files are the only source of truth — SQLite is a rebuild-able index, never primary storage.

## How it works

- **Folder = table.** Every subfolder in your vault becomes a browsable table view.
- **File = record.** Each `.md` file is a row.
- **Frontmatter keys + H2 headers = fields.** Schema is emergent — no declarations, no migrations.
- **Live sync.** A file watcher keeps SQLite in sync with vault changes. Edits in the UI write back to `.md` files atomically. Target latency: <500ms from Obsidian save to UI update.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLite |
| File watching | `watchdog` |
| Markdown parsing | `python-frontmatter` |
| Frontend | SvelteKit · TypeScript |
| Markdown editor | CodeMirror 6 |

## Prerequisites

- Python 3.12+, [`uv`](https://github.com/astral-sh/uv)
- Node.js 18+

## Building

Build a self-contained wheel with the UI baked in:

```bash
make build
```

This runs `npm run build` in the frontend, copies the output into the Python package, then runs `uv build`. The resulting wheel is in `backend/dist/`.

## Running the built package

Install and run:

```bash
uv tool install backend/dist/obsidian_manager-*.whl
obsidian-manager
```

Or run directly without installing:

```bash
uv run --with backend/dist/obsidian_manager-*.whl obsidian-manager
```

Configure via environment variables or a `.env` file in the working directory:

```env
VAULT_PATH=/path/to/your/obsidian/vault
DATA_DIR=~/.obsidian-manager
PORT=8000
```

Open [http://localhost:8000](http://localhost:8000).

## Development

Run the backend and frontend separately for hot reload:

```bash
# Terminal 1 — backend
cd backend
uv run uvicorn obsidian_manager.main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The frontend proxies `/api` to the backend.

**Backend tests:**
```bash
cd backend
uv run pytest
```

**Frontend tests:**
```bash
cd frontend
npm test
```

## Architecture

```
SvelteKit (served by FastAPI in production, :5173 in dev)
    │  GET /api/...
    ▼
FastAPI (:8000)
    │  queries
    ▼
SQLite (index)
    ▲  upsert on change
    │
watchdog ──── .md files (vault, source of truth)
```

**Read path:** SvelteKit → FastAPI queries SQLite → response

**Write path:** SvelteKit → `PUT /api/vaults/{id}/records/{id}` → FastAPI → `writer.py` writes `.md` atomically → `watcher.py` detects change → `parser.py` + `indexer.py` update SQLite → SSE event → Svelte store → UI re-renders

### Key backend modules

| File | Role |
|---|---|
| `db/queries.py` | All SQL — no raw queries elsewhere |
| `sync/parser.py` | `.md` → `{ frontmatter, sections, links }` |
| `sync/indexer.py` | Parser output → SQLite upsert; stable UUIDs from file paths |
| `sync/writer.py` | SQLite record → `.md` (atomic write via `.tmp` + `os.replace`) |
| `sync/watcher.py` | `watchdog` observer; skips `.obsidian/` and non-`.md` files |
| `api/events.py` | SSE endpoint at `GET /api/events` |

### Key frontend modules

| Path | Role |
|---|---|
| `lib/api/` | All fetch calls; `client.ts` base wrapper, `records.ts` / `folders.ts` typed functions |
| `lib/stores/` | `records`, `schema`, `drawer`, `sync` |
| `lib/components/fields/` | One component per field type: `TextField`, `DateField`, `UrlField`, `EnumField`, `RelationField`, `MarkdownField` |
| `lib/components/table/` | DataTable with inline editing, column resize/reorder, sort, visibility |
| `lib/components/page/` | Full document view with `FieldBlock` and `SectionBlock` (CodeMirror) |
| `lib/components/drawer/` | Slide-in panel with breadcrumb navigation for wikilink traversal |

## Field types

Type is inferred automatically from frontmatter values:

| Pattern | Type |
|---|---|
| `YYYY-MM-DD` | date |
| `https://...` | url |
| Numeric string | number |
| `[[...]]` | relation (wikilink) |
| Anything else | text |

## Sync status badge

Always visible in the UI corner:

- **Green** — connected, receiving heartbeats
- **Amber** — no heartbeat for >5s, reconnecting
- **Red** — watcher error
