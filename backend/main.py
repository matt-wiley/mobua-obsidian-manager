import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from api import events
from api.config import load_persisted_vaults, router as config_router, save_vault_registry
from api.events import router as events_router
from api.folders import router as folders_router
from api.records import router as records_router
from api.sync import router as sync_router
import vault
from config import VAULT_PATH
from db.connection import close_all

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    events.set_loop(asyncio.get_running_loop())

    persisted = load_persisted_vaults()

    if not persisted and VAULT_PATH is not None:
        logger.info("migrating single-vault config to multi-vault registry")
        entry = {"id": "default", "name": "My Vault", "path": str(VAULT_PATH)}
        save_vault_registry([entry])
        persisted = [entry]

    for entry in persisted:
        logger.info("activating vault '%s' at %s", entry["id"], entry["path"])
        try:
            vault.activate(entry["id"], entry["name"], Path(entry["path"]), on_change=events.broadcast)
        except Exception:
            logger.exception("failed to activate vault '%s'", entry["id"])

    yield

    vault.deactivate_all()
    close_all()


app = FastAPI(lifespan=lifespan)
app.include_router(config_router)
app.include_router(events_router)
app.include_router(folders_router, prefix="/vaults/{vault_id}")
app.include_router(records_router, prefix="/vaults/{vault_id}")
app.include_router(sync_router, prefix="/vaults/{vault_id}")


@app.get("/health")
def health():
    vaults = vault.list_vaults()
    return {
        "status": "ok",
        "vaults": vaults,
    }
