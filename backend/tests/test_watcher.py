"""Tests for sync/watcher.py"""

import json
import time
import pytest
from pathlib import Path

from db.connection import init_db
from sync.watcher import start_watcher


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "Tasks").mkdir()
    return tmp_path


@pytest.fixture
def conn(tmp_path):
    c = init_db(tmp_path / "test.db")
    yield c
    c.close()


@pytest.fixture
def watched(vault, conn):
    observer = start_watcher(vault, conn)
    yield vault, conn
    observer.stop()
    observer.join()


def _wait(condition, timeout=3.0, interval=0.05):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class TestWatcher:
    def test_new_file_indexed(self, watched):
        vault, conn = watched
        (vault / "Tasks" / "New task.md").write_text(
            "---\nstatus: todo\n---\n\n# [[New task]]\n"
        )
        assert _wait(
            lambda: conn.execute(
                "SELECT 1 FROM records WHERE filename = 'New task'"
            ).fetchone() is not None
        ), "record not indexed after file creation"

    def test_modified_file_reindexed(self, watched):
        vault, conn = watched
        path = vault / "Tasks" / "Editable.md"
        path.write_text("---\nstatus: todo\n---\n\n# [[Editable]]\n")
        assert _wait(
            lambda: conn.execute(
                "SELECT 1 FROM records WHERE filename = 'Editable'"
            ).fetchone() is not None
        )

        path.write_text("---\nstatus: done\n---\n\n# [[Editable]]\n")
        def _updated():
            row = conn.execute(
                "SELECT frontmatter FROM records WHERE filename = 'Editable'"
            ).fetchone()
            if row is None:
                return False
            return json.loads(row["frontmatter"]).get("status") == "done"

        assert _wait(_updated), "frontmatter not updated after file modification"

    def test_deleted_file_removed(self, watched):
        vault, conn = watched
        path = vault / "Tasks" / "Gone.md"
        path.write_text("---\nstatus: todo\n---\n\n# [[Gone]]\n")
        assert _wait(
            lambda: conn.execute(
                "SELECT 1 FROM records WHERE filename = 'Gone'"
            ).fetchone() is not None
        )

        path.unlink()
        assert _wait(
            lambda: conn.execute(
                "SELECT 1 FROM records WHERE filename = 'Gone'"
            ).fetchone() is None
        ), "record not removed after file deletion"

    def test_non_md_files_ignored(self, watched):
        vault, conn = watched
        (vault / "Tasks" / "ignore.txt").write_text("hello")
        time.sleep(0.2)
        count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        assert count == 0

    def test_obsidian_dir_ignored(self, watched):
        vault, conn = watched
        obsidian = vault / ".obsidian"
        obsidian.mkdir()
        (obsidian / "config.md").write_text("---\n---\n# hidden\n")
        time.sleep(0.2)
        count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        assert count == 0
