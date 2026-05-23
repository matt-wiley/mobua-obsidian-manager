"""All SQL lives here. No raw SQL outside this module."""

import json
import sqlite3
from datetime import date, datetime, timezone


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)


def _dumps(obj) -> str:
    return json.dumps(obj, cls=_Encoder)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

def upsert_record(
    conn: sqlite3.Connection,
    *,
    id: str,
    folder_path: str,
    file_path: str,
    filename: str,
    frontmatter: dict,
    sections: dict,
    content_hash: str,
) -> None:
    conn.execute(
        """
        INSERT INTO records (id, folder_path, file_path, filename, frontmatter, sections, content_hash, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            folder_path  = excluded.folder_path,
            file_path    = excluded.file_path,
            filename     = excluded.filename,
            frontmatter  = excluded.frontmatter,
            sections     = excluded.sections,
            content_hash = excluded.content_hash,
            updated_at   = excluded.updated_at
        """,
        (
            id,
            folder_path,
            file_path,
            filename,
            _dumps(frontmatter),
            _dumps(sections),
            content_hash,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def get_record_by_id(conn: sqlite3.Connection, record_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM records WHERE id = ?", (record_id,)
    ).fetchone()


def get_record_by_file_path(conn: sqlite3.Connection, file_path: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM records WHERE file_path = ?", (file_path,)
    ).fetchone()


def get_records_by_folder(conn: sqlite3.Connection, folder_path: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM records WHERE folder_path = ? ORDER BY filename",
        (folder_path,),
    ).fetchall()


def delete_record(conn: sqlite3.Connection, record_id: str) -> None:
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))


def delete_record_by_file_path(conn: sqlite3.Connection, file_path: str) -> None:
    conn.execute("DELETE FROM records WHERE file_path = ?", (file_path,))


def get_record_count(conn: sqlite3.Connection) -> int:
    (count,) = conn.execute("SELECT COUNT(*) FROM records").fetchone()
    return count


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

def replace_links(
    conn: sqlite3.Connection,
    source_id: str,
    links: list[dict],
) -> None:
    """Delete all links for source_id, then insert the new set."""
    conn.execute("DELETE FROM links WHERE source_id = ?", (source_id,))
    conn.executemany(
        "INSERT INTO links (source_id, target_file, field_name) VALUES (?, ?, ?)",
        [(source_id, lnk["target_file"], lnk["field_name"]) for lnk in links],
    )


def get_links_by_source(conn: sqlite3.Connection, source_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM links WHERE source_id = ?", (source_id,)
    ).fetchall()


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

def get_all_folders(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT folder_path, COUNT(*) AS record_count
        FROM records
        GROUP BY folder_path
        ORDER BY folder_path
        """
    ).fetchall()


# ---------------------------------------------------------------------------
# Schema (emergent — aggregated at query time)
# ---------------------------------------------------------------------------

def get_folder_frontmatter_keys(conn: sqlite3.Connection, folder_path: str) -> list[str]:
    """Return the union of all frontmatter keys across every record in a folder."""
    rows = conn.execute(
        "SELECT frontmatter FROM records WHERE folder_path = ?", (folder_path,)
    ).fetchall()
    keys: dict[str, None] = {}  # ordered set via insertion-order dict
    for row in rows:
        if row["frontmatter"]:
            for k in json.loads(row["frontmatter"]).keys():
                keys[k] = None
    return list(keys)


def get_folder_section_keys(conn: sqlite3.Connection, folder_path: str) -> list[str]:
    """Return the union of all section headings across every record in a folder."""
    rows = conn.execute(
        "SELECT sections FROM records WHERE folder_path = ?", (folder_path,)
    ).fetchall()
    keys: dict[str, None] = {}
    for row in rows:
        if row["sections"]:
            for k in json.loads(row["sections"]).keys():
                keys[k] = None
    return list(keys)


# ---------------------------------------------------------------------------
# Column widths
# ---------------------------------------------------------------------------

def upsert_col_width(
    conn: sqlite3.Connection, folder_path: str, field_name: str, width: int
) -> None:
    conn.execute(
        """
        INSERT INTO col_widths (folder_path, field_name, width)
        VALUES (?, ?, ?)
        ON CONFLICT(folder_path, field_name) DO UPDATE SET width = excluded.width
        """,
        (folder_path, field_name, width),
    )


def get_col_widths(conn: sqlite3.Connection, folder_path: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT field_name, width FROM col_widths WHERE folder_path = ?",
        (folder_path,),
    ).fetchall()


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def get_views(conn: sqlite3.Connection, folder_path: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM views WHERE folder_path = ? ORDER BY created_at",
        (folder_path,),
    ).fetchall()


def create_view(
    conn: sqlite3.Connection,
    *,
    id: str,
    folder_path: str,
    name: str,
    filters: list,
    sort: list,
    col_order: list,
    hidden_cols: list,
    created_at: str,
) -> None:
    conn.execute(
        """
        INSERT INTO views (id, folder_path, name, filters, sort, col_order, hidden_cols, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id, folder_path, name, _dumps(filters), _dumps(sort), _dumps(col_order), _dumps(hidden_cols), created_at),
    )


def delete_view(conn: sqlite3.Connection, view_id: str) -> None:
    conn.execute("DELETE FROM views WHERE id = ?", (view_id,))
