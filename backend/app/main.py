from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.api.v1.router import api_router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.static_dir.mkdir(parents=True, exist_ok=True)
    (settings.static_dir / "uploads").mkdir(parents=True, exist_ok=True)

    # Initialize database tables (no-op until models are defined)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)

# CORS
allow_origins = (
    [origin.strip() for origin in settings.cors_origins.split(",")] if isinstance(settings.cors_origins, str) else settings.cors_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_v1_router, prefix="/api/v1")

# Static files
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
