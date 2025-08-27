# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import Mock
from unittest.mock import PropertyMock

import httpx

from ipsdk import exceptions


class TestIpsdkError:
    """Test cases for the base IpsdkError exception class."""

    def test_basic_initialization(self):
        """Test basic exception initialization with just a message."""
        exc = exceptions.IpsdkError("Test error message")
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.details == {}

    def test_initialization_with_details(self):
        """Test exception initialization with details dictionary."""
        details = {"key1": "value1", "key2": 42}
        exc = exceptions.IpsdkError("Test error", details=details)
        assert str(exc) == "Test error. Details: {'key1': 'value1', 'key2': 42}"
        assert exc.message == "Test error"
        assert exc.details == details

    def test_initialization_with_none_details(self):
        """Test exception initialization with None details."""
        exc = exceptions.IpsdkError("Test error", details=None)
        assert str(exc) == "Test error"
        assert exc.details == {}

    def test_str_representation_with_details(self):
        """Test string representation includes details when present."""
        exc = exceptions.IpsdkError("Error", {"status": 500})
        assert "Details: {'status': 500}" in str(exc)

    def test_str_representation_without_details(self):
        """Test string representation without details."""
        exc = exceptions.IpsdkError("Simple error")
        assert str(exc) == "Simple error"
        assert "Details:" not in str(exc)


class TestNetworkError:
    """Test cases for NetworkError and related network exceptions."""

    def test_network_error_basic(self):
        """Test basic NetworkError initialization."""
        exc = exceptions.NetworkError("Network failed")
        assert str(exc) == "Network failed"
        assert exc.message == "Network failed"
        assert exc.details == {}

    def test_network_error_with_details(self):
        """Test NetworkError with additional details."""
        details = {"host": "example.com", "timeout": 30}
        exc = exceptions.NetworkError("Connection timeout", details=details)
        assert exc.details == details
        assert isinstance(exc, exceptions.IpsdkError)

    def test_network_error_inheritance(self):
        """Test NetworkError inheritance."""
        exc = exceptions.NetworkError("Network issue")
        assert isinstance(exc, exceptions.IpsdkError)
        assert isinstance(exc, exceptions.NetworkError)


class TestAuthenticationError:
    """Test cases for AuthenticationError and related authentication exceptions."""

    def test_authentication_error_basic(self):
        """Test basic AuthenticationError initialization."""
        exc = exceptions.AuthenticationError("Auth failed")
        assert str(exc) == "Auth failed"
        assert exc.message == "Auth failed"
        assert exc.details == {}

    def test_authentication_error_with_details(self):
        """Test AuthenticationError with additional details."""
        details = {"auth_type": "oauth", "username": "testuser"}
        exc = exceptions.AuthenticationError("Login failed", details=details)
        assert exc.details == details
        assert isinstance(exc, exceptions.IpsdkError)

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inheritance."""
        exc = exceptions.AuthenticationError("Auth issue")
        assert isinstance(exc, exceptions.IpsdkError)
        assert isinstance(exc, exceptions.AuthenticationError)


class TestHTTPError:
    """Test cases for HTTPError and its subclasses."""

    def test_http_error_basic(self):
        """Test basic HTTPError initialization."""
        exc = exceptions.HTTPError("HTTP error")
        assert str(exc) == "HTTP error"
        assert exc.message == "HTTP error"
        assert exc.details == {}
        assert exc.status_code is None
        assert exc.response is None
        assert exc.request_url is None

    def test_http_error_with_all_params(self):
        """Test HTTPError with all parameters."""
        response = Mock()
        response.text = "Error response body"
        exc = exceptions.HTTPError(
            "HTTP 400 error",
            status_code=400,
            response=response,
            request_url="http://example.com"
        )
        assert exc.status_code == 400
        assert exc.response == response
        assert exc.request_url == "http://example.com"
        assert exc.details["status_code"] == 400
        assert exc.details["request_url"] == "http://example.com"
        assert "Error response body" in exc.details["response_body"]

    def test_http_error_truncates_long_response(self):
        """Test HTTPError truncates long response bodies."""
        response = Mock()
        response.text = "A" * 1000  # Long response
        exc = exceptions.HTTPError("Error", response=response)
        assert len(exc.details["response_body"]) == 500

    def test_http_error_handles_response_text_exception(self):
        """Test HTTPError handles exceptions when accessing response text."""
        response = Mock()
        response.text = Mock(side_effect=Exception("Response text error"))
        exc = exceptions.HTTPError("Error", response=response)
        # Should not raise an exception and details should not include response_body
        assert "response_body" not in exc.details

    def test_http_error_non_string_response_text(self):
        """Test HTTPError handles non-string response text."""
        response = Mock()
        response.text = 123  # Non-string
        exc = exceptions.HTTPError("Error", response=response)
        # Should handle gracefully
        assert "response_body" not in exc.details

    def test_client_error_inheritance(self):
        """Test ClientError inheritance."""
        exc = exceptions.ClientError("Client error", status_code=400)
        assert isinstance(exc, exceptions.HTTPError)
        assert isinstance(exc, exceptions.IpsdkError)
        assert exc.status_code == 400

    def test_server_error_inheritance(self):
        """Test ServerError inheritance."""
        exc = exceptions.ServerError("Server error", status_code=500)
        assert isinstance(exc, exceptions.HTTPError)
        assert isinstance(exc, exceptions.IpsdkError)
        assert exc.status_code == 500


class TestValidationError:
    """Test cases for ValidationError and related validation exceptions."""

    def test_validation_error_basic(self):
        """Test basic ValidationError initialization."""
        exc = exceptions.ValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert exc.message == "Validation failed"
        assert exc.details == {}

    def test_validation_error_with_details(self):
        """Test ValidationError with additional details."""
        details = {"field": "email", "value": "invalid-email"}
        exc = exceptions.ValidationError("Invalid email", details=details)
        assert exc.details == details
        assert isinstance(exc, exceptions.IpsdkError)

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        exc = exceptions.ValidationError("Validation issue")
        assert isinstance(exc, exceptions.IpsdkError)
        assert isinstance(exc, exceptions.ValidationError)


class TestClassifyHTTPError:
    """Test cases for HTTP error classification."""

    def test_classify_401_unauthorized(self):
        """Test classification of 401 Unauthorized."""
        exc = exceptions.classify_http_error(401)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 401
        assert "Authentication failed" in exc.message
        assert "invalid credentials or expired token" in exc.message

    def test_classify_403_forbidden(self):
        """Test classification of 403 Forbidden."""
        exc = exceptions.classify_http_error(403)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 403
        assert "Access forbidden" in exc.message
        assert "insufficient permissions" in exc.message

    def test_classify_400_client_error(self):
        """Test classification of 400 Bad Request."""
        exc = exceptions.classify_http_error(400)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 400

    def test_classify_404_client_error(self):
        """Test classification of 404 Not Found."""
        exc = exceptions.classify_http_error(404)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 404

    def test_classify_500_server_error(self):
        """Test classification of 500 Internal Server Error."""
        exc = exceptions.classify_http_error(500)
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 500

    def test_classify_503_server_error(self):
        """Test classification of 503 Service Unavailable."""
        exc = exceptions.classify_http_error(503)
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 503

    def test_classify_unknown_status_code(self):
        """Test classification of unknown status codes."""
        exc = exceptions.classify_http_error(999)
        assert isinstance(exc, exceptions.HTTPError)
        assert not isinstance(exc, (exceptions.ClientError, exceptions.ServerError))
        assert exc.status_code == 999

    def test_classify_with_response_text(self):
        """Test classification with response text."""
        response = Mock()
        response.text = "Detailed error message"
        exc = exceptions.classify_http_error(400, response=response)
        assert "Detailed error message" in exc.message

    def test_classify_with_long_response_text(self):
        """Test classification with long response text."""
        response = Mock()
        response.text = "A" * 300  # Long response
        exc = exceptions.classify_http_error(400, response=response)
        # Message should be truncated to 200 characters
        assert len(exc.message.split(": ", 1)[1]) == 200

    def test_classify_with_response_parsing_error(self):
        """Test classification when response text parsing fails."""
        response = Mock()
        response.text = Mock(side_effect=Exception("Parse error"))
        exc = exceptions.classify_http_error(400, response=response)
        # Should fall back to default message
        assert exc.message == "HTTP 400 error"


class TestClassifyHttpxError:
    """Test cases for httpx error classification."""

    def test_classify_timeout_exception(self):
        """Test classification of httpx TimeoutException."""
        httpx_exc = httpx.TimeoutException("Request timed out")
        exc = exceptions.classify_httpx_error(httpx_exc, "http://example.com")
        assert isinstance(exc, exceptions.NetworkError)
        assert "Network error" in exc.message
        assert exc.details["request_url"] == "http://example.com"
        assert exc.details["original_error"] == str(httpx_exc)

    def test_classify_connect_error(self):
        """Test classification of httpx ConnectError."""
        httpx_exc = httpx.ConnectError("Connection failed")
        exc = exceptions.classify_httpx_error(httpx_exc)
        assert isinstance(exc, exceptions.NetworkError)
        assert "Network error" in exc.message

    def test_classify_request_error(self):
        """Test classification of httpx RequestError."""
        httpx_exc = httpx.RequestError("Request failed")
        exc = exceptions.classify_httpx_error(httpx_exc)
        assert isinstance(exc, exceptions.NetworkError)
        assert "Network error" in exc.message

    def test_classify_http_status_error(self):
        """Test classification of httpx HTTPStatusError."""
        response = Mock()
        response.status_code = 404
        request = Mock()
        request.url = "http://example.com"
        httpx_exc = httpx.HTTPStatusError(
            "Not found", request=request, response=response
        )
        exc = exceptions.classify_httpx_error(httpx_exc)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 404

    def test_classify_http_status_error_url_exception(self):
        """Test HTTPStatusError when URL access raises exception."""
        response = Mock()
        response.status_code = 404
        request = Mock()
        # Configure the url property to raise an exception when accessed
        type(request).url = PropertyMock(side_effect=RuntimeError("URL error"))
        httpx_exc = httpx.HTTPStatusError(
            "Not found", request=request, response=response
        )
        exc = exceptions.classify_httpx_error(httpx_exc, "http://fallback.com")
        assert isinstance(exc, exceptions.ClientError)
        assert exc.request_url == "http://fallback.com"

    def test_classify_unknown_exception(self):
        """Test classification of unknown exceptions."""
        unknown_exc = ValueError("Unknown error")
        exc = exceptions.classify_httpx_error(unknown_exc)
        assert isinstance(exc, exceptions.IpsdkError)
        assert "Unexpected error" in exc.message


class TestClassifyHTTPErrorEdgeCases:
    """Test edge cases for classify_http_error function."""

    def test_classify_with_empty_response_text(self):
        """Test classification with empty response text."""
        exc = exceptions.classify_http_error(400, response_text="")
        assert isinstance(exc, exceptions.ClientError)
        assert exc.status_code == 400

    def test_classify_with_none_response_text(self):
        """Test classification with None response text."""
        exc = exceptions.classify_http_error(500, response_text=None)
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 500
        assert "Server error: HTTP 500" in exc.message

    def test_classify_with_request_url_only(self):
        """Test classification with request URL but no response."""
        url = "https://api.example.com/test"
        exc = exceptions.classify_http_error(404, request_url=url)
        assert isinstance(exc, exceptions.ClientError)
        assert exc.request_url == url
        assert exc.details.get("request_url") == url

    def test_classify_with_real_httpx_response(self):
        """Test classification with actual httpx Response object."""
        from unittest.mock import Mock

        import httpx

        # Create a mock response that behaves like httpx.Response
        response = Mock(spec=httpx.Response)
        response.text = "Not Found"
        response.status_code = 404

        exc = exceptions.classify_http_error(404, response=response)
        assert isinstance(exc, exceptions.ClientError)
        assert "Not Found" in exc.message

    def test_classify_boundary_status_codes(self):
        """Test classification of boundary status codes."""
        # Edge of client error range
        exc1 = exceptions.classify_http_error(399)  # Just below 4xx range
        assert isinstance(exc1, exceptions.HTTPError)
        assert not isinstance(exc1, exceptions.ClientError)

        exc2 = exceptions.classify_http_error(499)  # End of 4xx range
        assert isinstance(exc2, exceptions.ClientError)

        # Edge of server error range
        exc3 = exceptions.classify_http_error(500)  # Start of 5xx range
        assert isinstance(exc3, exceptions.ServerError)

        exc4 = exceptions.classify_http_error(599)  # End of 5xx range
        assert isinstance(exc4, exceptions.ServerError)

        exc5 = exceptions.classify_http_error(600)  # Beyond 5xx range
        assert isinstance(exc5, exceptions.HTTPError)
        assert not isinstance(exc5, exceptions.ServerError)

    def test_classify_with_both_response_text_and_response_object(self):
        """Test that response_text parameter takes precedence over response.text."""
        from unittest.mock import Mock

        response = Mock()
        response.text = "Response object text"

        # response_text should take precedence
        exc = exceptions.classify_http_error(
            400,
            response_text="Explicit response text",
            response=response
        )
        assert "Explicit response text" in exc.message
        assert "Response object text" not in exc.message

    def test_classify_with_very_long_response_text(self):
        """Test handling of extremely long response text."""
        long_text = "A" * 1000  # Much longer than MAX_RESPONSE_DISPLAY_LENGTH
        exc = exceptions.classify_http_error(400, response_text=long_text)

        # Message should be truncated for display
        message_text = exc.message.split(": ", 1)[1]
        assert len(message_text) == exceptions.MAX_RESPONSE_DISPLAY_LENGTH

        # Details should contain truncated version for storage
        assert len(exc.details["response_body"]) == exceptions.MAX_RESPONSE_BODY_LENGTH


class TestClassifyHttpxErrorEdgeCases:
    """Test edge cases for classify_httpx_error function."""

    def test_classify_with_httpx_pool_timeout(self):
        """Test classification of httpx pool timeout exceptions."""
        import httpx
        pool_timeout = httpx.PoolTimeout("Connection pool timeout")

        exc = exceptions.classify_httpx_error(pool_timeout, "https://example.com")
        assert isinstance(exc, exceptions.NetworkError)
        assert "Network error" in exc.message
        assert exc.details["request_url"] == "https://example.com"
        assert "Connection pool timeout" in exc.details["original_error"]

    def test_classify_with_httpx_read_timeout(self):
        """Test classification of httpx read timeout exceptions."""
        import httpx
        read_timeout = httpx.ReadTimeout("Read timeout")

        exc = exceptions.classify_httpx_error(read_timeout)
        assert isinstance(exc, exceptions.NetworkError)
        assert "Network error" in exc.message
        assert "Read timeout" in exc.details["original_error"]

    def test_classify_with_httpx_write_timeout(self):
        """Test classification of httpx write timeout exceptions."""
        import httpx
        write_timeout = httpx.WriteTimeout("Write timeout")

        exc = exceptions.classify_httpx_error(write_timeout)
        assert isinstance(exc, exceptions.NetworkError)
        assert "Write timeout" in exc.details["original_error"]

    def test_classify_httpx_status_error_with_no_response_text(self):
        """Test HTTPStatusError when response.text is not accessible."""
        from unittest.mock import Mock
        from unittest.mock import PropertyMock

        import httpx

        # Mock response where .text raises an exception
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        type(response).text = PropertyMock(
            side_effect=Exception("Cannot read response")
        )

        request = Mock(spec=httpx.Request)
        request.url = "https://example.com"

        http_error = httpx.HTTPStatusError(
            "Internal Server Error",
            request=request,
            response=response
        )

        exc = exceptions.classify_httpx_error(http_error)
        assert isinstance(exc, exceptions.ServerError)
        assert exc.status_code == 500

    def test_classify_httpx_status_error_with_no_request_url(self):
        """Test HTTPStatusError when request URL cannot be accessed."""
        from unittest.mock import Mock
        from unittest.mock import PropertyMock

        import httpx

        response = Mock(spec=httpx.Response)
        response.status_code = 404
        response.text = "Not Found"

        request = Mock(spec=httpx.Request)
        type(request).url = PropertyMock(side_effect=RuntimeError("URL error"))

        http_error = httpx.HTTPStatusError(
            "Not Found",
            request=request,
            response=response
        )

        exc = exceptions.classify_httpx_error(http_error, "https://fallback.com")
        assert isinstance(exc, exceptions.ClientError)
        assert exc.request_url == "https://fallback.com"

    def test_classify_custom_exception_class(self):
        """Test classification of custom exception classes."""
        class CustomNetworkError(Exception):
            pass

        custom_error = CustomNetworkError("Custom error message")
        exc = exceptions.classify_httpx_error(custom_error)

        assert isinstance(exc, exceptions.IpsdkError)
        assert "Unexpected error" in exc.message
        assert "Custom error message" in exc.details["original_error"]


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_exception_chaining(self):
        """Test proper exception chaining."""
        try:
            original_msg = "Original error"
            raise ValueError(original_msg)
        except ValueError as e:
            validation_msg = "Validation failed"
            sdk_exc = exceptions.ValidationError(validation_msg,
                                                details={"original_error": str(e)})
            assert "Original error" in sdk_exc.details["original_error"]

    def test_exception_inheritance_checking(self):
        """Test that all custom exceptions inherit from IpsdkError."""
        exception_classes = [
            exceptions.NetworkError,
            exceptions.AuthenticationError,
            exceptions.HTTPError,
            exceptions.ClientError,
            exceptions.ServerError,
            exceptions.ValidationError,
        ]

        for exc_class in exception_classes:
            exc = exc_class("Test message")
            assert isinstance(exc, exceptions.IpsdkError)


class TestConstants:
    """Test cases for module constants."""

    def test_http_status_constants(self):
        """Test HTTP status code constants are correctly defined."""
        assert exceptions.HTTP_BAD_REQUEST == 400
        assert exceptions.HTTP_UNAUTHORIZED == 401
        assert exceptions.HTTP_FORBIDDEN == 403
        assert exceptions.HTTP_INTERNAL_SERVER_ERROR == 500
        assert exceptions.HTTP_CLIENT_ERROR_MAX == 500
        assert exceptions.HTTP_SERVER_ERROR_MAX == 600

    def test_response_body_limit_constants(self):
        """Test response body limit constants are correctly defined."""
        assert exceptions.MAX_RESPONSE_BODY_LENGTH == 500
        assert exceptions.MAX_RESPONSE_DISPLAY_LENGTH == 200
        # Ensure display length is not larger than body length
        assert (
            exceptions.MAX_RESPONSE_DISPLAY_LENGTH
            <= exceptions.MAX_RESPONSE_BODY_LENGTH
        )

    def test_status_code_relationships(self):
        """Test logical relationships between status code constants."""
        # Client error max should be start of server errors
        assert exceptions.HTTP_CLIENT_ERROR_MAX == exceptions.HTTP_INTERNAL_SERVER_ERROR
        # Bad request should be less than client error max
        assert exceptions.HTTP_BAD_REQUEST < exceptions.HTTP_CLIENT_ERROR_MAX
        # Unauthorized and forbidden should be in client error range
        assert (
            exceptions.HTTP_BAD_REQUEST
            <= exceptions.HTTP_UNAUTHORIZED
            < exceptions.HTTP_CLIENT_ERROR_MAX
        )
        assert (
            exceptions.HTTP_BAD_REQUEST
            <= exceptions.HTTP_FORBIDDEN
            < exceptions.HTTP_CLIENT_ERROR_MAX
        )


class TestInternalFunctions:
    """Test cases for internal helper functions."""

    def test_detect_mock_side_effect_with_mock(self):
        """Test _detect_mock_side_effect detects Mock objects with side effects."""
        from unittest.mock import Mock

        import pytest
        mock_obj = Mock(side_effect=Exception("test"))

        with pytest.raises(exceptions._MockDetectionError) as exc_info:
            exceptions._detect_mock_side_effect(mock_obj)

        assert "Mock side_effect detected" in str(exc_info.value)

    def test_detect_mock_side_effect_with_mock_no_side_effect(self):
        """Test _detect_mock_side_effect ignores Mock objects without side effects."""
        from unittest.mock import Mock
        mock_obj = Mock()
        # Explicitly set side_effect to None to ensure it's not set
        mock_obj.side_effect = None

        # Should not raise an exception
        exceptions._detect_mock_side_effect(mock_obj)

    def test_detect_mock_side_effect_with_regular_string(self):
        """Test _detect_mock_side_effect ignores regular strings."""
        regular_string = "This is just a regular string"

        # Should not raise an exception
        exceptions._detect_mock_side_effect(regular_string)

    def test_detect_mock_side_effect_with_mock_like_string(self):
        """Test _detect_mock_side_effect handles strings containing 'Mock'."""
        mock_like_string = "This string contains Mock but is not a Mock object"

        # Should not raise an exception because it doesn't have side_effect attribute
        exceptions._detect_mock_side_effect(mock_like_string)


class TestComprehensiveErrorHandling:
    """Test comprehensive error handling scenarios."""

    def test_exception_with_none_details(self):
        """Test exception initialization with explicitly None details."""
        exc = exceptions.IpsdkError("Test error", details=None)
        assert exc.details == {}
        assert isinstance(exc.details, dict)

    def test_exception_details_immutability(self):
        """Test that modifying details after creation doesn't affect original."""
        original_details = {"key": "value"}
        exc = exceptions.IpsdkError("Test error", details=original_details)

        # Modify the exception's details
        exc.details["new_key"] = "new_value"

        # Original dict should not be modified (details are copied in __init__)
        assert "new_key" not in original_details
        assert exc.details["new_key"] == "new_value"

    def test_http_error_with_complex_details(self):
        """Test HTTPError with complex details structure."""
        complex_details = {
            "request_id": "req_12345",
            "retry_count": 3,
            "headers": {"Content-Type": "application/json"},
            "nested": {"inner": "value"}
        }

        exc = exceptions.HTTPError(
            "Complex HTTP error",
            status_code=422,
            request_url="https://api.example.com",
            details=complex_details
        )

        assert exc.details["request_id"] == "req_12345"
        assert exc.details["retry_count"] == 3
        assert exc.details["nested"]["inner"] == "value"
        assert exc.details["status_code"] == 422
        assert exc.details["request_url"] == "https://api.example.com"

    def test_http_error_response_text_handling(self):
        """Test HTTPError response text extraction and truncation."""
        from unittest.mock import Mock

        # Test with response that has accessible text
        response = Mock()
        response.text = "Detailed server error message"

        exc = exceptions.HTTPError(
            "HTTP error",
            status_code=500,
            response=response
        )

        assert exc.details["response_body"] == "Detailed server error message"

    def test_http_error_response_text_exception_handling(self):
        """Test HTTPError when response.text raises an exception."""
        from unittest.mock import Mock
        from unittest.mock import PropertyMock

        response = Mock()
        type(response).text = PropertyMock(side_effect=UnicodeDecodeError(
            "utf-8", b"", 0, 1, "test error"
        ))

        # Should not raise an exception, should handle gracefully
        exc = exceptions.HTTPError(
            "HTTP error",
            status_code=400,
            response=response
        )

        assert exc.status_code == 400
        assert (
            "response_body" not in exc.details
            or exc.details["response_body"] is None
        )

    def test_network_error_with_connection_details(self):
        """Test NetworkError with network-specific details."""
        details = {
            "host": "api.example.com",
            "port": 443,
            "protocol": "https",
            "timeout": 30.0,
            "dns_resolution_time": 0.123
        }

        exc = exceptions.NetworkError("Connection timeout", details=details)

        assert exc.details["host"] == "api.example.com"
        assert exc.details["port"] == 443
        assert exc.details["timeout"] == 30.0
        assert isinstance(exc.details["dns_resolution_time"], float)

    def test_authentication_error_with_auth_context(self):
        """Test AuthenticationError with authentication context."""
        details = {
            "auth_method": "oauth2",
            "client_id": "app_123",
            "scope": ["read", "write"],
            "token_expiry": "2025-12-31T23:59:59Z",
            "refresh_available": True
        }

        exc = exceptions.AuthenticationError("Token expired", details=details)

        assert exc.details["auth_method"] == "oauth2"
        assert exc.details["scope"] == ["read", "write"]
        assert exc.details["refresh_available"] is True

    def test_validation_error_with_field_details(self):
        """Test ValidationError with field validation context."""
        details = {
            "field_name": "email",
            "field_value": "invalid-email",
            "expected_format": "email",
            "validation_rules": ["required", "email_format"],
            "error_code": "INVALID_EMAIL_FORMAT"
        }

        exc = exceptions.ValidationError("Email validation failed", details=details)

        assert exc.details["field_name"] == "email"
        assert exc.details["field_value"] == "invalid-email"
        assert "required" in exc.details["validation_rules"]

    def test_exception_str_with_long_details(self):
        """Test string representation with very long details."""
        long_details = {
            "long_string": "A" * 1000,
            "long_list": list(range(100)),
            "nested": {
                "deep": {
                    "very_deep": "value"
                }
            }
        }

        exc = exceptions.IpsdkError("Test with long details", details=long_details)
        str_repr = str(exc)

        # Should include the message and details
        assert "Test with long details" in str_repr
        assert "Details:" in str_repr

    def test_exception_inheritance_chain(self):
        """Test proper inheritance chain for all exception types."""
        # Test each exception type inherits properly
        exc_hierarchy = [
            (exceptions.IpsdkError, Exception),
            (exceptions.NetworkError, exceptions.IpsdkError),
            (exceptions.AuthenticationError, exceptions.IpsdkError),
            (exceptions.HTTPError, exceptions.IpsdkError),
            (exceptions.ClientError, exceptions.HTTPError),
            (exceptions.ServerError, exceptions.HTTPError),
            (exceptions.ValidationError, exceptions.IpsdkError)
        ]

        for child_class, parent_class in exc_hierarchy:
            assert issubclass(child_class, parent_class)

            # Test instance relationships
            instance = child_class("test")
            assert isinstance(instance, parent_class)
            assert isinstance(instance, Exception)

    def test_concurrent_exception_creation(self):
        """Test thread safety of exception creation."""
        import threading
        import time

        results = []
        exceptions_created = []

        def create_exceptions():
            for i in range(10):
                exc = exceptions.NetworkError(
                    f"Error {threading.current_thread().name}-{i}",
                    details={"thread": threading.current_thread().name, "count": i}
                )
                exceptions_created.append(exc)
                time.sleep(0.001)  # Small delay
            results.append("done")

        # Create multiple threads creating exceptions
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_exceptions, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all threads completed
        assert len(results) == 3
        assert len(exceptions_created) == 30  # 3 threads * 10 exceptions each

        # Verify each exception has correct details
        for exc in exceptions_created:
            assert "thread" in exc.details
            assert "count" in exc.details
            assert exc.details["thread"] in ["Thread-0", "Thread-1", "Thread-2"]
            assert 0 <= exc.details["count"] <= 9


class TestSimplifiedAPICompatibility:
    """Test that the simplified API maintains essential compatibility."""

    def test_simplified_network_error_usage(self):
        """Test simplified NetworkError covers all network scenarios."""
        # Connection failure
        exc1 = exceptions.NetworkError("Connection failed",
                                     details={"host": "example.com"})
        assert exc1.details["host"] == "example.com"

        # Timeout
        exc2 = exceptions.NetworkError("Request timeout",
                                     details={"timeout": 30.0})
        assert exc2.details["timeout"] == 30.0

    def test_simplified_auth_error_usage(self):
        """Test simplified AuthenticationError covers all auth scenarios."""
        # Invalid credentials
        exc1 = exceptions.AuthenticationError("Invalid credentials",
                                            details={"auth_type": "basic"})
        assert exc1.details["auth_type"] == "basic"

        # Expired token
        exc2 = exceptions.AuthenticationError("Token expired",
                                            details={"auth_type": "oauth"})
        assert exc2.details["auth_type"] == "oauth"

    def test_simplified_validation_error_usage(self):
        """Test simplified ValidationError covers all validation scenarios."""
        # JSON parsing error
        exc1 = exceptions.ValidationError("Invalid JSON",
                                        details={"error_type": "json_parse"})
        assert exc1.details["error_type"] == "json_parse"

        # Field validation error
        exc2 = exceptions.ValidationError("Invalid email",
                                        details={"field": "email", "value": "invalid"})
        assert exc2.details["field"] == "email"
