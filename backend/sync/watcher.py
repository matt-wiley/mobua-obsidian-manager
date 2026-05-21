"""Watch the vault for file changes and keep SQLite in sync.

Usage:
    observer = start_watcher(vault_path, conn)
    # later:
    observer.stop()
    observer.join()

The observer is wrapped in a restart loop so a crash doesn't kill sync.
"""

import logging
import sqlite3
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from db import queries
from sync.indexer import index_file

logger = logging.getLogger(__name__)


class _VaultHandler(FileSystemEventHandler):
    def __init__(self, vault_path: Path, conn: sqlite3.Connection) -> None:
        super().__init__()
        self.vault_path = vault_path
        self.conn = conn

    # ------------------------------------------------------------------
    # watchdog callbacks
    # ------------------------------------------------------------------

    def on_created(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        self._index(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        self._index(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        queries.delete_record_by_file_path(self.conn, event.src_path)
        self.conn.commit()
        logger.info("deleted record for %s", event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        # watchdog fires on_moved for renames
        src = Path(event.src_path)
        dest = Path(event.dest_path)

        if _is_obsidian(src) or _is_obsidian(dest):
            return

        if src.suffix == ".md":
            queries.delete_record_by_file_path(self.conn, str(src))
            self.conn.commit()

        if dest.suffix == ".md":
            self._index(dest)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _relevant(self, event: FileSystemEvent) -> bool:
        if event.is_directory:
            return False
        path = Path(event.src_path)
        return path.suffix == ".md" and not _is_obsidian(path)

    def _index(self, path: Path) -> None:
        try:
            index_file(path, self.vault_path, self.conn)
        except Exception:
            logger.exception("failed to index %s", path)


def _is_obsidian(path: Path) -> bool:
    return ".obsidian" in path.parts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_watcher(vault_path: Path, conn: sqlite3.Connection) -> Observer:
    """Start a watchdog observer with auto-restart on crash. Returns the Observer."""
    handler = _VaultHandler(vault_path, conn)
    observer = Observer()
    observer.schedule(handler, str(vault_path), recursive=True)
    observer.start()
    logger.info("watcher started on %s", vault_path)

    _start_guardian(observer, vault_path, conn)
    return observer


def _start_guardian(observer: Observer, vault_path: Path, conn: sqlite3.Connection) -> None:
    """Background thread that restarts the observer if it dies."""
    def _guard():
        nonlocal observer
        while True:
            time.sleep(5)
            if not observer.is_alive():
                logger.warning("watcher died — restarting")
                try:
                    observer.stop()
                except Exception:
                    pass
                new_obs = Observer()
                handler = _VaultHandler(vault_path, conn)
                new_obs.schedule(handler, str(vault_path), recursive=True)
                new_obs.start()
                logger.info("watcher restarted")
                # Replace the observer reference inside the thread so
                # subsequent checks watch the new one.
                observer = new_obs

    t = threading.Thread(target=_guard, daemon=True)
    t.start()
