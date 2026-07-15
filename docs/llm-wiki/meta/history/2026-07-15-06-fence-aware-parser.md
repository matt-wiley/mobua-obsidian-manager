# 2026-07-15 Pass 06 — Fence-Aware Section Parsing
_relates: [[parser]]_

## What Changed
- Updated [[parser]] component page with two additions:
  - **Fence-awareness fix** (commit 6bde6b1): `_parse_sections` now tracks fenced code block state via `_FENCE_RE`; `## ` lines inside ` ``` ` or `~~~` fences are content, not separators. Re-index required for affected files.
  - **Preamble-drop limitation** explicitly documented: content before the first `## ` heading is silently discarded and never stored in SQLite — a known limitation, not yet fixed.

## Why
Bug surfaced when a user pasted a large markdown note (containing `## ` headings inside a fenced code block) into a section. The naïve line-by-line split split the content at those fenced `## ` lines, truncating the visible section. Fix required tracking open/close fence state per CommonMark §4.5 rules. The preamble-drop limitation was also identified during root cause analysis as a related structural constraint.

## Gaps Remaining
- Preamble-drop limitation is documented but not yet fixed; notes with significant pre-H2 content are still invisible in the UI.
