"""Per-vault field schema configuration.

Canonical, user-defined option lists for frontmatter fields (e.g. the fixed set
of `status` values for a folder). Stored as YAML in the vault itself — the vault
is the single source of truth — at ``<vault>/.obsidian-manager/schema.yaml``.

The file is *config*, not record data: it is not a ``.md`` file, so ``watcher.py``
ignores it and it never enters the SQLite index. The schema endpoint merges these
canonical options with the values actually seen across records, so an option stays
selectable even when no file currently uses it.

Shape::

    folders:
      Projects:
        status:
          options:
            - "01 - Idea"
            - "02 - Next"
            - "03 - Todo"

Writes are atomic (``.tmp`` + ``os.replace()``), mirroring ``sync/writer.py``.
"""

import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_CONFIG_DIR = ".obsidian-manager"
_CONFIG_FILE = "schema.yaml"


def config_path(vault_path: Path) -> Path:
    return Path(vault_path) / _CONFIG_DIR / _CONFIG_FILE


def load(vault_path: Path) -> dict:
    """Return the parsed config, or ``{}`` if missing or unreadable."""
    path = config_path(vault_path)
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception:
        logger.exception("failed to load schema config at %s", path)
        return {}
    return data if isinstance(data, dict) else {}


def _save(vault_path: Path, data: dict) -> None:
    path = config_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    os.replace(tmp, path)


def _norm(folder: str) -> str:
    return folder.rstrip("/")


def get_folder_field_options(vault_path: Path, folder: str) -> dict[str, list[str]]:
    """Return ``{field: [options...]}`` explicitly configured for the folder."""
    folders = load(vault_path).get("folders") or {}
    fields = folders.get(_norm(folder)) or {}
    result: dict[str, list[str]] = {}
    for field, cfg in fields.items():
        if isinstance(cfg, dict):
            opts = cfg.get("options")
            if isinstance(opts, list):
                result[field] = [str(o) for o in opts]
    return result


def get_field_options(vault_path: Path, folder: str, field: str) -> list[str] | None:
    """Return the canonical option list for a field, or ``None`` if unset."""
    return get_folder_field_options(vault_path, folder).get(field)


def set_field_options(vault_path: Path, folder: str, field: str, options: list[str]) -> None:
    data = load(vault_path)
    folders = data.setdefault("folders", {})
    if not isinstance(folders, dict):
        folders = data["folders"] = {}
    fields = folders.setdefault(_norm(folder), {})
    if not isinstance(fields, dict):
        fields = folders[_norm(folder)] = {}
    entry = fields.setdefault(field, {})
    if not isinstance(entry, dict):
        entry = fields[field] = {}
    entry["options"] = [str(o) for o in options]
    _save(vault_path, data)


def delete_field_options(vault_path: Path, folder: str, field: str) -> None:
    data = load(vault_path)
    folders = data.get("folders")
    if not isinstance(folders, dict):
        return
    fields = folders.get(_norm(folder))
    if not isinstance(fields, dict) or field not in fields:
        return
    del fields[field]
    if not fields:
        del folders[_norm(folder)]
    if not folders:
        del data["folders"]
    _save(vault_path, data)
