# One component per field type
_updated: 2026-07-07 | relates: [[frontmatter-type-inference]], [[all-fetch-in-lib-api]], [[relation-field-resolution]]_

**Rule:** Each frontmatter field type has exactly one Svelte component in `lib/components/fields/`: `TextField`, `DateField`, `UrlField`, `EnumField`, `RelationField`, `MarkdownField`. Each takes the same props: `value`, `readonly`, `onSave(newValue)`. Interaction contract: click → edit mode; blur/Enter → save.

**Where:** `frontend/src/lib/components/fields/`. `lib/components/table/TableCell.svelte` routes a cell to the right component; `lib/components/page/FieldBlock.svelte` does the same in the full page view.

**Why:** The field type is decided at runtime by [[frontmatter-type-inference]], so cell/field rendering must be a lookup, not a switch scattered across views. Adding a field type = add one component + one route entry, nothing else. Each component's `onSave(newValue)` persists through the API wrapper — see [[all-fetch-in-lib-api]]. Relation rendering additionally depends on [[relation-field-resolution]].
