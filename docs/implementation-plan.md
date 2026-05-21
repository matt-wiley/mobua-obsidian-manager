# Implementation Plan: Obsidian-Backed Task Manager

## North Star

A "Notion Lite" web UI that sits on top of an Obsidian vault. Markdown files are the source of truth. SQLite is a queryable index. The UI disappears — the work stays visible.

---

## Confirmed Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11+ · FastAPI |
| Database | SQLite (via `sqlite3` stdlib) |
| File watching | `watchdog` |
| Markdown parsing | `python-frontmatter` · `mistune` or `markdown-it-py` |
| Frontend | SvelteKit · TypeScript |
| Table | `@tanstack/svelte-table` |
| Markdown editor | CodeMirror 6 |
| Resizable panels | `svelte-splitpanes` |
| Config | `.env` via `python-dotenv` / SvelteKit `$env` |

---

## Confirmed Design Decisions

- **Vault is source of truth.** SQLite is rebuilt from vault files, never the reverse.
- **Emergent schema.** No schema declarations. Folder = table. File = record. Frontmatter keys + H2 headers = fields. Schema is the union of all fields across all files in a folder.
- **Frontmatter stored as JSON blob** in SQLite (`frontmatter` column). H2 sections stored as JSON blob (`sections` column). No dynamic `ALTER TABLE`.
- **Relation fields resolved by convention.** `project:` → looks for a `Projects/` folder first. Falls back to distinct values across the folder (free enum behavior).
- **Wikilinks are navigable everywhere.** Click opens full page or drawer. Drawer uses replace-with-breadcrumb navigation, not stacking.
- **Live editing everywhere.** No mode toggle. Table cells edit inline. Page view edits in place. Drawer edits in place.
- **H2 sections use CodeMirror 6** for inline markdown editing to preserve round-trip file fidelity.
- **Auto-height rows.** Table rows size to their tallest cell. No user configuration required.
- **Column widths persisted** per folder in `col_widths` SQLite table (UI preference, not vault data).
- **SSE for live updates.** File watcher → SQLite → SSE event → Svelte store → UI re-renders. No manual refresh. Target latency: < 500ms from Obsidian save to UI update.
- **Sync badge** always visible. Green = connected. Amber = reconnecting. Red = watcher error.

---

## SQLite Schema

```sql
CREATE TABLE records (
    id           TEXT PRIMARY KEY,      -- uuid
    folder_path  TEXT NOT NULL,         -- "Tasks/"
    file_path    TEXT NOT NULL,         -- absolute path on disk
    filename     TEXT NOT NULL,         -- "Build login page" (no extension)
    frontmatter  TEXT,                  -- JSON blob
    sections     TEXT,                  -- JSON blob  { "Overview": "...", "Work Notes": "..." }
    content_hash TEXT,                  -- md5 of raw file, skip re-index if unchanged
    updated_at   TEXT NOT NULL
);

CREATE TABLE links (
    source_id   TEXT NOT NULL,          -- records.id
    target_file TEXT NOT NULL,          -- "Projects/Q3 Rebrand.md"
    field_name  TEXT NOT NULL,          -- "project"
    FOREIGN KEY (source_id) REFERENCES records(id) ON DELETE CASCADE
);

CREATE TABLE col_widths (
    folder_path TEXT NOT NULL,
    field_name  TEXT NOT NULL,
    width       INTEGER NOT NULL,
    PRIMARY KEY (folder_path, field_name)
);
```

---

## Project Structure

```
obsidian-manager/
  backend/
    main.py              # FastAPI app entry point
    config.py            # VAULT_PATH, DB_PATH, PORT from .env
    db/
      connection.py      # SQLite connection (WAL mode, single instance)
      schema.sql         # CREATE TABLE statements
      queries.py         # All SQL as named functions (no ORM)
    models/
      record.py          # Record dataclass
      link.py            # Link dataclass
    api/
      records.py         # CRUD routes
      folders.py         # Folder list + schema aggregation
      events.py          # SSE endpoint
      sync.py            # /sync/repair route
    sync/
      parser.py          # .md file → { frontmatter, sections, links }
      indexer.py         # parsed data → SQLite upsert
      writer.py          # SQLite record → .md file on disk
      watcher.py         # watchdog setup → calls parser + indexer

  frontend/
    src/
      lib/
        api/
          client.ts      # fetch wrapper (base URL, error handling)
          records.ts     # typed API calls for records
          folders.ts     # typed API calls for folders
        components/
          table/
            DataTable.svelte      # TanStack Table wrapper
            TableCell.svelte      # routes to correct field component
            ColumnHeader.svelte   # label + resize handle
          page/
            PageView.svelte       # full record layout
            FieldBlock.svelte     # single frontmatter field (view + edit)
            SectionBlock.svelte   # single H2 section with CodeMirror
          drawer/
            Drawer.svelte         # slide-in panel
            Breadcrumb.svelte     # navigation trail inside drawer
          fields/
            TextField.svelte
            DateField.svelte
            UrlField.svelte
            RelationField.svelte  # wikilink dropdown
            EnumField.svelte      # distinct values dropdown
            MarkdownField.svelte  # CodeMirror 6
          shared/
            SyncBadge.svelte      # SSE connection indicator
            WikiLink.svelte       # clickable wikilink (opens drawer or page)
        stores/
          records.ts       # current folder's records
          schema.ts        # current folder's field list
          drawer.ts        # drawer open state + breadcrumb stack
          sync.ts          # SSE connection status
      routes/
        +layout.svelte             # app shell: nav, drawer outlet, sync badge
        +page.svelte               # home: folder list
        [folder]/
          +page.svelte             # table view
          [record]/
            +page.svelte           # full page view

  .env                   # VAULT_PATH, DB_PATH, PORT
  README.md
```

---

## Phases

---

### Phase 0 — Project Setup

**Goal:** Both processes start. Config is wired. Nothing works yet.

**Backend:**
- Create `backend/` with `main.py`, `config.py`, `.env`
- Install: `fastapi`, `uvicorn`, `watchdog`, `python-frontmatter`, `python-dotenv`
- `db/connection.py` opens SQLite in WAL mode, runs `schema.sql` on startup
- `main.py` starts FastAPI, connects to DB, returns `{"status": "ok"}` at `GET /health`

**Frontend:**
- `npm create svelte@latest frontend` (SvelteKit, TypeScript, no SSR)
- Install: `@tanstack/svelte-table`, `svelte-splitpanes`
- Install CodeMirror 6: `@codemirror/view`, `@codemirror/state`, `@codemirror/lang-markdown`
- Proxy `/api` to `http://localhost:8000` in `vite.config.ts`
- Home route renders "It works."

**Done when:** `uvicorn main:app` and `npm run dev` both start without errors. Frontend proxies to backend successfully.

---

### Phase 1 — Parser & Indexer

**Goal:** A markdown file can be fully parsed and stored in SQLite.

**Files:** `sync/parser.py`, `sync/indexer.py`, `db/queries.py`

**`parser.py`** reads a `.md` file and returns a plain dict:
```python
{
  "filename": "Build login page",
  "folder_path": "Tasks/",
  "frontmatter": { "status": "active", "priority": "high", "project": "[[Q3 Rebrand]]" },
  "sections": { "Overview": "Build the OAuth...", "Work Notes": "Blocked on..." },
  "links": [ { "field_name": "project", "target_file": "Projects/Q3 Rebrand.md" } ]
}
```

Rules:
- Frontmatter parsed via `python-frontmatter`
- H2 headers parsed by splitting raw markdown on `^## ` lines
- Wikilinks extracted with a simple regex: `\[\[(.+?)\]\]`
- Relation links (frontmatter wikilinks) captured with their field name
- Body wikilinks captured with `field_name = "__body__"`
- Type inference on frontmatter values: date pattern → `date`, `https://` prefix → `url`, numeric string → `number`, else → `text`

**`indexer.py`** takes parser output, generates a stable UUID from the file path, upserts into `records`, deletes and re-inserts `links` for that record.

**`db/queries.py`** contains all SQL as named functions. No raw SQL outside this file.

**Done when:** A unit test parses a hand-written `.md` file and the correct rows appear in SQLite.

---

### Phase 2 — Writer & Sync Loop

**Goal:** Changes in SQLite can be written back to `.md` files. File changes trigger re-indexing.

**Files:** `sync/writer.py`, `sync/watcher.py`

**`writer.py`** takes a record from SQLite and renders a `.md` file:
- YAML frontmatter block from `frontmatter` JSON
- H1 as `# [[filename]]` (self-referencing wikilink)
- Each key in `sections` JSON rendered as `## Key\n\ncontent\n\n`
- Writes atomically (write to `.tmp`, then `os.replace`)

**`watcher.py`** uses `watchdog` to watch `VAULT_PATH`:
- `on_modified` and `on_created`: parse + index the changed file
- `on_deleted`: remove the record from SQLite
- Skips files that haven't changed (compare `content_hash`)
- Skips `.obsidian/` directory and non-`.md` files

**Repair function:** `sync/indexer.py` exposes `reindex_all(vault_path)` — walks every `.md` file in the vault and re-indexes it. Used at startup and by the repair API endpoint.

**Done when:** Edit a `.md` file directly. SQLite updates. Rename a file. SQLite updates. Call `reindex_all()`. All records are correct.

---

### Phase 3 — REST API

**Goal:** The frontend has everything it needs to read and write records.

**Files:** `api/records.py`, `api/folders.py`, `api/events.py`, `api/sync.py`

**Endpoints:**

```
GET  /health                          → { status, vault_path, record_count }

GET  /folders                         → [ { name, path, record_count } ]
GET  /folders/{folder}/schema         → [ { field_name, field_type, source } ]
                                           source: "frontmatter" | "section"

GET  /folders/{folder}/records        → [ Record ]  (with optional ?sort= &filter=)
GET  /records/{id}                    → Record
POST /folders/{folder}/records        → Record  (creates .md file + indexes)
PUT  /records/{id}                    → Record  (updates SQLite + calls writer)
DELETE /records/{id}                  → 204     (deletes .md file + SQLite row)

GET  /records/{id}/relations/{field}  → [ { id, filename, folder_path } ]
                                           (dropdown options for a relation field)

GET  /events                          → SSE stream
POST /sync/repair                     → { reindexed: N }
```

`GET /folders/{folder}/schema` aggregates all `frontmatter` JSON keys and all `sections` JSON keys across every record in the folder. Returns them with inferred types. This is the call that tells the table view what columns to render.

**Done when:** All endpoints return correct data. `PUT /records/{id}` updates the `.md` file on disk. Postman or `curl` tests pass.

---

### Phase 4 — SvelteKit Foundation

**Goal:** The app shell exists. Stores are wired. SSE connection is live.

**Files:** `+layout.svelte`, `stores/`, `lib/api/`

**`lib/api/client.ts`** — a thin `fetch` wrapper that handles base URL, JSON parsing, and error throwing.

**`lib/api/records.ts`** and **`folders.ts`** — typed functions that call the API. No raw `fetch` calls outside these files.

**Stores:**
- `records` — the current folder's record list. Exposes `load(folder)`, `update(id, patch)`, `invalidate()`.
- `schema` — the current folder's field list.
- `drawer` — `{ open: boolean, record: Record | null, breadcrumbs: Record[] }`. Exposes `push(record)`, `replace(record)`, `pop()`, `close()`.
- `sync` — `{ status: 'connected' | 'reconnecting' | 'error' }`.

**`+layout.svelte`** opens an `EventSource('/api/events')` on mount. On message, calls `records.invalidate()` if the event's folder matches the current route. Updates `sync` store on open/close/error. Renders `<SyncBadge>` and the `<Drawer>` outlet.

**Done when:** Navigate to `/`. Stores initialize. SSE connection opens (verify in browser DevTools network tab). Edit a `.md` file in Obsidian. Verify the SSE event fires in the browser.

---

### Phase 5 — Field Components

**Goal:** Every field type can render itself in view mode and switch to edit mode on click. Saves on blur.

**Files:** `components/fields/`

Each field component receives: `value`, `readonly`, `onSave(newValue)`.

On click → switches to edit mode. On blur or Enter → calls `onSave`, switches back to view mode.

| Component | View | Edit |
|---|---|---|
| `TextField` | plain text | `<input type="text">` |
| `DateField` | formatted date | `<input type="date">` |
| `UrlField` | clickable link | `<input type="url">` |
| `EnumField` | badge/pill | `<select>` populated from `GET /folders/{folder}/schema` distinct values |
| `RelationField` | `<WikiLink>` | `<select>` populated from `GET /records/{id}/relations/{field}` |
| `MarkdownField` | rendered markdown | CodeMirror 6 editor |

`WikiLink.svelte` renders a wikilink value as a clickable element. On click: calls `drawer.push(record)` if a drawer is already open, else `drawer.replace(record)`. Navigates to full page if Cmd/Ctrl+Click.

**Done when:** Each field component renders correctly in both modes. Saving a `RelationField` updates the record and re-renders the wikilink. `MarkdownField` round-trips to the vault without corrupting the markdown.

---

### Phase 6 — Table View

**Goal:** A folder's records render as a live-editable, resizable table.

**Files:** `components/table/`, `routes/[folder]/+page.svelte`

**`[folder]/+page.svelte`** loads folder schema and records on mount. Passes both to `<DataTable>`.

**`DataTable.svelte`** wraps `@tanstack/svelte-table`:
- Columns built from schema — one column per field
- `TableCell.svelte` renders the correct field component based on `field_type`
- Inline edit: `onSave` in each cell calls `PUT /records/{id}`, then updates the local store
- Column resizing enabled via TanStack's `columnResizing` feature
- On resize end: `PUT /col_widths` to persist
- Row heights auto-size via CSS `height: auto` on `<tr>` — no JS needed
- First column is always the record name (filename), styled as a link that opens the page view

**Done when:** Navigate to `/Tasks`. All records render. Click a cell — it edits inline. Resize a column — width persists on refresh. Edit a cell — the `.md` file on disk updates within 500ms.

---

### Phase 7 — Page View

**Goal:** A single record renders as a full document page, fully editable.

**Files:** `components/page/`, `routes/[folder]/[record]/+page.svelte`

**`PageView.svelte`** layout:
- Record title (filename) at top — click to edit, saves by renaming the `.md` file
- Frontmatter fields rendered as a two-column property list using `<FieldBlock>`
- H2 sections rendered below as `<SectionBlock>` components, in order
- "Add field" button appends a new frontmatter key
- "Add section" button appends a new H2 section

**`FieldBlock.svelte`** — label on left, field component on right. Label is editable (renames the frontmatter key). Clicking the label's type icon cycles through available types (text → date → url → relation → enum).

**SectionBlock.svelte`** — H2 heading (editable), `<MarkdownField>` body below. Drag handle on left for reordering sections (updates section order in the writer).

**Done when:** Navigate to a record's page. All fields and sections render. Edit a field — disk updates. Edit a section body in CodeMirror — disk updates. Add a new field — appears in the table view's schema on next load.

---

### Phase 8 — Drawer & Navigation

**Goal:** Wikilinks are navigable. Drawer opens, replaces, breadcrumbs, closes.

**Files:** `components/drawer/Drawer.svelte`, `components/drawer/Breadcrumb.svelte`

**`Drawer.svelte`** slides in from the right. Renders `<PageView>` for the current `drawer.record`. Width ~480px, resizable. Closes on Escape or clicking outside.

**`Breadcrumb.svelte`** renders the `drawer.breadcrumbs` trail at the top of the drawer. Click any crumb → `drawer.replace()` back to that record.

**`WikiLink.svelte`** (already built in Phase 5) drives all navigation. By this phase it should handle:
- Click → `drawer.push(record)`
- Click while drawer is open → `drawer.replace(record)`
- Cmd/Ctrl+Click → navigate to full page view

**Done when:** Click a wikilink in a table cell. Drawer opens with that record. Click a wikilink inside the drawer. It replaces in-place with breadcrumb. Click the breadcrumb. Returns to first record.

---

### Phase 9 — Home & Folder List

**Goal:** The app has a proper entry point.

**Files:** `routes/+page.svelte`

Renders all vault folders as cards. Each card shows folder name and record count. Click navigates to the table view. "Open vault in Obsidian" button (deep link: `obsidian://open?vault=...`).

**Done when:** Home shows all folders. Clicking a folder navigates to its table view.

---

### Phase 10 — Hardening & Polish

**Goal:** The app is reliable enough for daily use.

**Sync reliability:**
- `watcher.py` restarts automatically if it crashes (wrap in a retry loop)
- `SyncBadge` goes amber after 5 seconds without a heartbeat SSE ping
- `POST /sync/repair` button visible in the UI (small link in the footer)

**Error handling:**
- Failed `PUT /records/{id}` shows an inline error on the field, reverts the value
- Failed file write logs the error and surfaces it in the sync badge

**Record operations:**
- Create new record: "New record" button in the table view header — creates a blank `.md` file, focuses the title field
- Delete record: trash icon in the page view header, confirmation dialog, deletes `.md` file

**Empty states:**
- Empty folder: "No records yet. Create one or add a `.md` file to this folder in Obsidian."
- No vault path configured: onboarding screen with a path picker

**Done when:** You use it as your actual task manager for a day without thinking about the tool.

---

## Out of Scope (v1)

- Mobile layout
- Full-text search across the vault
- Multi-user / shared vault
- Conflict resolution (simultaneous edits in UI + Obsidian at the exact same moment)
- Custom field type declarations (beyond heuristic inference)
- Attachments / images in records
- Kanban or calendar views
