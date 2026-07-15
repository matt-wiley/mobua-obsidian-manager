# parser
_updated: 2026-07-15 | relates: [[frontmatter-type-inference]], [[indexer]], [[relation-field-resolution]]_

**File(s):** `backend/obsidian_manager/sync/parser.py`
**Role:** Pure function `.md` → `{ filename, folder_path, frontmatter, sections, links }`. No DB, no I/O beyond reading the one file.

**Non-obvious:**
- **Sections** are split on `^## ` (H2) only. Content before the first H2 (including the H1 self-link) is **silently discarded** — it is not a section and is never stored in SQLite. This is a known limitation: long preamble prose or notes using only H3+ headings will be invisible in the UI even though the file is intact on disk.
- **Fenced code blocks are fence-aware** (commit 6bde6b1): `_FENCE_RE` (`^[ \t]{0,3}(\`{3,}|~{3,})`) tracks open/close state across lines. A `## ` line inside a backtick or tilde fence is treated as content, not a section separator. The closing fence must use the same fence character and be at least as long as the opening (CommonMark §4.5). Unclosed fences treat the remainder of the file as content. **Re-index any affected file** (touch it or use "Repair index") to apply corrected parsing.
- **`folder_path`** is normalized to forward-slashes with a trailing `/` (`Tasks/`); a file at vault root returns `""`.
- **`links`** carry provenance: a frontmatter wikilink keeps its `field_name`; a body wikilink is tagged `field_name = "__body__"`. `_resolve_target` appends `.md` unless already present and preserves any folder prefix in the link.
- Type classification of frontmatter values lives here too — see [[frontmatter-type-inference]]. Output is consumed only by the [[indexer]]. Relation targets are later resolved per [[relation-field-resolution]].
