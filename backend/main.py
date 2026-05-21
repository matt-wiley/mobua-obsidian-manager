import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import events
from api.events import router as events_router
from api.folders import router as folders_router
from api.records import router as records_router
from api.sync import router as sync_router
from config import DB_PATH, VAULT_PATH
from db.connection import close_db, get_connection, init_db
from sync.indexer import reindex_all
from sync.watcher import start_watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("initializing DB at %s", DB_PATH)
    conn = init_db(DB_PATH)

    logger.info("reindexing vault at %s", VAULT_PATH)
    count = reindex_all(VAULT_PATH, conn)
    logger.info("reindex complete — %d files indexed", count)

    events.set_loop(asyncio.get_running_loop())
    observer = start_watcher(VAULT_PATH, conn, on_change=events.broadcast)
    yield
    observer.stop()
    observer.join()
    close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(events_router)
app.include_router(folders_router)
app.include_router(records_router)
app.include_router(sync_router)


@app.get("/health")
def health():
    conn = get_connection()
    (record_count,) = conn.execute("SELECT COUNT(*) FROM records").fetchone()
    return {
        "status": "ok",
        "vault_path": str(VAULT_PATH),
        "record_count": record_count,
    }
