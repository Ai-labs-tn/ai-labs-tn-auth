import pytest
from unittest.mock import AsyncMock, patch

import asyncpg

from app.services import email_otp_service


@pytest.fixture
def mock_pool():
    """
    Create a fake asyncpg pool with a fake connection.
    We only care that .acquire() returns an object with
    .execute() and .fetchrow().
    """
    class FakeConn:
        def __init__(self):
            self.executed = []
            self.rows = None

        async def execute(self, *args, **kwargs):
            self.executed.append((args, kwargs))

        async def fetchrow(self, *args, **kwargs):
            # just return last set row
            return self.rows

        async def transaction(self):
            class DummyTx:
                async def __aenter__(self_inner):
                    return None

                async def __aexit__(self_inner, exc_type, exc_val, exc_tb):
                    return False

            return DummyTx()

    class FakePool:
        def __init__(self):
            self.conn = FakeConn()

        async def acquire(self):
            class DummyAcquire:
                async def __aenter__(self_inner):
                    return pool.conn

                async def __aexit__(self_inner, exc_type, exc_val, exc_tb):
                    return False

            pool = self
            return DummyAcquire()

    return FakePool()


@pytest.mark.asyncio
async def test_start_register_with_email_otp_success(mock_pool):
    # Patch create_email_otp and send_otp_email
    with patch(
        "app.services.email_otp_service.create_email_otp",
        new_callable=AsyncMock,
    ) as mock_create_otp, patch(
        "app.services.email_otp_service.send_otp_email"
    ) as mock_send_email:
        mock_create_otp.return_value = "123456"

        result = await email_otp_service.start_register_with_email_otp(
            pool=mock_pool,
            email="test@example.com",
            password="Pass123",
        )

        assert result["success"] is True
        mock_create_otp.assert_awaited_once_with(
            mock_pool, email="test@example.com", purpose="register", ttl_minutes=10
        )
        mock_send_email.assert_called_once_with("test@example.com", "123456")


@pytest.mark.asyncio
async def test_complete_register_with_email_otp_success(mock_pool):
    with patch(
        "app.services.email_otp_service.verify_email_otp",
        new_callable=AsyncMock,
    ) as mock_verify, patch(
        "app.services.email_otp_service.supabase_service.register"
    ) as mock_supabase_register:
        mock_verify.return_value = True
        mock_supabase_register.return_value = {"id": "user123"}

        result = await email_otp_service.complete_register_with_email_otp(
            pool=mock_pool,
            email="test@example.com",
            password="Pass123",
            otp="123456",
            phone=None,
        )

        assert result == {"id": "user123"}
        mock_verify.assert_awaited_once_with(
            mock_pool, email="test@example.com", otp="123456", purpose="register"
        )
        mock_supabase_register.assert_called_once_with(
            "test@example.com", None, "Pass123"
        )


@pytest.mark.asyncio
async def test_complete_register_with_email_otp_invalid_otp(mock_pool):
    with patch(
        "app.services.email_otp_service.verify_email_otp",
        new_callable=AsyncMock,
    ) as mock_verify:
        mock_verify.return_value = False

        with pytest.raises(ValueError) as exc:
            await email_otp_service.complete_register_with_email_otp(
                pool=mock_pool,
                email="test@example.com",
                password="Pass123",
                otp="000000",
                phone=None,
            )

        assert "Invalid or expired OTP" in str(exc.value)


@pytest.mark.asyncio
async def test_start_login_with_email_otp_success(mock_pool):
    with patch(
        "app.services.email_otp_service.create_email_otp",
        new_callable=AsyncMock,
    ) as mock_create_otp, patch(
        "app.services.email_otp_service.send_otp_email"
    ) as mock_send_email:
        mock_create_otp.return_value = "123456"

        result = await email_otp_service.start_login_with_email_otp(
            pool=mock_pool,
            email="test@example.com",
        )

        assert result["success"] is True
        mock_create_otp.assert_awaited_once_with(
            mock_pool, email="test@example.com", purpose="login", ttl_minutes=10
        )
        mock_send_email.assert_called_once_with("test@example.com", "123456")


@pytest.mark.asyncio
async def test_complete_login_with_email_otp_without_new_password(mock_pool):
    with patch(
        "app.services.email_otp_service.verify_email_otp",
        new_callable=AsyncMock,
    ) as mock_verify:
        mock_verify.return_value = True

        result = await email_otp_service.complete_login_with_email_otp(
            pool=mock_pool,
            email="test@example.com",
            otp="123456",
            new_password=None,
        )

        assert result == {
            "success": True,
            "message": "OTP verified; please set new password",
        }


@pytest.mark.asyncio
async def test_complete_login_with_email_otp_with_new_password(mock_pool):
    with patch(
        "app.services.email_otp_service.verify_email_otp",
        new_callable=AsyncMock,
    ) as mock_verify, patch(
        "app.services.email_otp_service.supabase_service.login"
    ) as mock_login:
        mock_verify.return_value = True
        mock_login.return_value = {
            "access_token": "token123",
            "refresh_token": "ref456",
        }

        result = await email_otp_service.complete_login_with_email_otp(
            pool=mock_pool,
            email="test@example.com",
            otp="123456",
            new_password="NewPass123",
        )

        assert result["access_token"] == "token123"
        mock_verify.assert_awaited_once_with(
            mock_pool, email="test@example.com", otp="123456", purpose="login"
        )
        mock_login.assert_called_once_with("test@example.com", "NewPass123")
