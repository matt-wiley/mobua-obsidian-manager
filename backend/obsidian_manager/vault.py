import re
from pathlib import Path

from .config import DATA_DIR
from .db.connection import close_db, get_connection, init_db
from .sync.indexer import reindex_all
from .sync.watcher import start_watcher

_vaults: dict[str, dict] = {}


def unique_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))
    slug = re.sub(r"-+", "-", slug).strip("-") or "vault"
    if slug not in _vaults:
        return slug
    n = 2
    while f"{slug}-{n}" in _vaults:
        n += 1
    return f"{slug}-{n}"


def get_vault(vault_id: str) -> dict | None:
    entry = _vaults.get(vault_id)
    if entry is None:
        return None
    return {"id": entry["id"], "name": entry["name"], "path": entry["path"]}


def get_vault_path(vault_id: str) -> Path:
    return Path(_vaults[vault_id]["path"])


def list_vaults() -> list[dict]:
    return [{"id": v["id"], "name": v["name"], "path": v["path"]} for v in _vaults.values()]


def is_configured() -> bool:
    return len(_vaults) > 0


def activate(vault_id: str, name: str, vault_path: Path, on_change=None) -> None:
    db_path = DATA_DIR / f"{vault_id}.db"
    conn = init_db(vault_id, db_path)
    reindex_all(vault_path, conn)

    def _wrapped_on_change(event: dict) -> None:
        if on_change:
            on_change({**event, "vault_id": vault_id})

    observer = start_watcher(vault_path, conn, on_change=_wrapped_on_change)

    _vaults[vault_id] = {
        "id": vault_id,
        "name": name,
        "path": str(vault_path),
        "observer": observer,
    }


def deactivate(vault_id: str) -> None:
    entry = _vaults.pop(vault_id, None)
    if entry is None:
        return
    observer = entry.get("observer")
    if observer is not None:
        observer.stop()
        observer.join()
    close_db(vault_id)


def deactivate_all() -> None:
    for vault_id in list(_vaults.keys()):
        deactivate(vault_id)
