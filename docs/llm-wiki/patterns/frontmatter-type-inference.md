# Frontmatter type inference
_updated: 2026-07-13 | relates: [[emergent-schema]], [[one-component-per-field-type]], [[relation-field-resolution]], [[canonical-field-options]]_

**Rule:** A frontmatter value's field type is inferred, never declared. `parser.infer_type(value)` decides, and **order matters** — first match wins:

1. non-str → `number` if `int`/`float`, else `text`
2. matches `^\d{4}-\d{2}-\d{2}$` → `date`
3. starts with `http://` / `https://` → `url`
4. contains `[[...]]` → `relation`
5. parses as `float()` → `number`
6. otherwise → `text`

**Where:** `backend/obsidian_manager/sync/parser.py` (`infer_type`, `_DATE_RE`, `_WIKILINK_RE`). Frontend field routing consumes the result — see [[one-component-per-field-type]].

**Why:** This is what makes the [[emergent-schema]] possible — no `ALTER TABLE`, no field registry. Because the date regex runs before the numeric check, a bare `2026-07-07` is a `date`, not three numbers. `relation` (step 4) is a specialization of text detected by wikilink syntax; see [[relation-field-resolution]] for how the target is then resolved. An explicit [[canonical-field-options]] list overrides this inference for a field, forcing it to `enum`.
