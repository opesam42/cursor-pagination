from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.database import close_db_pool, init_db_pool
from backend.orm import init_models
from backend.routers import cursor, deferred, offset


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    # Create SQLModel tables if they don't exist. Core SQL and indexes left as TODO for author.
    try:
        await init_models()
    except Exception:
        # Best-effort model initialization for demo startup; don't crash app on model init failure.
        pass
    try:
        yield
    finally:
        await close_db_pool()


app = FastAPI(
    title="Cursor Pagination Demo",
    description="Visual demo for offset, cursor, and keyset pagination strategies",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(offset.router, prefix="/api/offset")
app.include_router(cursor.router, prefix="/api/cursor")
app.include_router(deferred.router, prefix="/api/deferred")


@app.get("/")
async def serve_frontend():
    return FileResponse(Path(__file__).resolve().parent.parent / "frontend" / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
