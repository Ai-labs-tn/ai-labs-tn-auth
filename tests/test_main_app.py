from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.main import create_app
from app.core.config import CORS_ORIGIN


def test_create_app_initialization():
    """Ensure the app object is created properly with middleware & routes."""
    app = create_app()

    # Validate app title
    assert app.title == "AI Labs TN Auth API"

    # Validate CORS middleware is present
    cors_middlewares = [mw for mw in app.user_middleware if mw.cls == CORSMiddleware]
    assert len(cors_middlewares) == 1, "CORS middleware was not added"

    # In your FastAPI/Starlette version, config lives in .kwargs, not .options
    cors_config = cors_middlewares[0].kwargs

    assert cors_config["allow_origins"] == [CORS_ORIGIN]
    assert cors_config["allow_credentials"] is True
    assert cors_config["allow_methods"] == ["*"]
    assert cors_config["allow_headers"] == ["*"]

    # Validate routers were included (health + auth)
    route_paths = [route.path for route in app.routes if isinstance(route, APIRoute)]

    assert "/api/health/" in route_paths
    assert any("/api/auth" in p for p in route_paths)


def test_health_endpoint_from_main_app():
    """Ensure the health endpoint is reachable using the full app instance."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/health/")
    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "ai-labs-tn-api"
