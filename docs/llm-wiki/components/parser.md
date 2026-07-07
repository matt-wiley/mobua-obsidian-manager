# parser
_updated: 2026-07-07 | relates: [[frontmatter-type-inference]], [[indexer]], [[relation-field-resolution]]_

**File(s):** `backend/obsidian_manager/sync/parser.py`
**Role:** Pure function `.md` → `{ filename, folder_path, frontmatter, sections, links }`. No DB, no I/O beyond reading the one file.

**Non-obvious:**
- **Sections** are split on `^## ` (H2) only. Content before the first H2 (including the H1 self-link) is discarded — it is not a section. Nested H3+ stays inside its parent H2's body text.
- **`folder_path`** is normalized to forward-slashes with a trailing `/` (`Tasks/`); a file at vault root returns `""`.
- **`links`** carry provenance: a frontmatter wikilink keeps its `field_name`; a body wikilink is tagged `field_name = "__body__"`. `_resolve_target` appends `.md` unless already present and preserves any folder prefix in the link.
- Type classification of frontmatter values lives here too — see [[frontmatter-type-inference]]. Output is consumed only by the [[indexer]]. Relation targets are later resolved per [[relation-field-resolution]].
