# 2026-07-13 Pass 04 — Vault Registry / Multi-Workspace

_relates: [[index]]_

## What Changed
- Created `components/vault-registry.md` — the multi-workspace subsystem: in-memory `_vaults` + durable `vaults.json` dual state, one `{vault_id}.db` per vault, `activate`/`deactivate` lifecycle, `on_change` vault_id stamping, and the non-destructive remove semantics (stops watcher + drops registry entry; source `.md` and index db left untouched). Documented the `/config` HTTP surface.
- INDEX: added [[vault-registry]] to Components, a new **workspaces** concept cluster, two cross-references (→ [[markdown-source-of-truth]], → [[watcher]]), and file↔concept bindings for `vault.py`, `api/config.py`, `lib/api/config.ts`, `+page.svelte`, `setup/+page.svelte`. Bumped header to pass 03 → corrected to pass 03/04 dating.
- wiki-health: retired the stale "single shared sqlite3.Connection" gap — verified `db/connection.py` now keys connections per vault (`_conns: dict[str, sqlite3.Connection]`). Added a gap noting CLAUDE.md's single-`VAULT_PATH` description predates the multi-vault reality.

## Why
Session added the "remove workspace" UI (`+page.svelte`), exposing that the entire multi-vault registry — a significant subsystem — had zero wiki coverage and that CLAUDE.md still described a single vault. The removal's key property (non-destructive to source content) is exactly the kind of non-obvious "why" the wiki exists to hold.

## Gaps Remaining
- CLAUDE.md ↔ multi-vault reality reconciliation.
- Frontend stores, remaining HTTP API surface, table view, and col_widths still undocumented (carried from prior passes).
