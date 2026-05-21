import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_conn: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _conn


def init_db(db_path: Path) -> sqlite3.Connection:
    global _conn
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(db_path), check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA foreign_keys=ON")

    schema = (Path(__file__).parent / "schema.sql").read_text()
    _conn.executescript(schema)
    _conn.commit()

    logger.info("database ready at %s", db_path)
    return _conn


def close_db() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
        logger.info("database connection closed")
