# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ORIGIN
from .api.health import router as health_router
from .api.auth import router as auth_router   # new OTP routes
from .db import init_db, close_db

def create_app() -> FastAPI:
    app = FastAPI(title="AI Labs TN Auth API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[CORS_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)

    @app.on_event("startup")
    async def on_startup():
        await init_db(app)

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_db(app)

    return app

app = create_app()
