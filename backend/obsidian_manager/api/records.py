"""Record CRUD endpoints.

GET    /folders/{folder}/records          → list records in a folder
GET    /records/{id}                      → single record
POST   /folders/{folder}/records          → create record (writes .md file)
PUT    /records/{id}                      → update record (writes .md file)
DELETE /records/{id}                      → delete record and .md file
GET    /records/{id}/relations/{field}    → relation dropdown options
"""

import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import vault
from . import events
from ._helpers import folder_db_path, require_vault, row_to_dict
from ..db import queries
from ..db.connection import get_connection
from ..sync.indexer import index_file
from ..sync.writer import (
    delete_section,
    retitle_h1,
    split_document,
    upsert_section,
    write_document,
    write_record,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class RecordCreate(BaseModel):
    filename: str
    frontmatter: dict = {}
    sections: dict = {}


class SectionEdit(BaseModel):
    heading: str
    body: str = ""
    previous_heading: str | None = None  # set when renaming a section


class RecordUpdate(BaseModel):
    """A record edit expressed as an *intent*, not a whole-record replacement.

    Body edits are surgical: ``section`` upserts (or renames) exactly one H2
    section; ``delete_section`` removes one. The rest of the file is left
    byte-for-byte untouched, so content the index doesn't model is never lost.
    """

    filename: str | None = None
    frontmatter: dict | None = None
    section: SectionEdit | None = None
    delete_section: str | None = None


# ---------------------------------------------------------------------------
# List / get
# ---------------------------------------------------------------------------

@router.get("/folders/{folder}/records", dependencies=[Depends(require_vault)])
def list_records(vault_id: str, folder: str):
    conn = get_connection(vault_id)
    rows = queries.get_records_by_folder(conn, folder_db_path(folder))
    return [row_to_dict(r) for r in rows]


@router.get("/records/{record_id}", dependencies=[Depends(require_vault)])
def get_record(vault_id: str, record_id: str):
    conn = get_connection(vault_id)
    row = queries.get_record_by_id(conn, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return row_to_dict(row)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.post("/folders/{folder}/records", status_code=201, dependencies=[Depends(require_vault)])
def create_record(vault_id: str, folder: str, body: RecordCreate):
    conn = get_connection(vault_id)
    vault_path = vault.get_vault_path(vault_id)
    fp = folder_db_path(folder)
    file_path = vault_path / fp / f"{body.filename}.md"

    if file_path.exists():
        raise HTTPException(status_code=409, detail=f"'{body.filename}.md' already exists")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    write_record(
        file_path=file_path,
        filename=body.filename,
        frontmatter=body.frontmatter,
        sections=body.sections,
    )
    record_id = index_file(file_path, vault_path, conn)
    row = queries.get_record_by_id(conn, record_id)

    events.broadcast({"type": "record_changed", "folder_path": fp, "record_id": record_id, "vault_id": vault_id})
    logger.info("created record %s in %s", body.filename, fp)
    return row_to_dict(row)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@router.put("/records/{record_id}", dependencies=[Depends(require_vault)])
def update_record(vault_id: str, record_id: str, body: RecordUpdate):
    conn = get_connection(vault_id)
    vault_path = vault.get_vault_path(vault_id)
    row = queries.get_record_by_id(conn, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")

    current = row_to_dict(row)
    old_path = Path(current["file_path"])

    # Read the live file — the single source of truth. Never rebuild the body
    # from the index, or content the index doesn't model would be lost.
    if old_path.exists():
        cur_frontmatter, doc_body = split_document(old_path.read_text(encoding="utf-8"))
    else:
        cur_frontmatter, doc_body = current["frontmatter"], _fallback_body(current)

    new_frontmatter = body.frontmatter if body.frontmatter is not None else cur_frontmatter

    if body.section is not None:
        doc_body = upsert_section(
            doc_body,
            body.section.heading,
            body.section.body,
            body.section.previous_heading,
        )
    if body.delete_section is not None:
        doc_body = delete_section(doc_body, body.delete_section)

    new_filename = body.filename if body.filename is not None else current["filename"]
    if new_filename != current["filename"]:
        doc_body = retitle_h1(doc_body, current["filename"], new_filename)
    new_path = old_path.parent / f"{new_filename}.md"

    write_document(file_path=new_path, frontmatter=new_frontmatter, body=doc_body)

    if old_path != new_path:
        os.remove(old_path)
        queries.delete_record(conn, record_id)
        conn.commit()

    updated_id = index_file(new_path, vault_path, conn)
    updated_row = queries.get_record_by_id(conn, updated_id)

    events.broadcast({
        "type": "record_changed",
        "folder_path": current["folder_path"],
        "record_id": updated_id,
        "vault_id": vault_id,
    })
    return row_to_dict(updated_row)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.delete("/records/{record_id}", status_code=204, dependencies=[Depends(require_vault)])
def delete_record(vault_id: str, record_id: str):
    conn = get_connection(vault_id)
    row = queries.get_record_by_id(conn, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")

    folder_path = row["folder_path"]
    file_path = Path(row["file_path"])

    if file_path.exists():
        file_path.unlink()

    queries.delete_record(conn, record_id)
    conn.commit()

    events.broadcast({"type": "record_deleted", "folder_path": folder_path, "record_id": record_id, "vault_id": vault_id})
    logger.info("deleted record %s", record_id)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fallback_body(current: dict) -> str:
    """Reconstruct a body from the index when the .md file is missing on disk.

    Only reached if the file was deleted out from under us mid-edit; normal
    updates read the live file. Best-effort — rebuilds the H1 and known
    sections from the index.
    """
    parts = [f"\n# [[{current['filename']}]]"]
    for heading, section_body in current["sections"].items():
        parts.append(f"\n## {heading}\n\n{section_body}")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------

@router.get("/records/{record_id}/relations/{field}", dependencies=[Depends(require_vault)])
def get_relations(vault_id: str, record_id: str, field: str):
    """Return dropdown options for a relation field."""
    conn = get_connection(vault_id)
    row = queries.get_record_by_id(conn, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")

    all_folders = {f["folder_path"] for f in queries.get_all_folders(conn)}
    candidates = [
        f"{field.capitalize()}s/",
        f"{field.capitalize()}/",
        f"{field}/",
    ]

    for candidate in candidates:
        if candidate in all_folders:
            records = queries.get_records_by_folder(conn, candidate)
            return [
                {"id": r["id"], "filename": r["filename"], "folder_path": r["folder_path"]}
                for r in records
            ]

    folder_records = queries.get_records_by_folder(conn, row["folder_path"])
    seen: dict[str, None] = {}
    for r in folder_records:
        fm = json.loads(r["frontmatter"] or "{}")
        val = fm.get(field)
        if val:
            seen[str(val)] = None

    return [{"id": None, "filename": v, "folder_path": None} for v in seen]
