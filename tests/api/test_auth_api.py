import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.auth import router as auth_router


@pytest.fixture
def client():
    """Create a test client with only the auth router."""
    app = FastAPI()
    app.include_router(auth_router)
    return TestClient(app)


# ------------------------------------------------------------------------------
# /api/auth/register
# ------------------------------------------------------------------------------
def test_register_api_success(client):
    fake_response = {"id": "user123", "email": "test@example.com"}

    # Patch where supabase_service is imported: app.api.auth
    with patch("app.api.auth.supabase_service.register") as mock_register:
        mock_register.return_value = fake_response

        response = client.get(
            "/api/auth/register",
            params={
                "email": "test@example.com",
                "phone": None,   # FastAPI ends up passing "" to the function
                "password": "Pass123",
            },
        )

        assert response.status_code == 200
        assert response.json() == fake_response

        # FastAPI passed '' instead of None -> match actual call
        mock_register.assert_called_once_with("test@example.com", "", "Pass123")


def test_register_api_failure(client):
    # Here FastAPI re-raises the exception instead of returning 500 in your env
    with patch("app.api.auth.supabase_service.register") as mock_register:
        mock_register.side_effect = Exception("Registration failed")

        with pytest.raises(Exception) as exc:
            client.get(
                "/api/auth/register",
                params={
                    "email": "x@example.com",
                    "phone": None,
                    "password": "123456",
                },
            )

        assert "Registration failed" in str(exc.value)


# ------------------------------------------------------------------------------
# /api/auth/login
# ------------------------------------------------------------------------------
def test_login_api_success(client):
    fake_response = {"access_token": "abc123"}

    with patch("app.api.auth.supabase_service.login") as mock_login:
        mock_login.return_value = fake_response

        response = client.get(
            "/api/auth/login",
            params={"email": "test@example.com", "password": "Pass123"},
        )

        assert response.status_code == 200
        assert response.json() == fake_response
        mock_login.assert_called_once_with("test@example.com", "Pass123")


def test_login_api_failure(client):
    with patch("app.api.auth.supabase_service.login") as mock_login:
        mock_login.side_effect = Exception("Invalid credentials")

        with pytest.raises(Exception) as exc:
            client.get(
                "/api/auth/login",
                params={"email": "wrong@example.com", "password": "bad"},
            )

        assert "Invalid credentials" in str(exc.value)


# ------------------------------------------------------------------------------
# /api/auth/refresh
# ------------------------------------------------------------------------------
def test_refresh_api_success(client):
    fake_response = {"access_token": "newtoken"}

    with patch("app.api.auth.supabase_service.refresh") as mock_refresh:
        mock_refresh.return_value = fake_response

        response = client.get(
            "/api/auth/refresh",
            params={"refresh_token": "oldtoken123"},
        )

        assert response.status_code == 200
        assert response.json() == fake_response
        mock_refresh.assert_called_once_with("oldtoken123")


def test_refresh_api_failure(client):
    with patch("app.api.auth.supabase_service.refresh") as mock_refresh:
        mock_refresh.side_effect = Exception("Refresh failed")

        with pytest.raises(Exception) as exc:
            client.get(
                "/api/auth/refresh",
                params={"refresh_token": "badtoken"},
            )

        assert "Refresh failed" in str(exc.value)
