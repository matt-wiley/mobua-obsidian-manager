# All SQL lives in db/queries.py
_updated: 2026-07-07 | relates: [[all-fetch-in-lib-api]], [[emergent-schema]]_

**Rule:** Every raw SQL statement lives in `backend/obsidian_manager/db/queries.py`. No SQL anywhere else in the backend. Callers use the typed functions (`get_record_by_file_path`, `upsert_record`, `replace_links`, `delete_record_by_file_path`, ...).

**Where:** all of `backend/obsidian_manager/`. `db/connection.py` owns the single WAL-mode connection; `queries.py` owns statements.

**Why:** One chokepoint for schema knowledge keeps the [[emergent-schema]] model honest — there is no ORM and no scattered string SQL to drift. It also localizes JSON (de)serialization of the `frontmatter`/`sections` columns and the date-encoding fix (frontmatter `datetime.date` → ISO string happens here, not at call sites).

**Note:** mirror rule on the frontend is [[all-fetch-in-lib-api]].
