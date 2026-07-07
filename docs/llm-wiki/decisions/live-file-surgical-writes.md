# Updates read the live file and splice, never regenerate

_updated: 2026-07-07 | relates: [[markdown-source-of-truth]], [[writer]], [[watcher]]_

**Decision:** A record update reads the current `.md` file as its source of truth and edits only the changed span (one frontmatter block, or one H2 section). It never rebuilds the whole file from the SQLite index.

**Why:** The old `update_record` reconstructed the entire file from the index (`frontmatter` + regenerated `# [[filename]]` H1 + `sections` dict). The index is rebuildable and can lag disk (missed/stale [[watcher]] event, `content_hash` skip), and it structurally cannot represent preamble prose, a custom H1, or any non-H2 body text. So a single field edit could silently erase everything the index didn't model — confirmed data loss: changing a `Status` field wiped both H2 sections and the preamble, leaving only frontmatter + H1. This directly violated [[markdown-source-of-truth]]: the writer treated the rebuildable index as authoritative for content it then destroyed.

**Consequence:**
- The write contract is intent-based, not whole-record. `RecordUpdate` carries `frontmatter` (full block replace), `section` (`{heading, body, previous_heading?}` — upsert or rename), and `delete_section`. The frontend sends deltas (`DataTable`, `PageView`), not a whole `sections` dict.
- [[writer]] gained splice primitives that keep untouched bytes verbatim: `split_document`, `join_document`, `upsert_section`, `delete_section`, `retitle_h1`, `write_document`. `split_document`→`join_document` is a byte-lossless round-trip.
- `write_record` (whole-file render) is now used **only on create**. Updates go through `write_document`.
- Index staleness is now harmless for data loss — the file, not the index, drives the write. (The shared single `sqlite3.Connection` across [[watcher]] + API threads remains a separate, still-open robustness smell.)
- Renaming a record retitles the H1 via `retitle_h1` (targeted line edit); it never fabricates an H1 if none exists.
