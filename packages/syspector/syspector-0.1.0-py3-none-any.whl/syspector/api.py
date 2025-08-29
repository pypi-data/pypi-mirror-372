"""Small FastAPI wrapper exposing system snapshots."""
from __future__ import annotations

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio

from .core import SystemInspector

def create_app(poll_interval: float = 1.0) -> FastAPI:
    app = FastAPI(title="syspector API")
    inspector = SystemInspector(poll_interval=poll_interval)
    _stream_task: asyncio.Task | None = None

    @app.get("/snapshot")
    async def snapshot():
        return JSONResponse(content=inspector.simple_report())

    @app.get("/stream")
    async def stream():
        # Very small illustrative streaming endpoint using server-sent events
        async def event_generator():
            async for snap in inspector.stream():
                yield ("data: " + str(snap) + "\n\n")
        return app.responses.StreamingResponse(event_generator(), media_type="text/event-stream")

    return app
