"""Sync / repair endpoints.

POST /sync/repair   → re-index every .md file in the vault
"""

import logging

from fastapi import APIRouter

from config import VAULT_PATH
from db.connection import get_connection
from sync.indexer import reindex_all

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sync/repair")
def repair():
    conn = get_connection()
    logger.info("repair requested — reindexing vault")
    count = reindex_all(VAULT_PATH, conn)
    logger.info("repair complete — %d files reindexed", count)
    return {"reindexed": count}
