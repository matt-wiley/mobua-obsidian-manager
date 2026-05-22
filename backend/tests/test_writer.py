"""Tests for sync/writer.py"""

import pytest
import yaml
from pathlib import Path

from obsidian_manager.sync.writer import write_record


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
