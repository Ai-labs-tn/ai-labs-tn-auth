# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ORIGIN
from .api.health import router as health_router
from .api.auth import router as auth_router
from .db import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db(app)
    try:
        # Application is running
        yield
    finally:
        # Shutdown
        await close_db(app)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Labs TN Auth API",
        lifespan=lifespan,  # <- use lifespan instead of on_event
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[CORS_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)

    return app

app = create_app()
