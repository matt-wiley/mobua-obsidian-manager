"""Parse a single .md file into a plain dict.

Returns:
    {
        "filename":    "Build login page",
        "folder_path": "Tasks/",
        "frontmatter": { "status": "active", ... },
        "sections":    { "Overview": "...", "Work Notes": "..." },
        "links":       [ { "field_name": "project", "target_file": "Projects/Q3 Rebrand.md" } ]
    }
"""

import re
from pathlib import Path

import frontmatter as fm

_WIKILINK_RE = re.compile(r"\[\[(.+?)\]\]")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_file(file_path: Path, vault_path: Path) -> dict:
    raw = file_path.read_text(encoding="utf-8")
    post = fm.loads(raw)

    folder_path = _folder_path(file_path, vault_path)
    filename = file_path.stem

    frontmatter_data = dict(post.metadata)
    sections = _parse_sections(post.content)
    links = _extract_links(frontmatter_data, post.content)

    return {
        "filename": filename,
        "folder_path": folder_path,
        "frontmatter": frontmatter_data,
        "sections": sections,
        "links": links,
    }


# ---------------------------------------------------------------------------
# Type inference
# ---------------------------------------------------------------------------

def infer_type(value) -> str:
    if not isinstance(value, str):
        return "number" if isinstance(value, (int, float)) else "text"
    if _DATE_RE.match(value):
        return "date"
    if value.startswith("https://") or value.startswith("http://"):
        return "url"
    if _WIKILINK_RE.search(value):
        return "relation"
    try:
        float(value)
        return "number"
    except ValueError:
        pass
    return "text"


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _folder_path(file_path: Path, vault_path: Path) -> str:
    """Return e.g. 'Tasks/' — the immediate parent folder relative to vault root."""
    rel = file_path.relative_to(vault_path)
    if len(rel.parts) < 2:
        return ""
    # Always normalise to forward slashes with trailing /
    return "/".join(rel.parts[:-1]) + "/"


def _parse_sections(body: str) -> dict[str, str]:
    """Split markdown body on H2 headings. Returns { heading: content }."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


def _extract_links(frontmatter_data: dict, body: str) -> list[dict]:
    links: list[dict] = []

    # Frontmatter wikilinks — carry the field name
    for field_name, value in frontmatter_data.items():
        if not isinstance(value, str):
            continue
        for match in _WIKILINK_RE.finditer(value):
            target = match.group(1).strip()
            links.append({
                "field_name": field_name,
                "target_file": _resolve_target(target),
            })

    # Body wikilinks — field_name = "__body__"
    for match in _WIKILINK_RE.finditer(body):
        target = match.group(1).strip()
        links.append({
            "field_name": "__body__",
            "target_file": _resolve_target(target),
        })

    return links


def _resolve_target(raw: str) -> str:
    """Convert a wikilink target like 'Q3 Rebrand' to 'Q3 Rebrand.md'.

    If the target already contains a folder prefix (e.g. 'Projects/Q3 Rebrand')
    we preserve it. Otherwise we just append .md.
    """
    if not raw.endswith(".md"):
        raw = raw + ".md"
    return raw
