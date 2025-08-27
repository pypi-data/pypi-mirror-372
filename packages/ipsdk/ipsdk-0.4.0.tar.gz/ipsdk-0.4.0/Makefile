# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

.DEFAULT_GOAL := help

.PHONY: test coverage clean lint format ruff-fix security

# The help target displays a help message that includes the avialable targets
# in this `Makefile`.  It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  clean      - Cleans the development environment"
	@echo "  coverage   - Run test coverage report"
	@echo "  format     - Format source files with ruff"
	@echo "  lint       - Run analysis on source files"
	@echo "  premerge   - Run the permerge tests locallly"
	@echo "  ruff-fix   - Run ruff with --fix to auto-fix issues"
	@echo "  security   - Run security analysis using bandit"
	@echo "  test       - Run test suite"
	@echo ""

# The test target will invoke the unit tests using pytest.   This target
# requires uv to be installed and the environment created.
test:
	uv run pytest tests

# The coverage target will invoke pytest with coverage support.  It will
# display a summary of the unit test coverage as well as output the coverage
# data report
coverage:
	uv run pytest --cov=src/ipsdk --cov-report=term --cov-report=html tests/

# The lint target invokes ruff to run the linter against both the library
# and test code.   This target is invoked in the premerge pipeline.
lint:
	uv run ruff check src/ipsdk
	uv run ruff check tests

# The security target invokes bandit to run security analysis on the 
# source code.  It scans for common security vulnerabilities.
security:
	uv run bandit -r src/ipsdk --configfile pyproject.toml

# The clean target will remove build and dev artififacts that are not 
# part of the application and get created by other targets.
clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# The format target will format source files using ruff
format:
	uv run ruff format src/ipsdk tests

# The ruff-fix target will run ruff with --fix to automatically fix
# fixable issues in the source code
ruff-fix:
	uv run ruff check --fix src/ipsdk
	uv run ruff check --fix tests

# The premerge target will run the permerge tests locally.  This is
# the same target that is invoked in the permerge pipeline.
premerge: clean lint security test
