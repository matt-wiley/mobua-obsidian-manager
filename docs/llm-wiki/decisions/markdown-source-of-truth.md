# Markdown is the only source of truth
_updated: 2026-07-07 | relates: [[atomic-md-writes]], [[stable-uuid-and-hash-skip]], [[emergent-schema]]_

**Decision:** `.md` files in the Obsidian vault are the sole source of truth. SQLite is a rebuildable index, never authoritative.

**Why:** The vault must stay fully usable inside Obsidian itself. Any state that lived only in SQLite would be invisible/lossy to a user editing files directly. Keeping markdown canonical means the two editing surfaces (Obsidian, this web UI) never diverge.

**Consequence:**
- Every write path ends at a `.md` file on disk (see [[atomic-md-writes]]); the DB is updated only as a downstream effect of the file change, via the watcher → parser → indexer chain.
- The DB can be wiped and rebuilt at any time from the vault (`reindex_all`) with no data loss.
- Record identity cannot come from an autoincrement DB column — it must derive from the file itself (see [[stable-uuid-and-hash-skip]]).
- The schema is not declared anywhere; it is inferred from file contents (see [[emergent-schema]]).
