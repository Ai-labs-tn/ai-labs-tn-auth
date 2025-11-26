import json
import pytest
from unittest.mock import patch, MagicMock

from app.services import supabase_service
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


@pytest.fixture
def mock_post():
    """Mock for requests.post to avoid making real HTTP calls."""
    with patch("app.services.supabase_service.requests.post") as mock:
        yield mock


# ------------------------------------------------------------------------------
# TEST: register()
# ------------------------------------------------------------------------------
def test_register_success(mock_post):
    # Mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "user123", "email": "test@example.com"}
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    email = "test@example.com"
    phone = None
    password = "Pass123"

    result = supabase_service.register(email=email, phone=phone, password=password)

    # Validate return value
    assert result["id"] == "user123"
    assert result["email"] == email

    # Validate correct URL was used
    expected_url = f"{SUPABASE_URL}/auth/v1/admin/users"
    mock_post.assert_called_once()

    called_url = mock_post.call_args.args[0]
    assert called_url == expected_url

    # Validate headers & payload
    called_payload = mock_post.call_args.kwargs["json"]
    called_headers = mock_post.call_args.kwargs["headers"]

    assert called_payload == {
        "password": password,
        "email": email,
        "phone": None,
        "email_confirm": True,
        "phone_confirm": False,
    }

    assert called_headers == {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }


def test_register_failure(mock_post):
    """Ensure register() raises exception when Supabase returns 400."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Bad Request")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        supabase_service.register(email="x@test.com", phone=None, password="123456")


# ------------------------------------------------------------------------------
# TEST: login()
# ------------------------------------------------------------------------------
def test_login_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "access_token": "token123",
        "refresh_token": "refreshXYZ",
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    email = "test@example.com"
    password = "Pass123"

    result = supabase_service.login(email, password)

    assert result["access_token"] == "token123"

    expected_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    mock_post.assert_called_once()

    called_url = mock_post.call_args.args[0]
    assert called_url == expected_url

    called_payload = mock_post.call_args.kwargs["json"]
    assert called_payload == {"email": email, "password": password}


def test_login_failure(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Unauthorized")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        supabase_service.login("wrong@example.com", "badpassword")


# ------------------------------------------------------------------------------
# TEST: refresh()
# ------------------------------------------------------------------------------
def test_refresh_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
    }
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    refresh_token = "old_refresh"
    result = supabase_service.refresh(refresh_token)

    assert result["access_token"] == "new_access"

    expected_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
    mock_post.assert_called_once()

    called_payload = mock_post.call_args.kwargs["json"]
    assert called_payload == {"refresh_token": refresh_token}


def test_refresh_failure(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Invalid refresh token")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        supabase_service.refresh("badtoken")
