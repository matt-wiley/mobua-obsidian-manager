import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_conns: dict[str, sqlite3.Connection] = {}


def init_db(vault_id: str, db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    schema = (Path(__file__).parent / "schema.sql").read_text()
    conn.executescript(schema)
    conn.commit()

    _conns[vault_id] = conn
    logger.info("database ready at %s (vault_id=%s)", db_path, vault_id)
    return conn


def get_connection(vault_id: str) -> sqlite3.Connection:
    conn = _conns.get(vault_id)
    if conn is None:
        raise RuntimeError(f"Database not initialized for vault '{vault_id}'. Call init_db() first.")
    return conn


def close_db(vault_id: str) -> None:
    conn = _conns.pop(vault_id, None)
    if conn is not None:
        conn.close()
        logger.info("database connection closed (vault_id=%s)", vault_id)


def close_all() -> None:
    for vault_id in list(_conns.keys()):
        close_db(vault_id)
