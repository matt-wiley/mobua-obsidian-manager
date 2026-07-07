"""Tests for sync/writer.py"""

import pytest
import yaml
from pathlib import Path

from obsidian_manager.sync.writer import (
    delete_section,
    join_document,
    retitle_h1,
    split_document,
    upsert_section,
    write_record,
)


DOC = (
    "---\n"
    "status: active\n"
    "---\n"
    "\n"
    "# [[Note]]\n"
    "\n"
    "Preamble prose the index does not model.\n"
    "\n"
    "## Overview\n"
    "\n"
    "Original overview.\n"
    "\n"
    "## Work Notes\n"
    "\n"
    "Original notes.\n"
)


class TestWriteRecord:
    def test_creates_file(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(
            file_path=out,
            filename="My Note",
            frontmatter={"status": "active"},
            sections={"Overview": "Some content"},
        )
        assert out.exists()

    def test_frontmatter_block(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(
            file_path=out,
            filename="My Note",
            frontmatter={"status": "active", "priority": "high"},
            sections={},
        )
        text = out.read_text()
        assert text.startswith("---\n")
        assert "status: active" in text
        assert "priority: high" in text

    def test_h1_wikilink(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(
            file_path=out,
            filename="Build login page",
            frontmatter={},
            sections={},
        )
        assert "# [[Build login page]]" in out.read_text()

    def test_section_rendered(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(
            file_path=out,
            filename="note",
            frontmatter={},
            sections={"Overview": "Hello world"},
        )
        text = out.read_text()
        assert "## Overview" in text
        assert "Hello world" in text

    def test_multiple_sections_in_order(self, tmp_path):
        out = tmp_path / "note.md"
        sections = {"Alpha": "first", "Beta": "second", "Gamma": "third"}
        write_record(file_path=out, filename="note", frontmatter={}, sections=sections)
        text = out.read_text()
        assert text.index("## Alpha") < text.index("## Beta") < text.index("## Gamma")

    def test_atomic_write_no_tmp_left(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(file_path=out, filename="note", frontmatter={}, sections={})
        tmp = out.with_suffix(".md.tmp")
        assert not tmp.exists()

    def test_accepts_json_string_frontmatter(self, tmp_path):
        import json
        out = tmp_path / "note.md"
        write_record(
            file_path=out,
            filename="note",
            frontmatter=json.dumps({"status": "done"}),
            sections="{}",
        )
        assert "status: done" in out.read_text()

    def test_roundtrip_frontmatter(self, tmp_path):
        """Values written to disk can be read back cleanly by yaml."""
        out = tmp_path / "note.md"
        fm = {"status": "active", "priority": "high", "due": "2026-06-10"}
        write_record(file_path=out, filename="note", frontmatter=fm, sections={})
        text = out.read_text()
        # Strip --- delimiters and parse the YAML block
        inner = text.split("---")[1]
        parsed = yaml.safe_load(inner)
        assert parsed["status"] == "active"
        assert parsed["due"] == "2026-06-10"

    def test_empty_frontmatter_omits_block(self, tmp_path):
        out = tmp_path / "note.md"
        write_record(file_path=out, filename="note", frontmatter={}, sections={})
        assert not out.read_text().startswith("---")


# ---------------------------------------------------------------------------
# Document split/join — the round-trip must be lossless
# ---------------------------------------------------------------------------

class TestSplitJoin:
    def test_roundtrip_is_byte_identical(self):
        frontmatter, body = split_document(DOC)
        assert join_document(frontmatter, body) == DOC

    def test_frontmatter_parsed(self):
        frontmatter, _ = split_document(DOC)
        assert frontmatter == {"status": "active"}

    def test_body_keeps_preamble_and_h1(self):
        _, body = split_document(DOC)
        assert body.startswith("\n# [[Note]]\n")
        assert "Preamble prose the index does not model." in body

    def test_no_frontmatter_returns_verbatim_body(self):
        text = "# [[Note]]\n\nJust a body.\n"
        frontmatter, body = split_document(text)
        assert frontmatter == {}
        assert body == text
        assert join_document(frontmatter, body) == text

    def test_frontmatter_replacement_leaves_body_untouched(self):
        _, body = split_document(DOC)
        result = join_document({"status": "done"}, body)
        assert "status: done" in result
        assert "Preamble prose the index does not model." in result
        assert "## Overview" in result and "## Work Notes" in result


# ---------------------------------------------------------------------------
# Surgical section edits
# ---------------------------------------------------------------------------

class TestUpsertSection:
    def test_edits_only_target_section(self):
        _, body = split_document(DOC)
        new = upsert_section(body, "Overview", "Rewritten overview.")
        assert "Rewritten overview." in new
        assert "Original overview." not in new
        # Everything else survives.
        assert "Preamble prose the index does not model." in new
        assert "# [[Note]]" in new
        assert "Original notes." in new

    def test_preserves_other_section_position(self):
        _, body = split_document(DOC)
        new = upsert_section(body, "Overview", "X")
        assert new.index("## Overview") < new.index("## Work Notes")

    def test_missing_heading_is_appended(self):
        _, body = split_document(DOC)
        new = upsert_section(body, "New Section", "Fresh content.")
        assert new.index("## Work Notes") < new.index("## New Section")
        assert "Fresh content." in new
        assert "Original notes." in new

    def test_rename_preserves_content_and_place(self):
        _, body = split_document(DOC)
        new = upsert_section(body, "Summary", "Original overview.", previous_heading="Overview")
        assert "## Summary" in new
        assert "## Overview" not in new
        assert "Original overview." in new
        assert new.index("## Summary") < new.index("## Work Notes")

    def test_empty_content_keeps_heading(self):
        _, body = split_document(DOC)
        new = upsert_section(body, "Overview", "")
        assert "## Overview" in new
        assert "Original notes." in new


class TestDeleteSection:
    def test_removes_target_only(self):
        _, body = split_document(DOC)
        new = delete_section(body, "Overview")
        assert "## Overview" not in new
        assert "Original overview." not in new
        assert "## Work Notes" in new
        assert "Preamble prose the index does not model." in new

    def test_absent_heading_is_noop(self):
        _, body = split_document(DOC)
        assert delete_section(body, "Nope") == body


class TestRetitleH1:
    def test_updates_self_link(self):
        _, body = split_document(DOC)
        new = retitle_h1(body, "Note", "Renamed Note")
        assert "# [[Renamed Note]]" in new
        assert "# [[Note]]" not in new

    def test_no_match_leaves_body_unchanged(self):
        body = "# Plain heading\n\nBody.\n"
        assert retitle_h1(body, "Note", "Renamed") == body
