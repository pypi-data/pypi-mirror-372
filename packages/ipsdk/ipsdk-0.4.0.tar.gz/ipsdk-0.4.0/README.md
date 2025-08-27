# ipsdk

The Itential Python SDK provides a client implementation in Python for writing
scripts that can make API calls to Itential Platform or Itential Automation
Gateway 4.x.

## Features

- Easy API requests with automatic authentication
- Support for OAuth and user/password login
- Customizable connection settings
- Centralized logging configuration

## Getting started

## Requirements

- Python 3.8 or higher
- httpx >= 0.28.1

### Tested Python Versions

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.10           | ✅ Tested | Minimum recommended version |
| 3.11           | ✅ Tested | Full support |
| 3.12           | ✅ Tested | Full support |
| 3.13           | ✅ Tested | Latest stable release |
| 3.14           | 🔄 Beta | Development/preview testing |

The SDK is automatically tested against Python 3.10-3.13 in our CI pipeline to ensure compatibility across all supported versions.

## Installation

Install `ipsdk` using pip:

```bash
$ pip install ipsdk
```

Or using uv (recommended for development):

```bash
$ uv add ipsdk
```

The `ipsdk` package provides factory functions for connecting to either
Itential Platform or Itential Automation Gateway.

The `platform_factory(...)` function creates a connection to Itential Platform
The `gateway_factory(...)` function creates a connection to Itential Automation Gateway

Use one of the factory functions to create a new connection to the server
and send requests.

```python
>>> import ipsdk
>>> platform = ipsdk.platform_factory(host="platform.itential.dev", user="admin@pronghorn")
>>> res = platform.get("/health/server")
>>> res
<Response [200 OK]>
>>> res.text
'{"version":"15.8.10-2023.2.44","release":"2023.2.9"...`
```

The above works the same for Itential Automation Gateway, simply use
`gateway_factory` instead of `platform_factory` to connect to Itential
Automation Gateway.

Itential Python SDK also supports using `asyncio` to connect to servers as
well. The example below demonstrates how to connect to the server using an
async connection.

```python
import asyncio
import ipsdk

async def main():
    p = ipsdk.platform_factory(
        host="platform.itential.dev",
        user="admin@pronghorn",
        want_async=True
    )

    res = await p.get("/adapters")

if __name__ == "__main__":
    asyncio.run(main())
```

The connection object supports the following HTTP methods:

- `GET` - Sends a HTTP GET request to the server and returns the results
- `POST` - Sends a HTTP POST request to the server and returns the results
- `PUT` - Sends a HTTP PUT request to the server and returns the results
- `DELETE` - Sends a HTTP DELETE request to the server and returns the results
- `PATCH` - Sends a HTTP PATCH request to the server and returns the results

The following table shows the keyword arguments for each HTTP method:

 | Keyword  | `GET`         | `POST`   | `PUT`    | `DELETE`      | `PATCH`  |
 |----------|---------------|----------|----------|---------------|----------|
 | `path`   | Required      | Required | Required | Required      | Required |
 | `params` | Optional      | Optional | Optional | Optional      | Optional |
 | `json`   | Not Supported | Optional | Optional | Not Supported | Optional |

The `path` argument specifies the relative path of the URI.   This value is
prepended to the base URL.  The base URL for Itential Platform is `<host>` and
the base URL for Itential Automation Gateway is `<host>/api/v2.0`.

The `params` argument accepts a `dict` object that is transformed into the URL
query string.  For example, if `params={"foo": "bar"}` the resulting query
string would be `?foo=bar`

The `json` argument accepts the payload to send in the request as JSON. This
argument accepts either a `list` or `dict` object. When specified, the data
will automatically be converted to a JSON string and the `Content-Type` and
`Accept` headers will be set to `application/json`.

## Configuration

Both the `platform_factory` and `gateway_factory` functions support
configuration using keyword arguments. The table below shows the keyword
arguments for each function along with their default value.

 | Keyword         | `platform_factory` | `gateway_factory` |
 |-----------------|--------------------|-------------------|
 | `host`          | `localhost`        | `localhost`       |
 | `port`          | `0`                | `0`               |
 | `use_tls`       | `True`             | `True`            |
 | `verify`        | `True`             | `True`            |
 | `user`          | `admin`            | `admin@itential`  |
 | `password`      | `admin`            | `admin`           |
 | `client_id`     | `None`             | Not Supported     |
 | `client_secret` | `None`             | Not Supported     |
 | `timeout`       | `30`               | `30`              |
 | `want_async`    | `False`            | `False`           |

## Development

For development setup, testing, and contribution guidelines, see the [Development Guide](docs/development.md).


## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
