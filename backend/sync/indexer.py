"""Index .md files into SQLite.

Entry points:
  index_file(file_path, vault_path, conn)  — parse + upsert one file
  reindex_all(vault_path, conn)            — walk the vault and re-index everything
"""

import hashlib
import uuid
from pathlib import Path
import sqlite3

from db import queries
from sync.parser import parse_file


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def index_file(file_path: Path, vault_path: Path, conn: sqlite3.Connection) -> str:
    """Parse and upsert a single .md file. Returns the record id."""
    content_hash = _md5(file_path)

    existing = queries.get_record_by_file_path(conn, str(file_path))
    if existing and existing["content_hash"] == content_hash:
        return existing["id"]

    parsed = parse_file(file_path, vault_path)
    record_id = _stable_uuid(file_path)

    queries.upsert_record(
        conn,
        id=record_id,
        folder_path=parsed["folder_path"],
        file_path=str(file_path),
        filename=parsed["filename"],
        frontmatter=parsed["frontmatter"],
        sections=parsed["sections"],
        content_hash=content_hash,
    )
    queries.replace_links(conn, record_id, parsed["links"])
    conn.commit()

    return record_id


def reindex_all(vault_path: Path, conn: sqlite3.Connection) -> int:
    """Walk every .md file in the vault and index it. Returns count of files processed."""
    count = 0
    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue
        index_file(md_file, vault_path, conn)
        count += 1
    return count


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _md5(file_path: Path) -> str:
    return hashlib.md5(file_path.read_bytes()).hexdigest()


def _stable_uuid(file_path: Path) -> str:
    """Generate a deterministic UUID from the absolute file path."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, str(file_path)))
