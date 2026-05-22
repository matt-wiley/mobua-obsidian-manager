"""Folder and schema endpoints.

GET /folders                            → list of folders with record counts
GET /folders/{folder}/schema            → union of all field names + inferred types
GET /folders/{folder}/col_widths        → saved column widths for the folder
PUT /folders/{folder}/col_widths/{field}→ save a column width
"""

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api._helpers import folder_db_path
from db import queries
from db.connection import get_connection
from sync.parser import infer_type

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/folders")
def list_folders():
    conn = get_connection()
    rows = queries.get_all_folders(conn)
    return [
        {
            "name": row["folder_path"].rstrip("/"),
            "path": row["folder_path"],
            "record_count": row["record_count"],
        }
        for row in rows
    ]


@router.get("/folders/{folder}/schema")
def folder_schema(folder: str):
    conn = get_connection()
    fp = folder_db_path(folder)

    records = queries.get_records_by_folder(conn, fp)
    if not records:
        raise HTTPException(status_code=404, detail=f"Folder '{folder}' not found")

    fm_keys = queries.get_folder_frontmatter_keys(conn, fp)
    section_keys = queries.get_folder_section_keys(conn, fp)

    schema = []
    for key in fm_keys:
        sample = _sample_value(records, "frontmatter", key)
        schema.append({
            "field_name": key,
            "field_type": infer_type(sample) if sample is not None else "text",
            "source": "frontmatter",
        })
    for key in section_keys:
        schema.append({
            "field_name": key,
            "field_type": "markdown",
            "source": "section",
        })

    return schema


class ColWidthBody(BaseModel):
    width: int


@router.get("/folders/{folder}/col_widths")
def get_col_widths(folder: str):
    conn = get_connection()
    fp = folder_db_path(folder)
    rows = queries.get_col_widths(conn, fp)
    return {row["field_name"]: row["width"] for row in rows}


@router.put("/folders/{folder}/col_widths/{field}", status_code=204)
def set_col_width(folder: str, field: str, body: ColWidthBody):
    conn = get_connection()
    fp = folder_db_path(folder)
    queries.upsert_col_width(conn, fp, field, body.width)


def _sample_value(records, column: str, key: str):
    """Return the first non-null value for `key` across all records."""
    for row in records:
        data = json.loads(row[column] or "{}")
        if key in data and data[key] is not None:
            return data[key]
    return None
