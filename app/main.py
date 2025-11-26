from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import CORS_ORIGIN
from .api.health import router as health_router
from .api.auth import router as auth_router

def create_app() -> FastAPI:
    app = FastAPI(title="AI Labs TN Auth API")
    app.add_middleware(CORSMiddleware, allow_origins=[CORS_ORIGIN], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.include_router(health_router)
    app.include_router(auth_router)
    return app

app = create_app()
