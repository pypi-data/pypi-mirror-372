# Development Guide

This project uses `uv` as the Python package manager and build tool. Here are the key development commands:

## Setup

```bash
# Install dependencies and create virtual environment
$ uv sync
```

## Testing

```bash
# Run tests
$ uv run pytest tests
$ make test

# Run tests with coverage
$ uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/
$ make coverage
```

## Code Quality

```bash
# Lint code
$ uv run ruff check src/ipsdk
$ uv run ruff check tests
$ make lint

# Type checking
$ uv run mypy src/ipsdk
```

## Build and Maintenance

```bash
# Clean build artifacts
$ make clean

# Run premerge checks (clean, lint, and test)
$ make premerge
```

## Development Workflow

1. **Setup**: Run `uv sync` to install dependencies and create a virtual environment
2. **Development**: Make your changes to the codebase
3. **Testing**: Run tests with `make test` or `uv run pytest tests`
4. **Quality Checks**: Run `make lint` to check code quality
5. **Pre-merge**: Run `make premerge` before submitting changes

## Additional Tools

The project uses the following development tools:

- **uv**: Package manager and virtual environment management
- **pytest**: Testing framework with async support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **coverage**: Code coverage reporting

All tools are configured in `pyproject.toml` and can be run through `uv` or the provided Makefile targets.

## Logging

By default all logging is turned off for `ipsdk`. To enable logging to
`stdout`, use the `ipsdk.logger.set_level` function.

The SDK provides logging level constants that you can use instead of importing the standard library logging module:

```python
>>> import ipsdk

# Using ipsdk logging constants (recommended)
>>> ipsdk.logger.set_level(ipsdk.logger.DEBUG)
```

### Available Logging Levels

The SDK provides the following logging level constants:

- `ipsdk.logger.NOTSET` - No logging threshold (0)
- `ipsdk.logger.DEBUG` - Debug messages (10)
- `ipsdk.logger.INFO` - Informational messages (20)
- `ipsdk.logger.WARNING` - Warning messages (30)
- `ipsdk.logger.ERROR` - Error messages (40)
- `ipsdk.logger.CRITICAL` - Critical error messages (50)
- `ipsdk.logger.FATAL` - Fatal error messages (90)

### File Logging

The SDK supports optional file logging in addition to console logging. You can configure file logging using several approaches:

#### Quick Setup with `configure_file_logging`

The easiest way to enable both console and file logging:

```python
>>> import ipsdk

# Enable both console and file logging
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", level=ipsdk.logger.DEBUG)

# With propagation to httpx/httpcore loggers
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", level=ipsdk.logger.INFO, propagate=True)
```

#### Manual File Handler Management

For more control, you can add and remove file handlers manually:

```python
>>> import ipsdk

# First set the console logging level
>>> ipsdk.logger.set_level(ipsdk.logger.INFO)

# Add a file handler
>>> ipsdk.logger.add_file_handler("/path/to/app.log")

# Add multiple file handlers with different levels
>>> ipsdk.logger.add_file_handler("/path/to/debug.log", level=ipsdk.logger.DEBUG)
>>> ipsdk.logger.add_file_handler("/path/to/errors.log", level=ipsdk.logger.ERROR)

# Remove all file handlers when done
>>> ipsdk.logger.remove_file_handlers()
```

#### Custom Log Formatting

You can specify custom format strings for file handlers:

```python
>>> custom_format = "%(asctime)s [%(levelname)s] %(message)s"
>>> ipsdk.logger.add_file_handler("/path/to/app.log", format_string=custom_format)

# Or with configure_file_logging
>>> ipsdk.logger.configure_file_logging("/path/to/app.log", format_string=custom_format)
```

**Note:** File logging automatically creates parent directories if they don't exist.