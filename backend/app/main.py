"""Mustafa Cricket Club — Management & Operations API."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.router import api_router
from app.db.session import engine
from app.db.base import Base

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="MCC Cricket Club API",
    description="Mustafa Cricket Club — Management & Operations Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    from app.db.seed import seed_if_empty

    seed_if_empty()


@app.get("/health")
def health():
    return {"status": "ok", "club": "Mustafa Cricket Club", "short": "MCC"}


@app.get("/")
def public_home():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"club": "Mustafa Cricket Club", "docs": "/docs"}
