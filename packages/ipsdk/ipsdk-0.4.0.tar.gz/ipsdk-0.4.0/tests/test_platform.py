# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import httpx
import pytest

from ipsdk import exceptions
from ipsdk.connection import AsyncConnection
from ipsdk.connection import Connection
from ipsdk.connection import Response
from ipsdk.platform import AsyncAuthMixin
from ipsdk.platform import AuthMixin
from ipsdk.platform import Platform
from ipsdk.platform import _make_basicauth_body
from ipsdk.platform import _make_basicauth_path
from ipsdk.platform import _make_oauth_body
from ipsdk.platform import _make_oauth_headers
from ipsdk.platform import _make_oauth_path
from ipsdk.platform import platform_factory

# --------- Factory Tests ---------


def test_platform_factory_default():
    """Test platform_factory with default parameters."""
    conn = platform_factory()
    assert isinstance(conn, Platform)
    assert conn.user == "admin"
    assert conn.password == "admin"
    assert conn.client_id is None
    assert conn.client_secret is None


def test_platform_factory_returns_connection():
    """Test that platform_factory returns a Connection instance."""
    p = platform_factory()
    assert isinstance(p, Connection)


def test_platform_factory_returns_async():
    """Test that platform_factory returns AsyncConnection when want_async=True."""
    p = platform_factory(want_async=True)
    assert isinstance(p, AsyncConnection)


def test_platform_factory_custom_params():
    """Test platform_factory with custom parameters."""
    conn = platform_factory(
        host="platform.example.com",
        port=443,
        user="custom_user",
        password="custom_pass",
        client_id="test_client",
        client_secret="test_secret",
        use_tls=True,
        verify=False,
        timeout=120,
    )
    assert isinstance(conn, Platform)
    assert conn.user == "custom_user"
    assert conn.password == "custom_pass"
    assert conn.client_id == "test_client"
    assert conn.client_secret == "test_secret"


def test_platform_factory_oauth_only():
    """Test platform_factory with only OAuth credentials."""
    conn = platform_factory(
        client_id="oauth_client", client_secret="oauth_secret", user=None, password=None
    )
    assert conn.client_id == "oauth_client"
    assert conn.client_secret == "oauth_secret"
    assert conn.user is None
    assert conn.password is None


def test_platform_authentication_fallback():
    """Test platform authentication fails when no credentials provided."""
    conn = platform_factory(client_id=None, client_secret=None)
    # auth should fail gracefully since no server is running
    conn.client_id = None
    conn.client_secret = None
    conn.user = None
    conn.password = None
    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        conn.authenticate()


# --------- Helper Function Tests ---------


def test_make_oauth_headers():
    """Test _make_oauth_headers utility function."""
    headers = _make_oauth_headers()
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_make_oauth_path():
    """Test _make_oauth_path utility function."""
    assert _make_oauth_path() == "/oauth/token"


def test_make_oauth_body():
    """Test _make_oauth_body utility function."""
    result = _make_oauth_body("test_id", "test_secret")
    expected = {
        "grant_type": "client_credentials",
        "client_id": "test_id",
        "client_secret": "test_secret",
    }
    assert result == expected


def test_make_oauth_body_special_chars():
    """Test _make_oauth_body with special characters."""
    result = _make_oauth_body("client@domain.com", "secret!@#$%")
    expected = {
        "grant_type": "client_credentials",
        "client_id": "client@domain.com",
        "client_secret": "secret!@#$%",
    }
    assert result == expected


def test_make_basicauth_body():
    """Test _make_basicauth_body utility function."""
    result = _make_basicauth_body("testuser", "testpass")
    expected = {"user": {"username": "testuser", "password": "testpass"}}
    assert result == expected


def test_make_basicauth_path():
    """Test _make_basicauth_path utility function."""
    assert _make_basicauth_path() == "/login"


# --------- Sync AuthMixin Tests ---------


def test_authenticate_oauth_success():
    """Test AuthMixin.authenticate_oauth successful authentication."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "test_token_123"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch(
        "ipsdk.jsonutils.loads", return_value={"access_token": "test_token_123"}
    ):
        mixin.authenticate_oauth()

    assert mixin.token == "test_token_123"
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )


def test_authenticate_oauth_401_unauthorized():
    """Test AuthMixin.authenticate_oauth with 401 unauthorized."""
    mixin = AuthMixin()
    mixin.client_id = "invalid_id"
    mixin.client_secret = "invalid_secret"
    mixin.client = Mock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"


def test_authenticate_oauth_network_error():
    """Test AuthMixin.authenticate_oauth with network error."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = Mock()

    # Mock network error
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"
    exception = httpx.ConnectError("Connection refused", request=mock_request)
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.NetworkError) as exc_info:
        mixin.authenticate_oauth()

    assert "Network error during OAuth authentication" in str(exc_info.value)


def test_authenticate_user_success():
    """Test AuthMixin.authenticate_user successful authentication."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    mixin.authenticate_user()

    mixin.client.post.assert_called_once_with(
        "/login", json={"user": {"username": "testuser", "password": "testpass"}}
    )


def test_authenticate_user_401_unauthorized():
    """Test AuthMixin.authenticate_user with 401 unauthorized."""
    mixin = AuthMixin()
    mixin.user = "testuser"
    mixin.password = "wrongpass"
    mixin.client = Mock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/login"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        mixin.authenticate_user()

    assert "Basic authentication failed - invalid username or password" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "basic"


def test_authenticate_prefers_oauth():
    """Test that authenticate prefers OAuth when both credentials are available."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock OAuth success
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "oauth_token"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "oauth_token"}):
        mixin.authenticate()

    # Should have called OAuth, not basic auth
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )
    assert mixin.token == "oauth_token"


def test_authenticate_oauth_preferred_over_basic():
    """Test that authenticate uses OAuth when both OAuth and basic credentials are
    available."""
    mixin = AuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = Mock()

    # Mock OAuth success
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "oauth_token"}'
    mock_response.raise_for_status.return_value = None
    mixin.client.post.return_value = mock_response

    with patch("ipsdk.jsonutils.loads", return_value={"access_token": "oauth_token"}):
        mixin.authenticate()

    # Should have called OAuth (not basic auth) since OAuth credentials are preferred
    mixin.client.post.assert_called_once_with(
        "/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
        },
    )
    assert mixin.token == "oauth_token"


def test_authenticate_no_credentials_error():
    """Test authenticate raises error when no credentials provided."""
    mixin = AuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        mixin.authenticate()


# --------- Async AuthMixin Tests ---------


@pytest.mark.asyncio
async def test_async_authenticate_oauth_success():
    """Test AsyncAuthMixin.authenticate_oauth successful authentication."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "test_id"
    mixin.client_secret = "test_secret"
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.text = '{"access_token": "async_token_123"}'
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    with patch(
        "ipsdk.jsonutils.loads", return_value={"access_token": "async_token_123"}
    ):
        await mixin.authenticate_oauth()

    assert mixin.token == "async_token_123"
    mixin.client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_authenticate_basicauth_success():
    """Test AsyncAuthMixin.authenticate_basicauth successful authentication."""
    mixin = AsyncAuthMixin()
    mixin.user = "testuser"
    mixin.password = "testpass"
    mixin.client = AsyncMock()

    # Mock successful response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status = Mock()
    mixin.client.post.return_value = mock_response

    await mixin.authenticate_basicauth()
    mixin.client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_authenticate_oauth_401_unauthorized():
    """Test AsyncAuthMixin.authenticate_oauth with 401 unauthorized."""
    mixin = AsyncAuthMixin()
    mixin.client_id = "invalid_id"
    mixin.client_secret = "invalid_secret"
    mixin.client = AsyncMock()

    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_request = Mock()
    mock_request.url = "https://platform.example.com/oauth/token"

    exception = httpx.HTTPStatusError(
        "Unauthorized", request=mock_request, response=mock_response
    )
    mixin.client.post.side_effect = exception

    with pytest.raises(exceptions.AuthenticationError) as exc_info:
        await mixin.authenticate_oauth()

    assert "OAuth authentication failed - invalid client credentials" in str(
        exc_info.value
    )
    assert exc_info.value.details.get("auth_type") == "oauth"


@pytest.mark.asyncio
async def test_async_authenticate_no_credentials_error():
    """Test async authenticate raises error when no credentials provided."""
    mixin = AsyncAuthMixin()
    mixin.client_id = None
    mixin.client_secret = None
    mixin.user = None
    mixin.password = None

    with pytest.raises(
        exceptions.AuthenticationError,
        match="No valid authentication credentials provided",
    ):
        await mixin.authenticate()


# --------- Integration Tests ---------


def test_platform_integration_with_connection():
    """Test that Platform integrates properly with Connection base class."""
    platform = platform_factory()

    # Verify it has the expected connection methods
    assert hasattr(platform, "get")
    assert hasattr(platform, "post")
    assert hasattr(platform, "put")
    assert hasattr(platform, "delete")
    assert hasattr(platform, "patch")
    assert hasattr(platform, "authenticate")

    # Verify credentials are set correctly
    assert platform.user == "admin"
    assert platform.password == "admin"


def test_platform_base_url_construction():
    """Test that Platform constructs the correct base URL."""
    platform = platform_factory(host="platform.example.com", port=443, use_tls=True)

    # Platform should have no base path (direct to host)
    expected_base_url = "https://platform.example.com"
    assert str(platform.client.base_url) == expected_base_url


def test_platform_authentication_not_called_initially():
    """Test that Platform doesn't authenticate until first API call."""
    platform = platform_factory()

    # Authentication should not have been called yet
    assert not platform.authenticated
    assert platform.token is None


def test_platform_oauth_token_handling():
    """Test that Platform properly handles OAuth tokens."""
    platform = platform_factory(client_id="test_client", client_secret="test_secret")

    # Token should be None initially
    assert platform.token is None

    # After setting a token, it should be available
    platform.token = "test_token_value"
    assert platform.token == "test_token_value"
