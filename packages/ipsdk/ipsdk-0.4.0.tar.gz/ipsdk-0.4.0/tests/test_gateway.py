# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock
from unittest.mock import Mock

import httpx
import pytest

from ipsdk import exceptions
from ipsdk.connection import Response
from ipsdk.gateway import AsyncAuthMixin
from ipsdk.gateway import AuthMixin
from ipsdk.gateway import Gateway
from ipsdk.gateway import _make_body
from ipsdk.gateway import _make_headers
from ipsdk.gateway import _make_path
from ipsdk.gateway import gateway_factory

# --------- Factory Tests ---------


def test_gateway_factory_default():
    """Test gateway_factory with default parameters."""
    conn = gateway_factory()
    assert isinstance(conn, Gateway)
    assert conn.user == "admin@itential"
    assert conn.password == "admin"


def test_gateway_factory_custom_params():
    """Test gateway_factory with custom parameters."""
    conn = gateway_factory(
        host="gateway.example.com",
        port=8443,
        user="custom_user",
        password="custom_pass",
        use_tls=False,
        verify=False,
        timeout=60,
    )
    assert isinstance(conn, Gateway)
    assert conn.user == "custom_user"
    assert conn.password == "custom_pass"


def test_gateway_factory_async():
    """Test gateway_factory with async=True."""
    from ipsdk.connection import AsyncConnection

    conn = gateway_factory(want_async=True)
    assert isinstance(conn, AsyncConnection)
    assert hasattr(conn, "authenticate")


# --------- Utility Function Tests ---------


def test_make_path():
    """Test _make_path utility function."""
    assert _make_path() == "/login"


def test_make_body():
    """Test _make_body utility function."""
    result = _make_body("user1", "pass1")
    expected = {"username": "user1", "password": "pass1"}
    assert result == expected


def test_make_body_with_special_chars():
    """Test _make_body with special characters."""
    result = _make_body("user@domain.com", "p@ssw0rd!")
    expected = {"username": "user@domain.com", "password": "p@ssw0rd!"}
    assert result == expected


def test_make_headers():
    """Test _make_headers utility function."""
    headers = _make_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


# --------- Sync AuthMixin Tests ---------


def test_auth_mixin_authenticate_success():
    """Test AuthMixin.authenticate successful authentication."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    mixin.authenticate()

    mixin.client.post.assert_called_once_with(
        "/login",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"username": "admin", "password": "adminpass"},
    )
    mock_response.raise_for_status.assert_called_once()


def test_auth_mixin_authenticate_401_unauthorized():
    """Test AuthMixin.authenticate with 401 unauthorized."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "wrongpass"
    mixin.client = Mock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate()

    assert "Gateway authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details["status_code"] == 401


def test_auth_mixin_authenticate_403_forbidden():
    """Test AuthMixin.authenticate with 403 forbidden."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    # Mock 403 response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"

    exception = httpx.HTTPStatusError(
        "Forbidden", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate()

    assert "Gateway authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details["status_code"] == 403


def test_auth_mixin_authenticate_500_server_error():
    """Test AuthMixin.authenticate with 500 server error."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    # Mock 500 response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"

    exception = httpx.HTTPStatusError(
        "Internal Server Error", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate()

    assert "Gateway authentication failed with status 500" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert exc_info.value.details["status_code"] == 500


def test_auth_mixin_authenticate_network_error():
    """Test AuthMixin.authenticate with network error."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    # Mock network error
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"
    exception = httpx.ConnectError("Connection refused", request=mock_request)
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate()

    assert "Network error during gateway authentication" in str(exc_info.value)
    assert "Connection refused" in exc_info.value.details["original_error"]


def test_auth_mixin_authenticate_generic_exception():
    """Test AuthMixin.authenticate with generic exception."""
    mixin = AuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = Mock()

    # Mock generic exception
    mixin.client.post.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate()

    assert "Unexpected error during gateway authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"
    assert "Unexpected error" in exc_info.value.details["original_error"]


# --------- Async AuthMixin Tests ---------


@pytest.mark.asyncio
async def test_async_auth_mixin_authenticate_success():
    """Test AsyncAuthMixin.authenticate successful authentication."""
    mixin = AsyncAuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    await mixin.authenticate()

    mixin.client.post.assert_awaited_once_with(
        "/login",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"username": "admin", "password": "adminpass"},
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_async_auth_mixin_authenticate_401_unauthorized():
    """Test AsyncAuthMixin.authenticate with 401 unauthorized."""
    mixin = AsyncAuthMixin()
    mixin.user = "admin"
    mixin.password = "wrongpass"
    mixin.client = AsyncMock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate()

    assert "Gateway authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"


@pytest.mark.asyncio
async def test_async_auth_mixin_authenticate_network_error():
    """Test AsyncAuthMixin.authenticate with network error."""
    mixin = AsyncAuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = AsyncMock()

    # Mock network error
    mock_request = Mock()
    mock_request.url = "https://gateway.example.com/login"
    exception = httpx.ConnectError("Connection refused", request=mock_request)
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.NetworkError) as exc_info:
        await mixin.authenticate()

    assert "Network error during gateway authentication" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_auth_mixin_authenticate_generic_exception():
    """Test AsyncAuthMixin.authenticate with generic exception."""
    mixin = AsyncAuthMixin()
    mixin.user = "admin"
    mixin.password = "adminpass"
    mixin.client = AsyncMock()

    # Mock generic exception
    mixin.client.post.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate()

    assert "Unexpected error during gateway authentication" in str(exc_info.value)
    assert exc_info.value.details.get("auth_type") == "basic"


# --------- Integration Tests ---------


def test_gateway_integration_with_connection():
    """Test that Gateway integrates properly with Connection base class."""
    gateway = gateway_factory()

    # Verify it has the expected connection methods
    assert hasattr(gateway, "get")
    assert hasattr(gateway, "post")
    assert hasattr(gateway, "put")
    assert hasattr(gateway, "delete")
    assert hasattr(gateway, "patch")
    assert hasattr(gateway, "authenticate")

    # Verify user and password are set correctly
    assert gateway.user == "admin@itential"
    assert gateway.password == "admin"


def test_gateway_base_url_construction():
    """Test that Gateway constructs the correct base URL."""
    gateway = gateway_factory(host="gateway.example.com", port=8443, use_tls=True)

    # The base URL should include the API path for gateway
    expected_base_url = "https://gateway.example.com:8443/api/v2.0/"
    assert str(gateway.client.base_url) == expected_base_url


def test_gateway_authentication_not_called_initially():
    """Test that Gateway doesn't authenticate until first API call."""
    gateway = gateway_factory()

    # Authentication should not have been called yet
    assert not gateway.authenticated
    assert gateway.token is None
