"""Tests for per-vault field schema configuration."""

from obsidian_manager import schema_config


def test_missing_file_returns_empty(tmp_path):
    assert schema_config.load(tmp_path) == {}
    assert schema_config.get_field_options(tmp_path, "Projects", "status") is None
    assert schema_config.get_folder_field_options(tmp_path, "Projects") == {}


def test_set_and_get_round_trip(tmp_path):
    opts = ["01 - Idea", "02 - Next", "03 - Todo"]
    schema_config.set_field_options(tmp_path, "Projects", "status", opts)

    assert schema_config.config_path(tmp_path).exists()
    assert schema_config.get_field_options(tmp_path, "Projects", "status") == opts
    assert schema_config.get_folder_field_options(tmp_path, "Projects") == {"status": opts}


def test_folder_key_is_trailing_slash_insensitive(tmp_path):
    schema_config.set_field_options(tmp_path, "Projects/", "status", ["A", "B"])
    # Stored and read back under the normalized (no trailing slash) key.
    assert schema_config.get_field_options(tmp_path, "Projects", "status") == ["A", "B"]


def test_set_preserves_order_and_stringifies(tmp_path):
    schema_config.set_field_options(tmp_path, "Tasks", "priority", [3, 1, 2])
    assert schema_config.get_field_options(tmp_path, "Tasks", "priority") == ["3", "1", "2"]


def test_multiple_fields_and_folders_coexist(tmp_path):
    schema_config.set_field_options(tmp_path, "Projects", "status", ["A"])
    schema_config.set_field_options(tmp_path, "Projects", "phase", ["X", "Y"])
    schema_config.set_field_options(tmp_path, "Tasks", "status", ["Z"])

    assert schema_config.get_folder_field_options(tmp_path, "Projects") == {
        "status": ["A"],
        "phase": ["X", "Y"],
    }
    assert schema_config.get_field_options(tmp_path, "Tasks", "status") == ["Z"]


def test_delete_removes_field_and_prunes_empty(tmp_path):
    schema_config.set_field_options(tmp_path, "Projects", "status", ["A"])
    schema_config.delete_field_options(tmp_path, "Projects", "status")

    assert schema_config.get_field_options(tmp_path, "Projects", "status") is None
    # Folder (and empty top-level) pruned once the last field is gone.
    assert schema_config.load(tmp_path) == {}


def test_delete_leaves_other_fields(tmp_path):
    schema_config.set_field_options(tmp_path, "Projects", "status", ["A"])
    schema_config.set_field_options(tmp_path, "Projects", "phase", ["X"])
    schema_config.delete_field_options(tmp_path, "Projects", "status")

    assert schema_config.get_folder_field_options(tmp_path, "Projects") == {"phase": ["X"]}


def test_delete_missing_is_noop(tmp_path):
    # Should not raise when nothing is configured.
    schema_config.delete_field_options(tmp_path, "Projects", "status")
    assert schema_config.load(tmp_path) == {}


def test_broken_file_returns_empty(tmp_path):
    path = schema_config.config_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("::: not valid yaml :::\n  - [")
    assert schema_config.load(tmp_path) == {}


def test_no_tmp_file_left_behind(tmp_path):
    schema_config.set_field_options(tmp_path, "Projects", "status", ["A"])
    leftovers = list(schema_config.config_path(tmp_path).parent.glob("*.tmp"))
    assert leftovers == []
