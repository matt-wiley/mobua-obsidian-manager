# writer
_updated: 2026-07-07 | relates: [[atomic-md-writes]], [[watcher]], [[markdown-source-of-truth]], [[live-file-surgical-writes]]_

**File(s):** `backend/obsidian_manager/sync/writer.py`
**Role:** The only place the app writes vault files (see [[markdown-source-of-truth]]). Two paths: render a fresh file on create, or splice an existing one on update (see [[live-file-surgical-writes]]).

**Non-obvious:**
- **Two write paths.** `write_record` renders a whole new file (frontmatter + `# [[filename]]` self-link H1 + H2 sections in dict order) — **create only**. `write_document` writes an already-assembled `(frontmatter, verbatim body)` — used by updates.
- **Splice primitives** operate on the live file so untouched bytes survive verbatim: `split_document` (raw text → `(frontmatter_dict, verbatim_body)`), `join_document` (inverse; byte-lossless round-trip), `upsert_section`/`delete_section` (edit one H2 span, everything else preserved), `retitle_h1` (targeted `# [[old]]`→`# [[new]]`, never fabricates one).
- `split_document` slices the body verbatim via `_FRONTMATTER_RE`, not `frontmatter.loads().content` — the latter strips the leading blank line + trailing newline. The body keeps its own leading blank line so join is exact.
- `_split_blocks` splits a body into `(preamble, [(heading, verbatim_block)])`; a block runs from its `## ` line to the next `## `/EOF **including trailing blank lines**. `upsert_section` preserves that separator (`_trailing_newlines`) so spacing is stable and appended sections are separated by one blank line.
- `write_record`/`write_document` share `_atomic_write` (`.md.tmp` → `os.replace`, see [[atomic-md-writes]]) — which is what forces the [[watcher]]'s delete-debounce.
- `write_record` still accepts `frontmatter`/`sections` as `dict` or JSON string (they're JSON columns in SQLite); empty frontmatter emits no `---` block.
