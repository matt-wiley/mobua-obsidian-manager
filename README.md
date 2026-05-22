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

## Setup

### Prerequisites

- Python 3.12+, [`uv`](https://github.com/astral-sh/uv)
- Node.js 18+

### Configuration

Create a `.env` file in the project root (or `backend/`):

```env
VAULT_PATH=/path/to/your/obsidian/vault
DB_PATH=/path/to/obsidian.db
PORT=8000
```

### Running

Start both processes simultaneously:

```bash
# Terminal 1 — backend
cd backend
uv run uvicorn main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Development

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

**Frontend production build:**
```bash
cd frontend
npm run build && npm run preview
```

## Architecture

```
SvelteKit (5173)
    │  GET /api/...
    ▼
FastAPI (8000)
    │  queries
    ▼
SQLite (index)
    ▲  upsert on change
    │
watchdog ──── .md files (vault, source of truth)
```

**Read path:** SvelteKit → FastAPI queries SQLite → response

**Write path:** SvelteKit → `PUT /records/{id}` → FastAPI → `writer.py` writes `.md` atomically → `watcher.py` detects change → `parser.py` + `indexer.py` update SQLite → SSE event → Svelte store → UI re-renders

### Key backend modules

| File | Role |
|---|---|
| `db/queries.py` | All SQL — no raw queries elsewhere |
| `sync/parser.py` | `.md` → `{ frontmatter, sections, links }` |
| `sync/indexer.py` | Parser output → SQLite upsert; stable UUIDs from file paths |
| `sync/writer.py` | SQLite record → `.md` (atomic write via `.tmp` + `os.replace`) |
| `sync/watcher.py` | `watchdog` observer; skips `.obsidian/` and non-`.md` files |
| `api/events.py` | SSE endpoint at `GET /events` |

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
