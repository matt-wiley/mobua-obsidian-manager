import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

    observer = start_watcher(VAULT_PATH, conn)
    yield
    observer.stop()
    observer.join()
    close_db()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    conn = get_connection()
    (record_count,) = conn.execute("SELECT COUNT(*) FROM records").fetchone()
    return {
        "status": "ok",
        "vault_path": str(VAULT_PATH),
        "record_count": record_count,
    }
