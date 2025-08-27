# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import httpx
import pytest

from ipsdk import exceptions
from ipsdk.connection import AsyncConnection
from ipsdk.connection import Connection
from ipsdk.connection import ConnectionBase
from ipsdk.connection import HTTPMethod
from ipsdk.connection import Request
from ipsdk.connection import Response

# --------- Fixtures ---------


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx.Response for testing."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.content = b'{"key": "value"}'
    mock_response.text = '{"key": "value"}'
    mock_response.url = httpx.URL("https://example.com/api/test")
    mock_response.request = Mock()
    mock_response.json.return_value = {"key": "value"}
    return mock_response


@pytest.fixture
def connection_base_mock():
    """Create a ConnectionBase instance with mocked dependencies."""
    with patch.object(ConnectionBase, "_init_client") as mock_init:
        mock_client = Mock()
        mock_client.headers = {}
        mock_init.return_value = mock_client

        conn = ConnectionBase("example.com")
        yield conn


@pytest.fixture
def connection_mock():
    """Create a Connection instance with mocked dependencies."""
    with patch.object(ConnectionBase, "__init__", lambda self, *args, **kwargs: None):
        conn = Connection("example.com")
        conn.authenticated = False
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())
        yield conn


@pytest.fixture
def async_connection_mock():
    """Create an AsyncConnection instance with mocked dependencies."""
    with patch.object(ConnectionBase, "__init__", lambda self, *args, **kwargs: None):
        conn = AsyncConnection("example.com")
        conn.authenticated = False
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())
        conn.authenticate = AsyncMock()
        yield conn


# --------- HTTPMethod Tests ---------


def test_http_method_constants():
    """Test that HTTPMethod class has correct constants."""
    assert HTTPMethod.GET == "GET"
    assert HTTPMethod.POST == "POST"
    assert HTTPMethod.DELETE == "DELETE"
    assert HTTPMethod.PUT == "PUT"
    assert HTTPMethod.PATCH == "PATCH"


# --------- Request Class Tests ---------


def test_request_creation():
    """Test creating a basic Request object."""
    req = Request("GET", "/api/test")
    assert req.method == "GET"
    assert req.path == "/api/test"
    assert req.params == {}
    assert req.headers == {}
    assert req.json is None


def test_request_with_all_params():
    """Test creating a Request with all parameters."""
    params = {"key": "value"}
    headers = {"Authorization": "Bearer token"}
    json_data = {"data": "test"}

    req = Request(
        method="POST",
        path="/api/create",
        params=params,
        headers=headers,
        json=json_data,
    )

    assert req.method == "POST"
    assert req.path == "/api/create"
    assert req.params == params
    assert req.headers == headers
    assert req.json == json_data


def test_request_url_property():
    """Test Request url property."""
    req = Request("GET", "/api/test")
    assert req.url == "/api/test"


def test_request_repr():
    """Test Request string representation."""
    req = Request("GET", "/api/test")
    expected = "Request(method='GET', path='/api/test')"
    assert repr(req) == expected


def test_request_with_none_params():
    """Test Request with None params and headers."""
    req = Request("GET", "/api/test", params=None, headers=None)
    assert req.params == {}
    assert req.headers == {}


def test_request_with_different_json_types():
    """Test Request with different JSON data types."""
    # Test with dict
    req_dict = Request("POST", "/api/test", json={"key": "value"})
    assert req_dict.json == {"key": "value"}

    # Test with list
    req_list = Request("POST", "/api/test", json=[1, 2, 3])
    assert req_list.json == [1, 2, 3]

    # Test with string
    req_str = Request("POST", "/api/test", json='{"key": "value"}')
    assert req_str.json == '{"key": "value"}'

    # Test with bytes
    req_bytes = Request("POST", "/api/test", json=b'{"key": "value"}')
    assert req_bytes.json == b'{"key": "value"}'


def test_request_empty_path():
    """Test Request with empty path."""
    req = Request("GET", "")
    assert req.path == ""
    assert req.url == ""


# --------- Response Class Tests ---------


def test_response_creation(mock_httpx_response):
    """Test creating a Response object."""
    response = Response(mock_httpx_response)
    assert response.status_code == 200
    assert response.headers == {"Content-Type": "application/json"}
    assert response.content == b'{"key": "value"}'
    assert response.text == '{"key": "value"}'
    assert response.url == httpx.URL("https://example.com/api/test")
    assert response.request is not None


def test_response_none_httpx_response():
    """Test Response creation with None httpx_response raises ValueError."""
    with pytest.raises(ValueError, match="httpx_response cannot be None"):
        Response(None)


def test_response_json_success(mock_httpx_response):
    """Test Response json method returns parsed JSON."""
    response = Response(mock_httpx_response)
    result = response.json()
    assert result == {"key": "value"}


def test_response_json_failure():
    """Test Response json method raises ValueError on parse error."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

    response = Response(mock_response)
    with pytest.raises(ValueError, match="Failed to parse response as JSON"):
        response.json()


def test_response_raise_for_status():
    """Test Response raise_for_status delegates to httpx response."""
    mock_response = Mock(spec=httpx.Response)
    response = Response(mock_response)

    response.raise_for_status()
    mock_response.raise_for_status.assert_called_once()


def test_response_is_success():
    """Test Response is_success method."""
    mock_response = Mock(spec=httpx.Response)

    # Test successful status codes
    for status in [200, 201, 204, 299]:
        mock_response.status_code = status
        response = Response(mock_response)
        assert response.is_success() is True

    # Test non-successful status codes
    for status in [199, 300, 400, 404, 500]:
        mock_response.status_code = status
        response = Response(mock_response)
        assert response.is_success() is False


def test_response_is_error():
    """Test Response is_error method."""
    mock_response = Mock(spec=httpx.Response)

    # Test error status codes
    for status in [400, 401, 404, 500, 502]:
        mock_response.status_code = status
        response = Response(mock_response)
        assert response.is_error() is True

    # Test non-error status codes
    for status in [200, 201, 299, 300, 399]:
        mock_response.status_code = status
        response = Response(mock_response)
        assert response.is_error() is False


def test_response_repr():
    """Test Response string representation."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.url = httpx.URL("https://example.com/api/test")

    response = Response(mock_response)
    expected = "Response(status_code=200, url='https://example.com/api/test')"
    assert repr(response) == expected


def test_response_various_status_codes():
    """Test Response with various HTTP status codes."""
    status_codes = [100, 200, 201, 204, 301, 400, 401, 403, 404, 500, 502]

    for status_code in status_codes:
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = status_code

        response = Response(mock_response)
        assert response.status_code == status_code

        # Test success/error classification
        if 200 <= status_code < 300:
            assert response.is_success() is True
            assert response.is_error() is False
        elif status_code >= 400:
            assert response.is_error() is True
            assert response.is_success() is False
        else:
            assert response.is_success() is False
            assert response.is_error() is False


def test_response_json_with_different_exceptions():
    """Test Response json method with different exception types."""
    mock_response = Mock(spec=httpx.Response)

    # Test with JSONDecodeError
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    response = Response(mock_response)
    with pytest.raises(ValueError, match="Failed to parse response as JSON"):
        response.json()

    # Test with generic exception
    mock_response.json.side_effect = RuntimeError("Generic error")
    response = Response(mock_response)
    with pytest.raises(
        ValueError, match="Failed to parse response as JSON: Generic error"
    ):
        response.json()


def test_response_properties_delegation():
    """Test that Response properly delegates properties to httpx response."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 201
    mock_response.headers = {"X-Custom": "value"}
    mock_response.content = b"test content"
    mock_response.text = "test content"
    mock_response.url = httpx.URL("https://test.com")
    mock_request = Mock()
    mock_response.request = mock_request

    response = Response(mock_response)

    # Verify all properties are correctly delegated
    assert response.status_code == 201
    assert response.headers == {"X-Custom": "value"}
    assert response.content == b"test content"
    assert response.text == "test content"
    assert response.url == httpx.URL("https://test.com")
    assert response.request is mock_request


# --------- ConnectionBase Tests ---------


class TestConnectionBase:
    """Test suite for ConnectionBase class."""

    def test_make_base_url_default_ports(self):
        """Test _make_base_url with default ports."""
        # Mock _init_client since ConnectionBase is abstract
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")

            # Test HTTPS default port
            url = conn._make_base_url("example.com", 0, None, True)
            assert url == "https://example.com"

            # Test HTTP default port
            url = conn._make_base_url("example.com", 0, None, False)
            assert url == "http://example.com"

    def test_make_base_url_custom_ports(self):
        """Test _make_base_url with custom ports."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")

            # Test custom port for HTTPS
            url = conn._make_base_url("example.com", 8443, None, True)
            assert url == "https://example.com:8443"

            # Test custom port for HTTP
            url = conn._make_base_url("example.com", 8080, None, False)
            assert url == "http://example.com:8080"

    def test_make_base_url_with_base_path(self):
        """Test _make_base_url with base path."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")

            url = conn._make_base_url("example.com", 0, "/api/v1", True)
            assert url == "https://example.com/api/v1"

    def test_make_base_url_standard_ports(self):
        """Test _make_base_url with standard ports (80, 443)."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")

            # Standard HTTPS port should not appear in URL
            url = conn._make_base_url("example.com", 443, None, True)
            assert url == "https://example.com"

            # Standard HTTP port should not appear in URL
            url = conn._make_base_url("example.com", 80, None, False)
            assert url == "http://example.com"

    def test_build_request_basic(self):
        """Test _build_request with basic parameters."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")
            conn.client = Mock()
            conn.token = None

            mock_request = Mock()
            conn.client.build_request.return_value = mock_request

            request = conn._build_request("GET", "/api/test")

            conn.client.build_request.assert_called_once_with(
                method="GET", url="/api/test", params=None, headers={}, json=None
            )
            assert request == mock_request

    def test_build_request_with_json(self):
        """Test _build_request with JSON data."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")
            conn.client = Mock()
            conn.token = None

            mock_request = Mock()
            conn.client.build_request.return_value = mock_request

            json_data = {"key": "value"}
            conn._build_request("POST", "/api/create", json=json_data)

            expected_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            conn.client.build_request.assert_called_once_with(
                method="POST",
                url="/api/create",
                params=None,
                headers=expected_headers,
                json=json_data,
            )

    def test_build_request_with_token(self):
        """Test _build_request with authentication token."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")
            conn.client = Mock()
            conn.token = "test-token"

            mock_request = Mock()
            conn.client.build_request.return_value = mock_request

            conn._build_request("GET", "/api/test")

            expected_headers = {"Authorization": "Bearer test-token"}
            conn.client.build_request.assert_called_once_with(
                method="GET",
                url="/api/test",
                params=None,
                headers=expected_headers,
                json=None,
            )

    def test_build_request_with_params(self):
        """Test _build_request with query parameters."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")
            conn.client = Mock()
            conn.token = None

            mock_request = Mock()
            conn.client.build_request.return_value = mock_request

            params = {"key": "value", "limit": 10}
            conn._build_request("GET", "/api/test", params=params)

            conn.client.build_request.assert_called_once_with(
                method="GET", url="/api/test", params=params, headers={}, json=None
            )

    def test_initialization_with_all_params(self):
        """Test ConnectionBase initialization with all parameters."""
        with patch.object(ConnectionBase, "_init_client") as mock_init:
            mock_client = Mock()
            mock_client.headers = {}
            mock_init.return_value = mock_client

            conn = ConnectionBase(
                host="example.com",
                port=8443,
                base_path="/api/v1",
                use_tls=True,
                verify=True,
                user="testuser",
                password="testpass",
                client_id="test_id",
                client_secret="test_secret",
                timeout=60,
            )

            assert conn.user == "testuser"
            assert conn.password == "testpass"
            assert conn.client_id == "test_id"
            assert conn.client_secret == "test_secret"
            assert conn.token is None
            assert conn.authenticated is False

            mock_init.assert_called_once_with(
                base_url="https://example.com:8443/api/v1", verify=True, timeout=60
            )

    def test_make_base_url_edge_cases(self):
        """Test _make_base_url with edge cases."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")

            # Test with IP address
            url = conn._make_base_url("192.168.1.1", 0, None, True)
            assert url == "https://192.168.1.1"

            # Test with localhost
            url = conn._make_base_url("localhost", 3000, None, False)
            assert url == "http://localhost:3000"

            # Test with empty base_path vs None
            url = conn._make_base_url("example.com", 0, "", True)
            assert url == "https://example.com"

            # Test with base_path starting with slash
            url = conn._make_base_url("example.com", 0, "/api/v2", True)
            assert url == "https://example.com/api/v2"

            # Test with base_path not starting with slash
            url = conn._make_base_url("example.com", 0, "api/v2", True)
            assert url == "https://example.com/api/v2"

    def test_build_request_edge_cases(self):
        """Test _build_request with edge cases."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = ConnectionBase("example.com")
            conn.client = Mock()
            conn.token = None

            mock_request = Mock()
            conn.client.build_request.return_value = mock_request

            # Test with empty params dict
            conn._build_request("GET", "/api/test", params={})
            conn.client.build_request.assert_called_with(
                method="GET", url="/api/test", params={}, headers={}, json=None
            )

            # Test with empty headers dict
            conn._build_request("GET", "/api/test", json=None)

            # Test with both token and json data
            conn.token = "test-token"
            json_data = {"test": "data"}
            conn._build_request("POST", "/api/test", json=json_data)

            expected_headers = {
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            conn.client.build_request.assert_called_with(
                method="POST",
                url="/api/test",
                params=None,
                headers=expected_headers,
                json=json_data,
            )


# --------- Connection Class Tests ---------


class TestConnection:
    """Test suite for Connection class."""

    def test_init_client(self):
        """Test Connection _init_client method."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = Connection("example.com")
        client = conn._init_client("https://example.com", True, 30)
        assert isinstance(client, httpx.Client)

    @patch("ipsdk.connection.httpx.Client")
    @patch.object(ConnectionBase, "__init__", lambda self, *args, **kwargs: None)
    def test_init_client_with_params(self, mock_client_class):
        """Test Connection _init_client with specific parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        conn = Connection("example.com")
        result = conn._init_client("https://example.com/api", False, 60)

        mock_client_class.assert_called_once_with(
            base_url="https://example.com/api", verify=False, timeout=60
        )
        assert result == mock_client

    def test_send_request_authentication(self):
        """Test _send_request triggers authentication when needed."""
        with patch.object(Connection, "authenticate") as mock_auth:
            conn = Connection("example.com")
            conn.authenticated = False
            conn.client = Mock()

            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            conn.client.send.return_value = mock_response
            conn._build_request = Mock(return_value=Mock())

            result = conn._send_request("GET", "/api/test")

            mock_auth.assert_called_once()
            assert conn.authenticated is True
            assert isinstance(result, Response)

    def test_send_request_no_authentication_when_already_authenticated(self):
        """Test _send_request skips authentication when already authenticated."""
        with patch.object(Connection, "authenticate") as mock_auth:
            conn = Connection("example.com")
            conn.authenticated = True
            conn.client = Mock()

            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            conn.client.send.return_value = mock_response
            conn._build_request = Mock(return_value=Mock())

            result = conn._send_request("GET", "/api/test")

            mock_auth.assert_not_called()
            assert isinstance(result, Response)

    def test_send_request_httpx_request_error(self):
        """Test _send_request handles httpx.RequestError."""
        conn = Connection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"

        exception = httpx.RequestError("Connection failed", request=mock_request)
        conn.client.send.side_effect = exception

        with pytest.raises(exceptions.NetworkError):
            conn._send_request("GET", "/api/test")

    def test_send_request_httpx_status_error(self):
        """Test _send_request handles httpx.HTTPStatusError."""
        conn = Connection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"
        mock_response = Mock()
        mock_response.status_code = 500

        exception = httpx.HTTPStatusError(
            "Server error", request=mock_request, response=mock_response
        )
        conn.client.send.side_effect = exception

        with pytest.raises(exceptions.ServerError):
            conn._send_request("GET", "/api/test")

    def test_send_request_generic_exception(self):
        """Test _send_request handles generic exceptions."""
        conn = Connection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        conn.client.send.side_effect = RuntimeError("Generic error")

        with pytest.raises(exceptions.IpsdkError):
            conn._send_request("GET", "/api/test")

    def test_get_method(self):
        """Test Connection get method."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        result = conn.get("/api/test", params=params)

        conn._send_request.assert_called_once_with(
            "GET", path="/api/test", params=params
        )
        assert isinstance(result, Mock)

    def test_delete_method(self):
        """Test Connection delete method."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        result = conn.delete("/api/test", params=params)

        conn._send_request.assert_called_once_with(
            "DELETE", path="/api/test", params=params
        )
        assert isinstance(result, Mock)

    def test_post_method(self):
        """Test Connection post method."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = conn.post("/api/create", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "POST", path="/api/create", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    def test_put_method(self):
        """Test Connection put method."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = conn.put("/api/update", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "PUT", path="/api/update", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    def test_patch_method(self):
        """Test Connection patch method."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = conn.patch("/api/patch", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "PATCH", path="/api/patch", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    def test_http_methods_without_params(self):
        """Test HTTP methods called without optional parameters."""
        conn = Connection("example.com")
        conn._send_request = Mock(return_value=Mock(spec=Response))

        # Test all methods without params
        conn.get("/api/test")
        conn._send_request.assert_called_with("GET", path="/api/test", params=None)

        conn.delete("/api/test")
        conn._send_request.assert_called_with("DELETE", path="/api/test", params=None)

        conn.post("/api/test")
        conn._send_request.assert_called_with(
            "POST", path="/api/test", params=None, json=None
        )

        conn.put("/api/test")
        conn._send_request.assert_called_with(
            "PUT", path="/api/test", params=None, json=None
        )

        conn.patch("/api/test")
        conn._send_request.assert_called_with(
            "PATCH", path="/api/test", params=None, json=None
        )

    def test_send_request_authentication_called_once(self):
        """Test that authentication is only called once per connection."""
        with patch.object(Connection, "authenticate") as mock_auth:
            conn = Connection("example.com")
            conn.authenticated = False
            conn.client = Mock()

            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            conn.client.send.return_value = mock_response
            conn._build_request = Mock(return_value=Mock())

            # First request should trigger authentication
            conn._send_request("GET", "/api/test1")
            assert mock_auth.call_count == 1
            assert conn.authenticated is True

            # Second request should not trigger authentication
            conn._send_request("GET", "/api/test2")
            assert mock_auth.call_count == 1  # Still 1, not called again

    def test_init_client_with_none_base_url(self):
        """Test Connection _init_client with None base_url."""
        with patch.object(
            ConnectionBase, "__init__", lambda self, *args, **kwargs: None
        ):
            conn = Connection("example.com")

            with patch("ipsdk.connection.httpx.Client") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client

                result = conn._init_client(None, True, 30)

                mock_client_class.assert_called_once_with(
                    base_url="", verify=True, timeout=30
                )
                assert result == mock_client


# --------- AsyncConnection Class Tests ---------


class TestAsyncConnection:
    """Test suite for AsyncConnection class."""

    def test_init_client(self):
        """Test AsyncConnection _init_client method."""
        with patch.object(ConnectionBase, "_init_client"):
            conn = AsyncConnection("example.com")
        client = conn._init_client("https://example.com", True, 30)
        assert isinstance(client, httpx.AsyncClient)

    @patch("ipsdk.connection.httpx.AsyncClient")
    @patch.object(ConnectionBase, "__init__", lambda self, *args, **kwargs: None)
    def test_init_client_with_params(self, mock_client_class):
        """Test AsyncConnection _init_client with specific parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        conn = AsyncConnection("example.com")
        result = conn._init_client("https://example.com/api", False, 60)

        mock_client_class.assert_called_once_with(
            base_url="https://example.com/api", verify=False, timeout=60
        )
        assert result == mock_client

    @pytest.mark.asyncio
    async def test_send_request_authentication(self):
        """Test async _send_request triggers authentication when needed."""
        conn = AsyncConnection("example.com")
        conn.authenticated = False
        conn.client = Mock()

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        conn.client.send = AsyncMock(return_value=mock_response)
        conn._build_request = Mock(return_value=Mock())
        conn.authenticate = AsyncMock()

        result = await conn._send_request("GET", "/api/test")

        conn.authenticate.assert_called_once()
        assert conn.authenticated is True
        assert isinstance(result, Response)

    @pytest.mark.asyncio
    async def test_send_request_no_authentication_when_already_authenticated(self):
        """Test async _send_request skips authentication when already authenticated."""
        conn = AsyncConnection("example.com")
        conn.authenticated = True
        conn.client = Mock()

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        conn.client.send = AsyncMock(return_value=mock_response)
        conn._build_request = Mock(return_value=Mock())
        conn.authenticate = AsyncMock()

        result = await conn._send_request("GET", "/api/test")

        conn.authenticate.assert_not_called()
        assert isinstance(result, Response)

    @pytest.mark.asyncio
    async def test_send_request_httpx_request_error(self):
        """Test async _send_request handles httpx.RequestError."""
        conn = AsyncConnection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"

        exception = httpx.RequestError("Connection failed", request=mock_request)
        conn.client.send = AsyncMock(side_effect=exception)

        with pytest.raises(exceptions.NetworkError):
            await conn._send_request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_send_request_httpx_status_error(self):
        """Test async _send_request handles httpx.HTTPStatusError."""
        conn = AsyncConnection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"
        mock_response = Mock()
        mock_response.status_code = 500

        exception = httpx.HTTPStatusError(
            "Server error", request=mock_request, response=mock_response
        )
        conn.client.send = AsyncMock(side_effect=exception)

        with pytest.raises(exceptions.ServerError):
            await conn._send_request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_send_request_generic_exception(self):
        """Test async _send_request handles generic exceptions."""
        conn = AsyncConnection("example.com")
        conn.authenticated = True
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())

        conn.client.send = AsyncMock(side_effect=RuntimeError("Generic error"))

        with pytest.raises(exceptions.IpsdkError):
            await conn._send_request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_get_method(self):
        """Test AsyncConnection get method."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        result = await conn.get("/api/test", params=params)

        conn._send_request.assert_called_once_with(
            "GET", path="/api/test", params=params
        )
        assert isinstance(result, Mock)

    @pytest.mark.asyncio
    async def test_delete_method(self):
        """Test AsyncConnection delete method."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        result = await conn.delete("/api/test", params=params)

        conn._send_request.assert_called_once_with(
            "DELETE", path="/api/test", params=params
        )
        assert isinstance(result, Mock)

    @pytest.mark.asyncio
    async def test_post_method(self):
        """Test AsyncConnection post method."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = await conn.post("/api/create", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "POST", path="/api/create", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    @pytest.mark.asyncio
    async def test_put_method(self):
        """Test AsyncConnection put method."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = await conn.put("/api/update", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "PUT", path="/api/update", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    @pytest.mark.asyncio
    async def test_patch_method(self):
        """Test AsyncConnection patch method."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        params = {"key": "value"}
        json_data = {"data": "test"}
        result = await conn.patch("/api/patch", params=params, json=json_data)

        conn._send_request.assert_called_once_with(
            "PATCH", path="/api/patch", params=params, json=json_data
        )
        assert isinstance(result, Mock)

    @pytest.mark.asyncio
    async def test_async_http_methods_without_params(self):
        """Test async HTTP methods called without optional parameters."""
        conn = AsyncConnection("example.com")
        conn._send_request = AsyncMock(return_value=Mock(spec=Response))

        # Test all methods without params
        await conn.get("/api/test")
        conn._send_request.assert_called_with("GET", path="/api/test", params=None)

        await conn.delete("/api/test")
        conn._send_request.assert_called_with("DELETE", path="/api/test", params=None)

        await conn.post("/api/test")
        conn._send_request.assert_called_with(
            "POST", path="/api/test", params=None, json=None
        )

        await conn.put("/api/test")
        conn._send_request.assert_called_with(
            "PUT", path="/api/test", params=None, json=None
        )

        await conn.patch("/api/test")
        conn._send_request.assert_called_with(
            "PATCH", path="/api/test", params=None, json=None
        )

    @pytest.mark.asyncio
    async def test_async_send_request_authentication_called_once(self):
        """Test that async authentication is only called once per connection."""
        conn = AsyncConnection("example.com")
        conn.authenticated = False
        conn.client = Mock()
        conn._build_request = Mock(return_value=Mock())
        conn.authenticate = AsyncMock()

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        conn.client.send = AsyncMock(return_value=mock_response)

        # First request should trigger authentication
        await conn._send_request("GET", "/api/test1")
        assert conn.authenticate.call_count == 1
        assert conn.authenticated is True

        # Second request should not trigger authentication
        await conn._send_request("GET", "/api/test2")
        assert conn.authenticate.call_count == 1  # Still 1, not called again

    def test_async_init_client_with_none_base_url(self):
        """Test AsyncConnection _init_client with None base_url."""
        with patch.object(
            ConnectionBase, "__init__", lambda self, *args, **kwargs: None
        ):
            conn = AsyncConnection("example.com")

            with patch("ipsdk.connection.httpx.AsyncClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client

                result = conn._init_client(None, True, 30)

                mock_client_class.assert_called_once_with(
                    base_url="", verify=True, timeout=30
                )
                assert result == mock_client
