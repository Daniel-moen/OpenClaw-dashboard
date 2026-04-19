"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import get_connection
from .routers import (
    assistant,
    auth,
    businesses,
    calendar,
    chat,
    dashboard,
    profiles,
    skills,
    vault,
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    get_connection()  # forces migrations + seed
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Openclaw Command Center API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = "/api"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(businesses.router, prefix=api_prefix)
    app.include_router(calendar.router, prefix=api_prefix)
    app.include_router(skills.router, prefix=api_prefix)
    app.include_router(vault.router, prefix=api_prefix)
    app.include_router(assistant.router, prefix=api_prefix)
    app.include_router(profiles.router, prefix=api_prefix)
    app.include_router(profiles.me_router, prefix=api_prefix)
    app.include_router(chat.router, prefix=api_prefix)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
