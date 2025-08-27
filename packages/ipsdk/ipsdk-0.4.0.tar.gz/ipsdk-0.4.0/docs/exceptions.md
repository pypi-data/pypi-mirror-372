# Exception Hierarchy

This document explains the exception hierarchy used in the Itential Python SDK (ipsdk) and provides guidance on when each exception type is used.

## Exception Hierarchy Diagram

```
Exception (Python built-in)
└── IpsdkError (Base SDK exception)
    ├── NetworkError (Network/connection issues)
    ├── AuthenticationError (Authentication failures)
    ├── ValidationError (Data validation errors)
    └── HTTPError (HTTP protocol errors)
        ├── ClientError (HTTP 4xx errors)
        └── ServerError (HTTP 5xx errors)
```

## Exception Classes

### IpsdkError

**Base class:** `Exception`  
**Module:** `src/ipsdk/exceptions.py:30`

The root exception class for all Itential SDK errors. All SDK-specific exceptions inherit from this base class, making it easy to catch any SDK-related error with a single except clause.

**Attributes:**
- `message` (str): Human-readable error message
- `details` (dict): Additional error details and context

**Usage:**
```python
try:
    # SDK operations
    pass
except IpsdkError as e:
    print(f"SDK Error: {e.message}")
    print(f"Details: {e.details}")
```

### NetworkError

**Base class:** `IpsdkError`  
**Module:** `src/ipsdk/exceptions.py:66`

Exception raised for network and connection-related errors. This includes:
- Connection failures
- DNS resolution errors  
- Timeouts
- Other low-level network issues

**Common scenarios:**
- Server is unreachable
- Network connectivity issues
- DNS resolution failures
- Connection timeouts

### AuthenticationError

**Base class:** `IpsdkError`  
**Module:** `src/ipsdk/exceptions.py:79`

Exception raised for all authentication-related errors. This includes:
- Failed login attempts
- Invalid credentials
- Expired tokens
- Insufficient permissions
- All other authentication issues

**Common scenarios:**
- Invalid username/password
- OAuth token expiration
- Missing authentication headers
- Insufficient access rights

### ValidationError

**Base class:** `IpsdkError`  
**Module:** `src/ipsdk/exceptions.py:165`

Exception raised for data validation and parsing errors. This includes:
- Invalid input parameters
- Malformed JSON
- JSON parsing errors
- Data validation failures

**Common scenarios:**
- Invalid request payload format
- Missing required fields
- Type conversion errors
- JSON deserialization failures

### HTTPError

**Base class:** `IpsdkError`  
**Module:** `src/ipsdk/exceptions.py:92`

Exception raised for HTTP-related errors and protocol-level issues.

**Additional attributes:**
- `status_code` (int): HTTP status code if available
- `response` (httpx.Response): HTTP response object if available  
- `request_url` (str): URL that was requested

**Usage:**
```python
try:
    # HTTP request
    pass
except HTTPError as e:
    print(f"HTTP Error {e.status_code}: {e.message}")
    print(f"URL: {e.request_url}")
```

### ClientError

**Base class:** `HTTPError`  
**Module:** `src/ipsdk/exceptions.py:147`

Exception raised for HTTP 4xx client errors. This includes:
- Bad requests (400)
- Unauthorized access (401)
- Forbidden resources (403)
- Not found errors (404)
- Other client-side HTTP errors

**Common scenarios:**
- Malformed request syntax
- Authentication required
- Access denied
- Resource not found
- Method not allowed

### ServerError

**Base class:** `HTTPError`  
**Module:** `src/ipsdk/exceptions.py:156`

Exception raised for HTTP 5xx server errors. This includes:
- Internal server errors (500)
- Bad gateways (502)
- Service unavailable (503)
- Gateway timeouts (504)
- Other server-side HTTP errors

**Common scenarios:**
- Server crashes
- Database connection failures
- Service overload
- Maintenance mode

## Helper Functions

### classify_http_error()

**Module:** `src/ipsdk/exceptions.py:202`

Classifies an HTTP status code into the appropriate SDK exception.

**Parameters:**
- `status_code` (int): HTTP status code
- `response_text` (str, optional): Response body text
- `request_url` (str, optional): URL that was requested
- `response` (httpx.Response, optional): Response object

**Returns:** Appropriate `HTTPError` subclass instance

### classify_httpx_error()

**Module:** `src/ipsdk/exceptions.py:314`

Classifies an httpx exception into the appropriate SDK exception.

**Parameters:**
- `error` (Exception): The httpx exception to classify
- `request_url` (str, optional): URL that was requested

**Returns:** Appropriate `IpsdkError` subclass instance

## Error Handling Best Practices

### Specific Exception Handling

```python
from ipsdk.exceptions import NetworkError, AuthenticationError, ClientError

try:
    # SDK operations
    response = client.get("/api/resource")
except NetworkError as e:
    # Handle network issues - maybe retry
    logger.error(f"Network error: {e}")
except AuthenticationError as e:
    # Handle auth issues - maybe refresh token
    logger.error(f"Authentication failed: {e}")
except ClientError as e:
    # Handle client errors - maybe fix request
    if e.status_code == 404:
        logger.error("Resource not found")
    else:
        logger.error(f"Client error: {e}")
```

### General Exception Handling

```python
from ipsdk.exceptions import IpsdkError

try:
    # SDK operations
    response = client.get("/api/resource")
except IpsdkError as e:
    # Catch all SDK errors
    logger.error(f"SDK error: {e.message}")
    if e.details:
        logger.debug(f"Error details: {e.details}")
```

### Exception Information Access

All exceptions provide:
- `message`: Human-readable error description
- `details`: Dictionary with additional context
- `__str__()`: Formatted string including details

HTTP-related exceptions also provide:
- `status_code`: HTTP status code
- `response`: Original response object (if available)
- `request_url`: URL that generated the error

## Constants

The following HTTP status constants are defined for reference:

- `HTTP_BAD_REQUEST = 400`
- `HTTP_UNAUTHORIZED = 401` 
- `HTTP_FORBIDDEN = 403`
- `HTTP_INTERNAL_SERVER_ERROR = 500`
- `HTTP_CLIENT_ERROR_MAX = 500`
- `HTTP_SERVER_ERROR_MAX = 600`

Response body handling limits:
- `MAX_RESPONSE_BODY_LENGTH = 500` (stored in details)
- `MAX_RESPONSE_DISPLAY_LENGTH = 200` (shown in messages)