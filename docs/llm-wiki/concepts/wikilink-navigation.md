# Wikilink navigation (click vs Cmd-click)
_updated: 2026-07-07 | relates: [[relation-field-resolution]], [[atomic-md-writes]]_

A `[[...]]` wikilink in a record (rendered by `lib/components/shared/WikiLink.svelte`) has two navigation modes:

- **plain click** → `drawer.replace(record)`: opens the slide-in drawer (~480px, from the right) and **replaces** the current drawer content if one is already open. Navigation is replace-not-stack — the `drawer` store keeps a single active record plus a breadcrumb, not a growing stack.
- **Cmd/Ctrl + click** → full page view (`routes/[vault]/[folder]/[record]/+page.svelte`).

The drawer's `Breadcrumb` drives replace-in-place traversal. This is deliberate: rapid link-hopping through related records shouldn't bury the user under stacked panels.

Note: the `[[filename]]` self-link that `writer.py` emits as the H1 (see [[atomic-md-writes]]) exists for Obsidian's graph, not for this UI's navigation. How a relation link's *target* is resolved to a record is [[relation-field-resolution]].
