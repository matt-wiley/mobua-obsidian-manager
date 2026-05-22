"""Vault configuration endpoints.

GET    /config                  → {vault_configured: bool, vaults: [{id, name, path}]}
POST   /config/vault             → register new vault (name + path), returns vault entry
DELETE /config/vaults/{id}      → deregister + deactivate vault
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import vault as _vault
from api import events
from config import DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter()

_REGISTRY_PATH = DATA_DIR / "vaults.json"


def load_persisted_vaults() -> list[dict]:
    if not _REGISTRY_PATH.exists():
        return []
    try:
        return json.loads(_REGISTRY_PATH.read_text())
    except Exception:
        logger.exception("failed to load vaults.json")
        return []


def save_vault_registry(entries: list[dict]) -> None:
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY_PATH.write_text(json.dumps(entries, indent=2))


@router.get("/config")
def get_config():
    vaults = _vault.list_vaults()
    return {"vault_configured": _vault.is_configured(), "vaults": vaults}


class VaultCreate(BaseModel):
    name: str
    path: str


@router.post("/config/vault", status_code=201)
def add_vault(body: VaultCreate):
    vault_path = Path(body.path).expanduser()
    if not vault_path.exists() or not vault_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path '{body.path}' does not exist or is not a directory")

    vault_id = _vault.unique_id(body.name)
    _vault.activate(vault_id, body.name, vault_path, on_change=events.broadcast)

    entries = load_persisted_vaults()
    entries.append({"id": vault_id, "name": body.name, "path": str(vault_path)})
    save_vault_registry(entries)

    logger.info("registered vault '%s' at %s", vault_id, vault_path)
    return {"id": vault_id, "name": body.name, "path": str(vault_path)}


@router.delete("/config/vaults/{vault_id}", status_code=204)
def remove_vault(vault_id: str):
    if _vault.get_vault(vault_id) is None:
        raise HTTPException(status_code=404, detail=f"Vault '{vault_id}' not found")

    _vault.deactivate(vault_id)

    entries = [e for e in load_persisted_vaults() if e["id"] != vault_id]
    save_vault_registry(entries)

    logger.info("removed vault '%s'", vault_id)
