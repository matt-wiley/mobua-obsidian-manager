"""Write a record back to a .md file on disk.

Two write paths:

  * ``write_record`` — renders a *brand-new* file from scratch
    (frontmatter + ``# [[title]]`` H1 + H2 sections). Used only on create.

  * ``write_document`` — writes an already-assembled document
    (frontmatter block + verbatim body). Used by updates, which read the
    live file and *splice* only what changed rather than regenerating it.

The .md file on disk is the single source of truth. Updates never
reconstruct the body from the SQLite index — they edit the file in place
via the ``split_document`` / ``upsert_section`` / ``delete_section`` /
``retitle_h1`` primitives, so any content the index doesn't model
(preamble, custom H1, non-section prose) survives untouched.

All writes are atomic: file.md.tmp → os.replace → file.md
"""

import json
import logging
import os
import re
from pathlib import Path

import frontmatter as fm
import yaml

logger = logging.getLogger(__name__)

# Matches a leading YAML frontmatter block, consuming the newline after the
# closing '---' so the remaining body is byte-verbatim.
_FRONTMATTER_RE = re.compile(r"^---[ \t]*\n.*?\n---[ \t]*\n?", re.DOTALL)


# ---------------------------------------------------------------------------
# Create path — render a fresh file
# ---------------------------------------------------------------------------

def write_record(
    *,
    file_path: Path,
    filename: str,
    frontmatter: dict | str,
    sections: dict | str,
) -> None:
    """Render and atomically write a *new* .md file from record data.

    Args:
        file_path:   Absolute path to the target .md file.
        filename:    Record name (used for the H1 wikilink).
        frontmatter: Frontmatter dict (or JSON string).
        sections:    Sections dict {heading: body} (or JSON string).
    """
    if isinstance(frontmatter, str):
        frontmatter = json.loads(frontmatter)
    if isinstance(sections, str):
        sections = json.loads(sections)

    _atomic_write(file_path, _render(filename, frontmatter, sections))
    logger.info("wrote %s", file_path.name)


# ---------------------------------------------------------------------------
# Update path — write an assembled document
# ---------------------------------------------------------------------------

def write_document(*, file_path: Path, frontmatter: dict, body: str) -> None:
    """Atomically write a document assembled from a frontmatter dict and a
    verbatim body (everything after the frontmatter block)."""
    _atomic_write(file_path, join_document(frontmatter, body))
    logger.info("wrote %s", file_path.name)


# ---------------------------------------------------------------------------
# Document primitives (frontmatter block ⇄ verbatim body)
# ---------------------------------------------------------------------------

def split_document(text: str) -> tuple[dict, str]:
    """Split raw file text into (frontmatter_dict, verbatim_body).

    The body is returned byte-for-byte (including its leading blank line),
    so re-joining an unmodified document is lossless.
    """
    fm_dict = dict(fm.loads(text).metadata)
    match = _FRONTMATTER_RE.match(text)
    body = text[match.end():] if match else text
    return fm_dict, body


def render_frontmatter_block(frontmatter: dict) -> str:
    """Render the ``---\\n…\\n---\\n`` block, or '' when there is no frontmatter."""
    if not frontmatter:
        return ""
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).rstrip()
    return f"---\n{fm_str}\n---\n"


def join_document(frontmatter: dict, body: str) -> str:
    """Recombine a frontmatter block and a verbatim body into file text."""
    block = render_frontmatter_block(frontmatter)
    if not block:
        return body
    # body already carries its own leading blank line when one existed.
    return block + body


# ---------------------------------------------------------------------------
# Surgical body edits — touch only the targeted span
# ---------------------------------------------------------------------------

def upsert_section(
    body: str,
    heading: str,
    content: str,
    previous_heading: str | None = None,
) -> str:
    """Set the content of an H2 section, preserving everything else verbatim.

    * ``previous_heading`` set (rename) → locate that section and replace both
      its heading and content.
    * heading found → replace its content in place.
    * heading missing → append a new section at the end.
    """
    preamble, blocks = _split_blocks(body)
    target = previous_heading if previous_heading is not None else heading

    for i, (h, block_text) in enumerate(blocks):
        if h == target:
            blocks[i] = (heading, _render_block(heading, content, _trailing_newlines(block_text)))
            return preamble + "".join(bt for _, bt in blocks)

    # Not found — append.
    new_block = _render_block(heading, content, "\n")
    base = (preamble + "".join(bt for _, bt in blocks)).rstrip("\n")
    if base:
        return base + "\n\n" + new_block
    return new_block


def delete_section(body: str, heading: str) -> str:
    """Remove an H2 section (heading + its content); no-op if absent."""
    preamble, blocks = _split_blocks(body)
    kept = [(h, bt) for h, bt in blocks if h != heading]
    if len(kept) == len(blocks):
        return body
    return preamble + "".join(bt for _, bt in kept)


def retitle_h1(body: str, old_filename: str, new_filename: str) -> str:
    """Update a self-referencing ``# [[old]]`` H1 to ``# [[new]]``.

    Leaves the body unchanged if no such H1 exists — never fabricates one.
    """
    pattern = re.compile(
        r"^(#[ \t]+\[\[)" + re.escape(old_filename) + r"(\]\][ \t]*)$",
        re.MULTILINE,
    )
    return pattern.sub(lambda m: m.group(1) + new_filename + m.group(2), body, count=1)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _atomic_write(file_path: Path, content: str) -> None:
    tmp = file_path.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, file_path)


def _render(filename: str, frontmatter: dict, sections: dict) -> str:
    parts: list[str] = []

    if frontmatter:
        fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).rstrip()
        parts.append(f"---\n{fm_str}\n---")

    parts.append(f"\n# [[{filename}]]")

    for heading, body in sections.items():
        parts.append(f"\n## {heading}\n\n{body}")

    return "\n".join(parts) + "\n"


def _split_blocks(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a body into (preamble, [(heading, block_text), …]).

    ``preamble`` is everything before the first ``## `` line. Each block_text is
    the verbatim text of one H2 section, from its heading line up to (excluding)
    the next H2 line or EOF — trailing blank lines included.
    """
    preamble_lines: list[str] = []
    blocks: list[tuple[str, list[str]]] = []
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            blocks.append((line[3:].strip(), [line]))
        elif blocks:
            blocks[-1][1].append(line)
        else:
            preamble_lines.append(line)
    return "".join(preamble_lines), [(h, "".join(ls)) for h, ls in blocks]


def _trailing_newlines(block_text: str) -> str:
    """Return the run of trailing '\\n' at the end of a block (its separator)."""
    stripped = block_text.rstrip("\n")
    return block_text[len(stripped):] or "\n"


def _render_block(heading: str, content: str, trailing: str) -> str:
    """Render a section as ``## heading\\n\\ncontent`` + preserved trailing run."""
    head = f"## {heading}"
    content = content.strip("\n")
    body = f"{head}\n\n{content}" if content else head
    return body + trailing
