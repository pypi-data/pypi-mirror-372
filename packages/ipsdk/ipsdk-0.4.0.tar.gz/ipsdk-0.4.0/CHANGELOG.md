# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-08-26

### Added
- GitHub Dependabot configuration (#49)
- Python version matrix testing support (#44)

### Changed
- Update Dependabot configuration (#53)
- Enhance development environment and code quality tools (#47)
- Enhance exceptions module test coverage to 97% (#46)
- Expand jsonutils test coverage to 100% (#45)

### Fixed
- Fix unit tests and enhance exception handling (#52)

### Dependencies
- ci(deps): bump actions/checkout from 4 to 5 (#51)
- ci(deps): bump astral-sh/setup-uv from 5 to 6 (#50)

## [0.3.0] - 2025-08-12

### Added
- New developer guide to docs (#41)
- File logging support (#39)
- Logger stdlib level wrappers (#37)
- Comprehensive type hints throughout the app (#34)
- Request and response wrapper classes (#32)
- Centralized exceptions (#31)

### Changed
- Updated README file (#36)
- Updated logging functionality (#35)
- Updated unit test cases (#33)
- Refactored project structure (#30)

### Fixed
- Typos in all docstrings (#40)

### Removed
- Automatic status check (#29)

## [0.2.0] - 2025-05-22

### Added
- Support for setting request timeout (#26)

## [0.1.1] - 2025-05-12

### Fixed
- Async connection errors with "unexpected keyword argument" error (#24)

## [0.1.0] - 2025-05-07

### Added
- Examples and documentation in README (#14)
- Async support with httpx refactoring (#13)
- Comprehensive logging functionality (#12)
- Support for generating querystrings (#6)
- Initial release of Itential Python SDK
- Factory functions for Platform and Gateway connections
- Support for both synchronous and asynchronous HTTP clients
- OAuth and basic authentication support
- Automatic authentication on first API call

### Changed
- Updated email in pyproject.toml (#20)
- Updated method arguments and documentation (#18)
- Updated project dependencies (#16)
- Refactored library to use factory functions (#9)
- Migrated from requests to httpx library (#7)
- Updated base API path for gateway (#5)
- Updated precedence of values for cloud and gateway (#3)

### Fixed
- Missing setuptools_scm dev dependencies (#22)
- Missing quote in Makefile (#19)
- Data transformation to JSON string (#17)
- Pre-merge pipeline issues (#11)
- Body payload not setting headers properly (#8)

### Added (Dev/Build)
- Missing build package to dev dependencies (#21)
- Release workflow (#15)
- Test cases (#10)
- Community code of conduct (#4)
- Pre-merge pipeline workflow
