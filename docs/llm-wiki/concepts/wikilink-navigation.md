# Wikilink navigation (click vs Cmd-click)
_updated: 2026-07-15 | relates: [[relation-field-resolution]], [[atomic-md-writes]], [[drawer]]_

A `[[...]]` wikilink in a record (rendered by `lib/components/shared/WikiLink.svelte`) has two navigation modes:

- **plain click** → `drawer.replace(record)`: opens the slide-in drawer (~480px, from the right) and **replaces** the current drawer content if one is already open. Navigation is replace-not-stack — the `drawer` store keeps a single active record plus a breadcrumb, not a growing stack.
- **Cmd/Ctrl + click** → full page view (`routes/[vault]/[folder]/[record]/+page.svelte`).

The drawer's `Breadcrumb` drives replace-in-place traversal. This is deliberate: rapid link-hopping through related records shouldn't bury the user under stacked panels.

The drawer also has a `'settings'` mode (opened via the header Settings button) — see [[drawer]] and [[settings-in-drawer]]. In settings mode the breadcrumb is hidden and `SettingsPanel` renders instead of `PageView`.

Note: the `[[filename]]` self-link that `writer.py` emits as the H1 (see [[atomic-md-writes]]) exists for Obsidian's graph, not for this UI's navigation. How a relation link's *target* is resolved to a record is [[relation-field-resolution]].
