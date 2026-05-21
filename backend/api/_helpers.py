"""Shared helpers for API routers."""

import json
import sqlite3


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "folder_path": row["folder_path"],
        "file_path": row["file_path"],
        "filename": row["filename"],
        "frontmatter": json.loads(row["frontmatter"] or "{}"),
        "sections": json.loads(row["sections"] or "{}"),
        "content_hash": row["content_hash"],
        "updated_at": row["updated_at"],
    }


def folder_db_path(folder: str) -> str:
    """Convert a URL folder param ('Tasks') to the DB folder_path ('Tasks/')."""
    return folder.rstrip("/") + "/"
