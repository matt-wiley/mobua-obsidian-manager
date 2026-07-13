"""Folder and schema endpoints.

GET /folders                            → list of folders with record counts
GET /folders/{folder}/schema            → union of all field names + inferred types
GET    /folders/{folder}/field-options          → canonical option lists {field: [...]}
PUT    /folders/{folder}/field-options/{field}  → set a field's canonical options
DELETE /folders/{folder}/field-options/{field}  → clear a field's canonical options
GET /folders/{folder}/col_widths        → saved column widths for the folder
PUT /folders/{folder}/col_widths/{field}→ save a column width
GET /folders/{folder}/views             → saved views for the folder
POST /folders/{folder}/views            → create a view
DELETE /folders/{folder}/views/{id}     → delete a view
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ._helpers import folder_db_path, require_vault
from .. import schema_config
from .. import vault as _vault
from ..db import queries
from ..db.connection import get_connection
from ..sync.parser import infer_type

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/folders", dependencies=[Depends(require_vault)])
def list_folders(vault_id: str):
    conn = get_connection(vault_id)
    rows = queries.get_all_folders(conn)
    return [
        {
            "name": row["folder_path"].rstrip("/"),
            "path": row["folder_path"],
            "record_count": row["record_count"],
        }
        for row in rows
    ]


@router.get("/folders/{folder}/schema", dependencies=[Depends(require_vault)])
def folder_schema(vault_id: str, folder: str):
    conn = get_connection(vault_id)
    fp = folder_db_path(folder)

    records = queries.get_records_by_folder(conn, fp)
    if not records:
        raise HTTPException(status_code=404, detail=f"Folder '{folder}' not found")

    fm_keys = queries.get_folder_frontmatter_keys(conn, fp)
    section_keys = queries.get_folder_section_keys(conn, fp)

    vault_path = _vault.get_vault_path(vault_id)
    canonical = schema_config.get_folder_field_options(vault_path, folder)

    schema = []
    for key in fm_keys:
        values = _collect_field_values(records, "frontmatter", key)
        sample = values[0] if values else None
        field_type = infer_type(sample) if sample is not None else "text"
        entry: dict = {"field_name": key, "field_type": field_type, "source": "frontmatter"}
        if key in canonical:
            # Explicit config wins: promote to enum and keep canonical order,
            # appending any in-use values not in the list so nothing is unselectable.
            fixed = canonical[key]
            seen = [str(v) for v in values if isinstance(v, str) and v.strip()]
            entry["field_type"] = "enum"
            entry["options"] = fixed + [v for v in dict.fromkeys(seen) if v not in fixed]
        elif field_type == "text":
            enum_opts = _detect_enum(values)
            if enum_opts is not None:
                entry["field_type"] = "enum"
                entry["options"] = enum_opts
        schema.append(entry)
    for key in section_keys:
        schema.append({
            "field_name": key,
            "field_type": "markdown",
            "source": "section",
        })

    return schema


@router.get("/folders/{folder}/field-options", dependencies=[Depends(require_vault)])
def get_field_options(vault_id: str, folder: str):
    """Return the explicitly-configured canonical options: {field: [options...]}."""
    vault_path = _vault.get_vault_path(vault_id)
    return schema_config.get_folder_field_options(vault_path, folder)


class FieldOptionsBody(BaseModel):
    options: list[str]


@router.put("/folders/{folder}/field-options/{field}", status_code=204, dependencies=[Depends(require_vault)])
def set_field_options(vault_id: str, folder: str, field: str, body: FieldOptionsBody):
    vault_path = _vault.get_vault_path(vault_id)
    schema_config.set_field_options(vault_path, folder, field, body.options)


@router.delete("/folders/{folder}/field-options/{field}", status_code=204, dependencies=[Depends(require_vault)])
def delete_field_options(vault_id: str, folder: str, field: str):
    vault_path = _vault.get_vault_path(vault_id)
    schema_config.delete_field_options(vault_path, folder, field)


class ColWidthBody(BaseModel):
    width: int


@router.get("/folders/{folder}/col_widths", dependencies=[Depends(require_vault)])
def get_col_widths(vault_id: str, folder: str):
    conn = get_connection(vault_id)
    fp = folder_db_path(folder)
    rows = queries.get_col_widths(conn, fp)
    return {row["field_name"]: row["width"] for row in rows}


@router.put("/folders/{folder}/col_widths/{field}", status_code=204, dependencies=[Depends(require_vault)])
def set_col_width(vault_id: str, folder: str, field: str, body: ColWidthBody):
    conn = get_connection(vault_id)
    fp = folder_db_path(folder)
    queries.upsert_col_width(conn, fp, field, body.width)


class ViewBody(BaseModel):
    name: str
    filters: list
    sort: list
    col_order: list
    hidden_cols: list


@router.get("/folders/{folder}/views", dependencies=[Depends(require_vault)])
def list_views(vault_id: str, folder: str):
    conn = get_connection(vault_id)
    fp = folder_db_path(folder)
    rows = queries.get_views(conn, fp)
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "filters": json.loads(row["filters"]),
            "sort": json.loads(row["sort"]),
            "col_order": json.loads(row["col_order"]),
            "hidden_cols": json.loads(row["hidden_cols"]),
        }
        for row in rows
    ]


@router.post("/folders/{folder}/views", status_code=201, dependencies=[Depends(require_vault)])
def create_view(vault_id: str, folder: str, body: ViewBody):
    conn = get_connection(vault_id)
    fp = folder_db_path(folder)
    view_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    queries.create_view(
        conn,
        id=view_id,
        folder_path=fp,
        name=body.name,
        filters=body.filters,
        sort=body.sort,
        col_order=body.col_order,
        hidden_cols=body.hidden_cols,
        created_at=created_at,
    )
    return {
        "id": view_id,
        "name": body.name,
        "filters": body.filters,
        "sort": body.sort,
        "col_order": body.col_order,
        "hidden_cols": body.hidden_cols,
    }


@router.delete("/folders/{folder}/views/{view_id}", status_code=204, dependencies=[Depends(require_vault)])
def delete_view(vault_id: str, folder: str, view_id: str):
    conn = get_connection(vault_id)
    queries.delete_view(conn, view_id)


def _collect_field_values(records, column: str, key: str) -> list:
    """Return all non-null values for `key` across all records."""
    values = []
    for row in records:
        data = json.loads(row[column] or "{}")
        v = data.get(key)
        if v is not None:
            values.append(v)
    return values


_MAX_ENUM_DISTINCT = 10
_MAX_ENUM_VALUE_LEN = 30


def _detect_enum(values: list) -> list[str] | None:
    """Return sorted distinct options if values look tag-like, else None.

    Heuristics:
    - At least 2 records have a non-empty string value
    - At most 10 distinct values
    - All values are ≤ 30 characters (short, tag-like)
    """
    str_values = [v for v in values if isinstance(v, str) and v.strip()]
    if len(str_values) < 2:
        return None
    distinct = list(dict.fromkeys(str_values))
    if len(distinct) > _MAX_ENUM_DISTINCT:
        return None
    if any(len(v) > _MAX_ENUM_VALUE_LEN for v in distinct):
        return None
    return sorted(distinct)
