# 2026-07-07 Pass 02 — Live-file surgical writes (data-loss fix)

_relates: [[index]]_

## What Changed
- New decision page [[live-file-surgical-writes]] — updates read the live `.md` and splice one span; never regenerate from the index.
- Rewrote [[writer]] page: documents the two write paths (`write_record` create-only vs `write_document`) and the splice primitives (`split_document`, `join_document`, `upsert_section`, `delete_section`, `retitle_h1`).
- [[markdown-source-of-truth]]: added consequence + cross-ref tying "index is rebuildable" to "writes must trust the file, not the index".
- INDEX: added the decision, extended the write-path cluster, added a cross-ref and the `api/records.py` file binding.
- wiki-health: pass-02 status (19 pages, 3 decisions); logged the shared-connection smell as a known gap.

## Why
Root cause of a real data-loss bug: `update_record` reconstructed the whole file from the SQLite index (frontmatter + regenerated H1 + sections), so a `Status` field edit erased both H2 sections + preamble when the index lagged/couldn't model them. Fix makes the file authoritative on write and expresses edits as intents (`section`/`delete_section`) instead of a whole-record `sections` dict. This is a durable architectural decision, hence a decision page rather than only a component note.

## Gaps Remaining
- `api/records.py` HTTP surface still not a full component page (only bound via the new decision).
- Shared single `sqlite3.Connection` across threads undocumented as its own page.
