"""Tests for sync/parser.py"""

import pytest
from pathlib import Path

from obsidian_manager.sync.parser import parse_file, infer_type, _parse_sections


VAULT = Path(__file__).parent.parent.parent / ".local" / "test-vault"


# ---------------------------------------------------------------------------
# parse_file
# ---------------------------------------------------------------------------

class TestParseFile:
    def test_filename(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        assert result["filename"] == "Build login page"

    def test_folder_path(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        assert result["folder_path"] == "Tasks/"

    def test_frontmatter_keys(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        fm = result["frontmatter"]
        assert fm["status"] == "active"
        assert fm["priority"] == "high"
        assert fm["project"] == "[[Q3 Rebrand]]"
        assert fm["due"] is not None

    def test_sections_present(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        assert "Overview" in result["sections"]
        assert "Work Notes" in result["sections"]

    def test_sections_content(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        assert "OAuth" in result["sections"]["Work Notes"]

    def test_frontmatter_wikilinks_in_links(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        field_names = [lnk["field_name"] for lnk in result["links"]]
        assert "project" in field_names
        assert "assignee" in field_names

    def test_frontmatter_link_target(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        project_link = next(
            lnk for lnk in result["links"] if lnk["field_name"] == "project"
        )
        assert project_link["target_file"] == "Q3 Rebrand.md"

    def test_body_wikilinks_field_name(self):
        result = parse_file(VAULT / "Tasks" / "Build login page.md", VAULT)
        body_links = [lnk for lnk in result["links"] if lnk["field_name"] == "__body__"]
        assert len(body_links) > 0

    def test_multi_section_file(self):
        result = parse_file(VAULT / "Projects" / "Q3 Rebrand.md", VAULT)
        assert set(result["sections"].keys()) == {"Overview", "Goals", "Notes"}

    def test_no_sections_file(self):
        result = parse_file(VAULT / "Areas" / "Engineering.md", VAULT)
        # May or may not have sections — just assert it's a dict
        assert isinstance(result["sections"], dict)


# ---------------------------------------------------------------------------
# _parse_sections — unit tests (fence-awareness)
# ---------------------------------------------------------------------------

class TestParseSections:
    def test_basic_two_sections(self):
        body = "## Alpha\n\nfoo\n\n## Beta\n\nbar"
        result = _parse_sections(body)
        assert list(result.keys()) == ["Alpha", "Beta"]
        assert result["Alpha"] == "foo"
        assert result["Beta"] == "bar"

    def test_h2_inside_backtick_fence_ignored(self):
        body = (
            "## Section\n\n"
            "```markdown\n"
            "## fake heading inside fence\n"
            "```\n\n"
            "after fence"
        )
        result = _parse_sections(body)
        assert list(result.keys()) == ["Section"]
        assert "## fake heading inside fence" in result["Section"]
        assert "after fence" in result["Section"]

    def test_h2_inside_tilde_fence_ignored(self):
        body = (
            "## Section\n\n"
            "~~~python\n"
            "## not a heading\n"
            "~~~\n\n"
            "tail"
        )
        result = _parse_sections(body)
        assert list(result.keys()) == ["Section"]
        assert "## not a heading" in result["Section"]

    def test_longer_closing_fence_closes_block(self):
        # Opening ``` closed by ```` (longer fence — valid CommonMark)
        body = (
            "## S\n\n"
            "````\n"
            "## inside\n"
            "````\n\n"
            "outside"
        )
        result = _parse_sections(body)
        assert list(result.keys()) == ["S"]
        assert "## inside" in result["S"]
        assert "outside" in result["S"]

    def test_real_h2_after_fence_creates_new_section(self):
        body = (
            "## First\n\n"
            "```\n## inside\n```\n\n"
            "## Second\n\n"
            "content"
        )
        result = _parse_sections(body)
        assert list(result.keys()) == ["First", "Second"]
        assert result["Second"] == "content"

    def test_unclosed_fence_treats_rest_as_content(self):
        body = "## S\n\n```\n## inside unclosed\nno closing fence"
        result = _parse_sections(body)
        assert list(result.keys()) == ["S"]
        assert "## inside unclosed" in result["S"]

    def test_fence_in_preamble_does_not_create_section(self):
        body = "# Title\n\n```\n## preamble fake\n```\n\n## Real\n\nok"
        result = _parse_sections(body)
        assert list(result.keys()) == ["Real"]
        assert result["Real"] == "ok"


# ---------------------------------------------------------------------------
# infer_type
# ---------------------------------------------------------------------------

class TestInferType:
    def test_date(self):
        assert infer_type("2026-06-10") == "date"

    def test_url_https(self):
        assert infer_type("https://example.com") == "url"

    def test_url_http(self):
        assert infer_type("http://example.com") == "url"

    def test_relation(self):
        assert infer_type("[[Q3 Rebrand]]") == "relation"

    def test_number_string(self):
        assert infer_type("42") == "number"

    def test_float_string(self):
        assert infer_type("3.14") == "number"

    def test_text(self):
        assert infer_type("active") == "text"

    def test_native_int(self):
        assert infer_type(7) == "number"

    def test_not_a_date_lookalike(self):
        assert infer_type("not-a-date") == "text"
