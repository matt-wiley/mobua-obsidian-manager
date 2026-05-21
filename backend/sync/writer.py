"""Write a record back to a .md file on disk.

Renders:
  - YAML frontmatter block
  - H1 self-referencing wikilink
  - H2 sections in order

Writes atomically: file.md.tmp → os.replace → file.md
"""

import json
import os
from pathlib import Path

import yaml


def write_record(
    *,
    file_path: Path,
    filename: str,
    frontmatter: dict | str,
    sections: dict | str,
) -> None:
    """Render and atomically write a .md file from record data.

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

    content = _render(filename, frontmatter, sections)

    tmp = file_path.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, file_path)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render(filename: str, frontmatter: dict, sections: dict) -> str:
    parts: list[str] = []

    if frontmatter:
        fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).rstrip()
        parts.append(f"---\n{fm_str}\n---")

    parts.append(f"\n# [[{filename}]]")

    for heading, body in sections.items():
        parts.append(f"\n## {heading}\n\n{body}")

    return "\n".join(parts) + "\n"
