import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends

from app.api.auth_otp import router as auth_otp_router
from app.db import get_db_pool


# ---------------------------------------------------------------------------
# Fake DB connection + fake pool
# ---------------------------------------------------------------------------
class FakeDB(MagicMock):
    """Minimal fake DB connection used by SQL-accessing functions."""
    async def fetch(self, *args, **kwargs):
        return []
    async def execute(self, *args, **kwargs):
        return None


async def fake_get_db():
    """Overrides get_db dependency in tests."""
    return FakeDB()


# ---------------------------------------------------------------------------
# Test client fixture with DB dependency override
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    app = FastAPI()

    # Override DB dependency BEFORE including routers that use it
    app.dependency_overrides[get_db_pool] = fake_get_db

    # include your router
    app.include_router(auth_otp_router)

    return TestClient(app)


# ---------------------------------------------------------------------------
# /api/auth/otp/register/start
# ---------------------------------------------------------------------------
def test_start_register_otp_success(client):
    with patch(
        "app.api.auth_otp.start_register_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_start:
        mock_start.return_value = {"success": True, "message": "OTP sent to email"}

        response = client.post(
            "/api/auth/otp/register/start",
            params={"email": "test@example.com", "password": "Pass123"},
        )

        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "OTP sent to email"}
        mock_start.assert_awaited()


# ---------------------------------------------------------------------------
# /api/auth/otp/register/complete
# ---------------------------------------------------------------------------
def test_complete_register_otp_success(client):
    with patch(
        "app.api.auth_otp.complete_register_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_complete:
        mock_complete.return_value = {"id": "user123"}

        response = client.post(
            "/api/auth/otp/register/complete",
            params={
                "email": "test@example.com",
                "password": "Pass123",
                "otp": "123456",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"success": True, "user": {"id": "user123"}}
        mock_complete.assert_awaited()


def test_complete_register_otp_invalid(client):
    with patch(
        "app.api.auth_otp.complete_register_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_complete:
        mock_complete.side_effect = ValueError("Invalid or expired OTP")

        response = client.post(
            "/api/auth/otp/register/complete",
            params={
                "email": "test@example.com",
                "password": "Pass123",
                "otp": "000000",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["detail"] == "Invalid or expired OTP"


# ---------------------------------------------------------------------------
# /api/auth/otp/login/start
# ---------------------------------------------------------------------------
def test_start_login_otp_success(client):
    with patch(
        "app.api.auth_otp.start_login_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_start:
        mock_start.return_value = {"success": True, "message": "OTP sent to email"}

        response = client.post(
            "/api/auth/otp/login/start",
            params={"email": "test@example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "OTP sent to email"}
        mock_start.assert_awaited()


# ---------------------------------------------------------------------------
# /api/auth/otp/login/complete
# ---------------------------------------------------------------------------
def test_complete_login_otp_success_with_new_password(client):
    with patch(
        "app.api.auth_otp.complete_login_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_complete:
        mock_complete.return_value = {"access_token": "abc", "refresh_token": "xyz"}

        response = client.post(
            "/api/auth/otp/login/complete",
            params={
                "email": "test@example.com",
                "otp": "123456",
                "new_password": "NewPass123",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "abc",
            "refresh_token": "xyz",
        }
        mock_complete.assert_awaited()


def test_complete_login_otp_invalid(client):
    with patch(
        "app.api.auth_otp.complete_login_with_email_otp",
        new_callable=AsyncMock,
    ) as mock_complete:
        mock_complete.side_effect = ValueError("Invalid or expired OTP")

        response = client.post(
            "/api/auth/otp/login/complete",
            params={
                "email": "test@example.com",
                "otp": "000000",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid or expired OTP"
