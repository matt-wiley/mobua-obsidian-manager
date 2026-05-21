from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import DB_PATH, VAULT_PATH
from db.connection import close_db, get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DB_PATH)
    yield
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
