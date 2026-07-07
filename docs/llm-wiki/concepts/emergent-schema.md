# Emergent schema
_updated: 2026-07-07 | relates: [[markdown-source-of-truth]], [[frontmatter-type-inference]], [[all-sql-in-queries]]_

There is no declared table schema for user data. Structure emerges from the vault's shape:

- **folder** = a table/collection concept
- **file** = a record
- **frontmatter keys + H2 headings** = the fields/columns

`GET /folders/{folder}/schema` aggregates the distinct frontmatter keys across a folder's records **at query time** — the column set is computed, never stored. Field *types* come from [[frontmatter-type-inference]]. Because of this, **there is never an `ALTER TABLE`**: the three fixed SQLite tables (`records`, `links`, `col_widths`) hold `frontmatter` and `sections` as JSON blobs, and "adding a field" is just writing a new frontmatter key into a `.md` file.

This is the direct consequence of [[markdown-source-of-truth]]: the schema can't be authoritative in the DB when the DB is rebuildable. All the SQL that reads these JSON columns is centralized per [[all-sql-in-queries]].
