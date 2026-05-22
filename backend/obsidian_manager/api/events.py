"""SSE endpoint and broadcast helper.

Clients connect to GET /events and receive a stream of JSON events.
The watcher (a background thread) calls broadcast() to push events to
all connected clients. A ping is sent every 15 s so clients can detect
a dropped connection.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter()

_subscribers: set[asyncio.Queue] = set()
_loop: asyncio.AbstractEventLoop | None = None


def set_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Store the running event loop so broadcast() can use it from threads."""
    global _loop
    _loop = loop


def broadcast(event: dict) -> None:
    """Push an event to every connected SSE client. Thread-safe."""
    if _loop is None or not _subscribers:
        return
    data = json.dumps(event)
    for q in list(_subscribers):
        _loop.call_soon_threadsafe(q.put_nowait, data)


async def _stream() -> AsyncGenerator[str, None]:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.add(q)
    logger.info("SSE client connected (%d total)", len(_subscribers))
    try:
        while True:
            try:
                data = await asyncio.wait_for(q.get(), timeout=15.0)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                yield "event: ping\ndata: {}\n\n"
    finally:
        _subscribers.discard(q)
        logger.info("SSE client disconnected (%d remaining)", len(_subscribers))


@router.get("/events")
async def events():
    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
