# Atomic .md writes via tmp + os.replace
_updated: 2026-07-07 | relates: [[markdown-source-of-truth]], [[writer]], [[watcher]], [[atomic-write-delete-debounce]]_

**Decision:** `writer.py` never writes a `.md` file in place. It writes `file.md.tmp`, then `os.replace(tmp, file.md)`.

**Why:** `os.replace` is atomic on POSIX. It guarantees a reader (Obsidian, or the watcher's own reindex) never sees a half-written file — the path either holds the old complete content or the new complete content, never a torn write. Since [[markdown-source-of-truth]] makes the file canonical, a partial write would corrupt the source.

**Consequence:**
- The atomic swap surfaces to the OS as a `deleted` + `created` pair, not a single `modified`. The [[watcher]] must not treat that transient delete as a real deletion — see [[atomic-write-delete-debounce]].
- Writer also renders the H1 as a self-referencing wikilink `# [[filename]]` so the record links to itself in the Obsidian graph. See [[writer]].
