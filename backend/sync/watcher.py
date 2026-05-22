"""Watch the vault for file changes and keep SQLite in sync.

Usage:
    observer = start_watcher(vault_path, conn, on_change=broadcast)
    # later:
    observer.stop()
    observer.join()

The observer is wrapped in a restart loop so a crash doesn't kill sync.
`on_change` is an optional callable that receives an event dict after each
index or delete — used to push SSE events to connected clients.
"""

import logging
import sqlite3
import threading
import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from db import queries
from sync.indexer import index_file

logger = logging.getLogger(__name__)


_DELETE_DEBOUNCE_S = 0.5  # seconds to wait before committing a delete


class _VaultHandler(FileSystemEventHandler):
    def __init__(
        self,
        vault_path: Path,
        conn: sqlite3.Connection,
        on_change: Callable[[dict], None] | None = None,
    ) -> None:
        super().__init__()
        self.vault_path = vault_path
        self.conn = conn
        self.on_change = on_change
        self._pending_deletes: dict[str, threading.Timer] = {}

    # ------------------------------------------------------------------
    # watchdog callbacks
    # ------------------------------------------------------------------

    def on_created(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        # Cancel any pending delete for this path — handles the atomic
        # write pattern (tmp → os.replace → .md) which fires deleted+created.
        self._cancel_pending_delete(event.src_path)
        self._index(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        self._cancel_pending_delete(event.src_path)
        self._index(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not self._relevant(event):
            return
        path = event.src_path
        timer = threading.Timer(_DELETE_DEBOUNCE_S, self._do_delete, args=[path])
        self._pending_deletes[path] = timer
        timer.start()

    def _cancel_pending_delete(self, path: str) -> None:
        timer = self._pending_deletes.pop(path, None)
        if timer:
            timer.cancel()

    def _do_delete(self, path: str) -> None:
        self._pending_deletes.pop(path, None)
        # If the file exists again the "delete" was part of an atomic write
        # (e.g. tmp → os.replace → .md).  Re-index instead of deleting.
        if Path(path).exists():
            self._index(Path(path))
            return
        row = queries.get_record_by_file_path(self.conn, path)
        queries.delete_record_by_file_path(self.conn, path)
        self.conn.commit()
        logger.info("deleted record for %s", path)
        if row and self.on_change:
            self.on_change({
                "type": "record_deleted",
                "folder_path": row["folder_path"],
                "record_id": row["id"],
            })

    def on_moved(self, event: FileSystemEvent) -> None:
        src = Path(event.src_path)
        dest = Path(event.dest_path)

        if _is_obsidian(src) or _is_obsidian(dest):
            return

        if src.suffix == ".md":
            self._cancel_pending_delete(str(src))
            queries.delete_record_by_file_path(self.conn, str(src))
            self.conn.commit()

        if dest.suffix == ".md":
            self._cancel_pending_delete(str(dest))
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
            record_id = index_file(path, self.vault_path, self.conn)
            if self.on_change:
                folder_path = _folder_path(path, self.vault_path)
                self.on_change({
                    "type": "record_changed",
                    "folder_path": folder_path,
                    "record_id": record_id,
                })
        except Exception:
            logger.exception("failed to index %s", path)


def _is_obsidian(path: Path) -> bool:
    return ".obsidian" in path.parts


def _folder_path(file_path: Path, vault_path: Path) -> str:
    rel = file_path.relative_to(vault_path)
    if len(rel.parts) < 2:
        return ""
    return "/".join(rel.parts[:-1]) + "/"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_watcher(
    vault_path: Path,
    conn: sqlite3.Connection,
    on_change: Callable[[dict], None] | None = None,
) -> Observer:
    """Start a watchdog observer with auto-restart on crash. Returns the Observer."""
    handler = _VaultHandler(vault_path, conn, on_change)
    observer = Observer()
    observer.schedule(handler, str(vault_path), recursive=True)
    observer.start()
    logger.info("watcher started on %s", vault_path)

    _start_guardian(observer, vault_path, conn, on_change)
    return observer


def _start_guardian(
    observer: Observer,
    vault_path: Path,
    conn: sqlite3.Connection,
    on_change: Callable[[dict], None] | None,
) -> None:
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
                handler = _VaultHandler(vault_path, conn, on_change)
                new_obs.schedule(handler, str(vault_path), recursive=True)
                new_obs.start()
                logger.info("watcher restarted")
                observer = new_obs

    t = threading.Thread(target=_guard, daemon=True)
    t.start()
