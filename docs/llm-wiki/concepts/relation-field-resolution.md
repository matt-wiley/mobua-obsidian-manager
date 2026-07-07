# Relation field resolution
_updated: 2026-07-07 | relates: [[frontmatter-type-inference]], [[wikilink-navigation]], [[one-component-per-field-type]]_

When a frontmatter value is typed `relation` (contains `[[...]]`, see [[frontmatter-type-inference]]), the `RelationField` must offer candidate targets. Resolution order:

1. Look for a folder matching the field name, capitalized + pluralized-ish — e.g. a `project:` field looks for a `Projects/` folder and uses its records as the relation's target set.
2. **Fallback:** if no such folder exists, use the distinct existing values of that field *within the current folder* as an enum-like candidate set.

So a relation degrades gracefully into a self-referential enum when there's no dedicated collection to point at — which is why `RelationField` (one of the [[one-component-per-field-type]] set) sometimes behaves like an enum picker. Link extraction itself happens in `parser._extract_links`: frontmatter links carry their `field_name`; body links are tagged `__body__`. Navigating a resolved relation follows [[wikilink-navigation]].
