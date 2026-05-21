"""Tests for sync/indexer.py"""

import json
import pytest
from pathlib import Path

from db.connection import init_db
from sync.indexer import index_file, reindex_all


VAULT = Path(__file__).parent.parent.parent / ".local" / "test-vault"


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    c = init_db(db_path)
    yield c
    c.close()


class TestIndexFile:
    def test_record_inserted(self, conn):
        index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        row = conn.execute("SELECT * FROM records WHERE filename = 'Build login page'").fetchone()
        assert row is not None

    def test_folder_path(self, conn):
        index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        row = conn.execute("SELECT folder_path FROM records WHERE filename = 'Build login page'").fetchone()
        assert row["folder_path"] == "Tasks/"

    def test_frontmatter_stored_as_json(self, conn):
        index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        row = conn.execute("SELECT frontmatter FROM records WHERE filename = 'Build login page'").fetchone()
        fm = json.loads(row["frontmatter"])
        assert fm["status"] == "active"

    def test_sections_stored_as_json(self, conn):
        index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        row = conn.execute("SELECT sections FROM records WHERE filename = 'Build login page'").fetchone()
        sections = json.loads(row["sections"])
        assert "Overview" in sections

    def test_links_inserted(self, conn):
        index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        row = conn.execute("SELECT id FROM records WHERE filename = 'Build login page'").fetchone()
        links = conn.execute("SELECT * FROM links WHERE source_id = ?", (row["id"],)).fetchall()
        field_names = [lnk["field_name"] for lnk in links]
        assert "project" in field_names

    def test_content_hash_skips_reindex(self, conn):
        file_path = VAULT / "Tasks" / "Build login page.md"
        id1 = index_file(file_path, VAULT, conn)
        # Update updated_at to check it doesn't change on second call
        conn.execute("UPDATE records SET updated_at = '1970-01-01' WHERE id = ?", (id1,))
        conn.commit()
        id2 = index_file(file_path, VAULT, conn)
        assert id1 == id2
        row = conn.execute("SELECT updated_at FROM records WHERE id = ?", (id1,)).fetchone()
        assert row["updated_at"] == "1970-01-01"

    def test_stable_uuid(self, conn):
        id1 = index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        id2 = index_file(VAULT / "Tasks" / "Build login page.md", VAULT, conn)
        assert id1 == id2

    def test_links_replaced_on_reindex(self, conn, tmp_path):
        """Mutate a file and reindex — old links removed, new ones inserted."""
        md = tmp_path / "note.md"
        md.write_text("---\nproject: \"[[Alpha]]\"\n---\n# [[note]]\n")
        vault = tmp_path
        index_file(md, vault, conn)
        row = conn.execute("SELECT id FROM records WHERE filename = 'note'").fetchone()
        assert row is not None
        links_before = conn.execute("SELECT target_file FROM links WHERE source_id = ?", (row["id"],)).fetchall()
        assert any("Alpha" in lnk["target_file"] for lnk in links_before)

        # Overwrite the file with a different wikilink
        md.write_text("---\nproject: \"[[Beta]]\"\n---\n# [[note]]\n")
        index_file(md, vault, conn)
        links_after = conn.execute("SELECT target_file FROM links WHERE source_id = ?", (row["id"],)).fetchall()
        targets = [lnk["target_file"] for lnk in links_after]
        assert not any("Alpha" in t for t in targets)
        assert any("Beta" in t for t in targets)


class TestReindexAll:
    def test_all_files_indexed(self, conn):
        count = reindex_all(VAULT, conn)
        total = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        assert total == count
        assert count > 0

    def test_skips_obsidian_dir(self, conn, tmp_path):
        obsidian_dir = tmp_path / ".obsidian"
        obsidian_dir.mkdir()
        (obsidian_dir / "config.md").write_text("---\n---\n# hidden\n")
        (tmp_path / "Tasks").mkdir()
        (tmp_path / "Tasks" / "Real note.md").write_text("---\nstatus: done\n---\n# [[Real note]]\n")
        reindex_all(tmp_path, conn)
        rows = conn.execute("SELECT filename FROM records").fetchall()
        filenames = [r["filename"] for r in rows]
        assert "config" not in filenames
        assert "Real note" in filenames
