"""Sync / repair endpoints.

POST /sync/repair   → re-index every .md file in the vault
"""

import logging

from fastapi import APIRouter, Depends

import vault
from api._helpers import require_vault
from db.connection import get_connection
from sync.indexer import reindex_all

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sync/repair", dependencies=[Depends(require_vault)])
def repair(vault_id: str):
    conn = get_connection(vault_id)
    vault_path = vault.get_vault_path(vault_id)
    logger.info("repair requested — reindexing vault '%s'", vault_id)
    count = reindex_all(vault_path, conn)
    logger.info("repair complete — %d files reindexed", count)
    return {"reindexed": count}
