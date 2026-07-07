# Wiki Schema
_updated: 2026-07-07_

Read this before every write. Taxonomy for the mobua-obsidian-manager wiki: a "Notion Lite" web UI (SvelteKit) over an Obsidian vault, backed by FastAPI + a rebuildable SQLite index.

## Content types

### decision
- **directory**: decisions/
- **purpose**: an architectural/design choice + the WHY behind it (the tradeoff, not the mechanics)
- **template**:
  ```
  # <Title>
  _updated: YYYY-MM-DD | relates: [[slug]]_

  **Decision:** <one line>
  **Why:** <the tradeoff / constraint that forced it>
  **Consequence:** <what this obligates elsewhere>
  ```
- **sub-index threshold**: 8 entries

### pattern
- **directory**: patterns/
- **purpose**: a recurring implementation convention to follow when writing code here
- **template**:
  ```
  # <Title>
  _updated: YYYY-MM-DD | relates: [[slug]]_

  **Rule:** <the convention>
  **Where:** <files/dirs it governs>
  **Why:** <what breaks if ignored>
  ```
- **sub-index threshold**: 8 entries

### concept
- **directory**: concepts/
- **purpose**: a domain term or behavior with project-specific meaning (not obvious from any single file)
- **template**:
  ```
  # <Title>
  _updated: YYYY-MM-DD | relates: [[slug]]_

  <dense explanation, project-specific semantics only>
  ```
- **sub-index threshold**: 8 entries

### component
- **directory**: components/
- **purpose**: a module/subsystem's role + its NON-OBVIOUS behavior and cross-module ties. Never restate code line-by-line.
- **template**:
  ```
  # <Title>
  _updated: YYYY-MM-DD | relates: [[slug]]_

  **File(s):** `path`
  **Role:** <one line>
  **Non-obvious:** <gotchas, edge-case handling, why it's shaped this way>
  ```
- **sub-index threshold**: 8 entries

## Conventions
- Filenames: lowercase kebab-case slugs, `.md` (`atomic-md-writes.md`).
- Second line of every page: `_updated: YYYY-MM-DD | relates: [[slug]], ..._`.
- `relates:` frontmatter and inline `[[slug]]` links are exact mirrors — every slug in one appears in the other.
- Wikilinks target wiki pages only. Source code paths stay as plain `inline code`, never wikilinked.
- No ghost links: only `[[slug]]` that resolve to a real file.
- Keep files ≤100 lines. Flag and propose a split if exceeded.

## Change log
- 2026-07-07: schema bootstrapped — 4 types (decision, pattern, concept, component). Component type added at user request beyond the default 3.
