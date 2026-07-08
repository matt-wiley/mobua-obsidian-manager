import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import events
from .api.config import load_persisted_vaults, router as config_router, save_vault_registry
from .api.events import router as events_router
from .api.folders import router as folders_router
from .api.meta import router as meta_router
from .api.records import router as records_router
from .api.sync import router as sync_router
from . import vault
from .config import VAULT_PATH
from .db.connection import close_all

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"


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
app.include_router(config_router, prefix="/api")
app.include_router(meta_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(folders_router, prefix="/api/vaults/{vault_id}")
app.include_router(records_router, prefix="/api/vaults/{vault_id}")
app.include_router(sync_router, prefix="/api/vaults/{vault_id}")


@app.get("/api/health")
def health():
    vaults = vault.list_vaults()
    return {
        "status": "ok",
        "vaults": vaults,
    }


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    candidate = _STATIC_DIR / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    fallback = _STATIC_DIR / "200.html"
    if fallback.exists():
        return FileResponse(fallback)
    return {"error": "UI not built. Run `make build` first."}
