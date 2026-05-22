"""Shared helpers for API routers."""

import json
import sqlite3

import vault as _vault
from fastapi import HTTPException


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


def require_vault(vault_id: str) -> None:
    """FastAPI path-parameter dependency — raises 404 if vault_id is unknown."""
    if _vault.get_vault(vault_id) is None:
        raise HTTPException(status_code=404, detail=f"Vault '{vault_id}' not found")
