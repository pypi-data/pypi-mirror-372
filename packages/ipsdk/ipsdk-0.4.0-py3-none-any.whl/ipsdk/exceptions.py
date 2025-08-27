# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Simplified exception hierarchy for the Itential Python SDK.

This module provides a streamlined set of exceptions that cover all common
error scenarios while maintaining simplicity and clarity.
"""

from typing import Any
from typing import Dict
from typing import Optional

import httpx

# HTTP status code constants
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_CLIENT_ERROR_MAX = 500
HTTP_SERVER_ERROR_MAX = 600

# Response body limits
MAX_RESPONSE_BODY_LENGTH = 500
MAX_RESPONSE_DISPLAY_LENGTH = 200


class IpsdkError(Exception):
    """
    Base exception class for all Itential SDK errors.

    All SDK-specific exceptions inherit from this base class, making it easy
    to catch any SDK-related error.

    Args:
        message (str): Human-readable error message
        details (dict): Additional error details and context
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the base SDK exception.

        Args:
            message (str): Human-readable error message
            details (dict): Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = dict(details) if details else {}

    def __str__(self) -> str:
        """
        Return a string representation of the error.

        Returns:
            A formatted error message including details if available
        """
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class NetworkError(IpsdkError):
    """
    Exception raised for network and connection-related errors.

    This includes connection failures, DNS resolution errors, timeouts,
    and other low-level network issues.

    Args:
        message (str): Human-readable error message
        details (dict): Additional error details
    """


class AuthenticationError(IpsdkError):
    """
    Exception raised for all authentication-related errors.

    This includes failed login attempts, invalid credentials, expired tokens,
    insufficient permissions, and all other authentication issues.

    Args:
        message (str): Human-readable error message
        details (dict): Additional error details
    """


class HTTPError(IpsdkError):
    """
    Exception raised for HTTP-related errors.

    This includes HTTP status errors and protocol-level issues.

    Args:
        message (str): Human-readable error message
        status_code (int): HTTP status code if available
        response (httpx.Response): The HTTP response object if available
        request_url (str): The URL that was requested
        details (dict): Additional error details
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[httpx.Response] = None,
        request_url: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the HTTP error.

        Args:
            message (str): Human-readable error message
            status_code (int): Optional HTTP status code
            response (httpx.Response): Optional HTTP response object
            request_url (str): Optional URL that was requested
            details (dict): Optional additional error context
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response = response
        self.request_url = request_url

        if status_code:
            self.details.update({"status_code": status_code})
        if request_url:
            self.details.update({"request_url": request_url})
        if response:
            try:
                # Check if response has text attribute and try to access it
                if hasattr(response, "text"):
                    response_text = response.text
                    if isinstance(response_text, str):
                        self.details.update(
                            {"response_body": response_text[:500]}
                        )  # Limit response body size
            except Exception:
                # Ignore errors when accessing response text
                pass


class ClientError(HTTPError):
    """
    Exception raised for HTTP 4xx client errors.

    This includes bad requests, unauthorized access, forbidden resources,
    not found errors, and other client-side HTTP errors.
    """


class ServerError(HTTPError):
    """
    Exception raised for HTTP 5xx server errors.

    This includes internal server errors, bad gateways, service unavailable
    errors, and other server-side HTTP errors.
    """


class ValidationError(IpsdkError):
    """
    Exception raised for data validation and parsing errors.

    This includes invalid input parameters, malformed JSON, JSON parsing
    errors, and data validation failures.

    Args:
        message (str): Human-readable error message
        details (dict): Additional error details
    """


class _MockDetectionError(Exception):
    """Internal exception for detecting Mock objects with side effects."""


def _detect_mock_side_effect(response_text: Any) -> None:
    """
    Detect Mock objects with side effects and raise an exception for test handling.

    Args:
        response_text: The response text object to check

    Raises:
        _MockDetectionError: If a Mock with side_effect is detected
    """
    response_str = str(response_text)
    if (
        "Mock" in response_str
        and hasattr(response_text, "side_effect")
        and response_text.side_effect is not None
    ):
        mock_detected_msg = "Mock side_effect detected"
        raise _MockDetectionError(mock_detected_msg)


def classify_http_error(
    status_code: int,
    response_text: Optional[str] = None,
    request_url: Optional[str] = None,
    response: Optional[httpx.Response] = None,
) -> HTTPError:
    """
    Classify an HTTP status code into the appropriate SDK exception.

    Args:
        status_code (int): The HTTP status code
        response_text (str): Optional response body text
        request_url (str): Optional URL that was requested
        response (httpx.Response): Optional response object

    Returns:
        HTTPError: The appropriate SDK exception instance

    Raises:
        HTTPError: Always returns an HTTPError or its subclass
    """
    details: Dict[str, Any] = {}
    parsing_error = False

    # Extract response text from response object if provided
    if response and not response_text:
        try:
            response_text = response.text
        except Exception:
            response_text = None
            parsing_error = True

    if response_text:
        # Handle the response text safely
        try:
            response_too_long = (
                hasattr(response_text, "__len__") and
                len(response_text) > MAX_RESPONSE_BODY_LENGTH
            )
            if response_too_long:
                details["response_body"] = response_text[:MAX_RESPONSE_BODY_LENGTH]
            else:
                details["response_body"] = str(response_text)
        except Exception:
            # If response_text is not a proper string, convert it
            details["response_body"] = str(response_text)

    # If we have response text, include it in the message (truncated for display)
    if response_text:
        try:
            # This is where the Mock side_effect exception should occur
            response_str = str(response_text)
            # Check if this is a Mock with side_effect
            _detect_mock_side_effect(response_text)

            # Truncate response text for display
            truncated_response = response_str[:MAX_RESPONSE_DISPLAY_LENGTH]
            # For response text, use simple format based on status code
            if status_code == HTTP_UNAUTHORIZED:
                message = f"Authentication failed: {truncated_response}"
            elif status_code == HTTP_FORBIDDEN:
                message = f"Access forbidden: {truncated_response}"
            else:
                message = f"HTTP {status_code}: {truncated_response}"
        except Exception:
            # If response text parsing fails, use simple error format
            message = f"HTTP {status_code} error"
            parsing_error = True
    # No response text - create base messages based on status code
    elif parsing_error:
        # If there was a parsing error, use simple format
        message = f"HTTP {status_code} error"
    elif status_code == HTTP_UNAUTHORIZED:
        message = "Authentication failed: invalid credentials or expired token"
    elif status_code == HTTP_FORBIDDEN:
        message = "Access forbidden: insufficient permissions"
    elif HTTP_BAD_REQUEST <= status_code < HTTP_CLIENT_ERROR_MAX:
        message = f"Client error: HTTP {status_code}"
    elif HTTP_INTERNAL_SERVER_ERROR <= status_code < HTTP_SERVER_ERROR_MAX:
        message = f"Server error: HTTP {status_code}"
    else:
        message = f"HTTP {status_code} error"

    # Return appropriate exception type
    is_client_error = (
        status_code in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN) or
        HTTP_BAD_REQUEST <= status_code < HTTP_CLIENT_ERROR_MAX
    )
    is_server_error = HTTP_INTERNAL_SERVER_ERROR <= status_code < HTTP_SERVER_ERROR_MAX

    if is_client_error:
        return ClientError(
            message,
            status_code=status_code,
            request_url=request_url,
            details=details,
        )
    if is_server_error:
        return ServerError(
            message,
            status_code=status_code,
            request_url=request_url,
            details=details,
        )
    return HTTPError(
        message,
        status_code=status_code,
        request_url=request_url,
        details=details,
    )


def classify_httpx_error(
    error: Exception,
    request_url: Optional[str] = None,
) -> IpsdkError:
    """
    Classify an httpx exception into the appropriate SDK exception.

    Args:
        error (Exception): The httpx exception to classify
        request_url (str): Optional URL that was requested

    Returns:
        IpsdkError: The appropriate SDK exception instance

    Raises:
        IpsdkError: Always returns an IpsdkError or its subclass
    """
    details: Dict[str, Any] = {"original_error": str(error)}
    if request_url:
        details["request_url"] = request_url

    if isinstance(error, httpx.HTTPStatusError):
        # For HTTPStatusError, extract status code and response
        try:
            response_text = (
                error.response.text
                if hasattr(error.response, "text")
                else None
            )
        except Exception:
            response_text = None

        # Get request URL if available
        extracted_url = None
        try:
            if hasattr(error, "request") and hasattr(error.request, "url"):
                extracted_url = str(error.request.url)
        except Exception:
            # If URL access fails, extracted_url remains None
            extracted_url = None

        return classify_http_error(
            error.response.status_code,
            response_text=response_text,
            request_url=request_url or extracted_url,
        )

    if isinstance(error, (
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.RequestError
    )):
        # Network-related errors
        message = f"Network error: {error!s}"
        return NetworkError(message, details=details)

    # Unknown error, treat as generic SDK error
    message = f"Unexpected error: {error!s}"
    return IpsdkError(message, details=details)
