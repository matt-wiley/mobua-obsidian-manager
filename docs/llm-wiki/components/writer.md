# writer
_updated: 2026-07-07 | relates: [[atomic-md-writes]], [[watcher]], [[markdown-source-of-truth]]_

**File(s):** `backend/obsidian_manager/sync/writer.py`
**Role:** Record data → rendered `.md` on disk. The only place the app writes vault files (see [[markdown-source-of-truth]]).

**Non-obvious:**
- `frontmatter`/`sections` args may arrive as either a `dict` or a JSON string — writer `json.loads` strings first. (They live as JSON columns in SQLite, so callers sometimes hand over the raw column value.)
- Render order is fixed: YAML frontmatter block → `# [[filename]]` self-referencing H1 wikilink → each H2 section in dict order. The self-link is intentional, for Obsidian's graph.
- YAML via `yaml.dump(..., allow_unicode=True, default_flow_style=False)`; empty frontmatter emits no `---` block at all.
- Atomic swap (`.md.tmp` → `os.replace`) per [[atomic-md-writes]] — which is exactly what forces the [[watcher]]'s delete-debounce.
