install:
	uv sync

run:
	uv run python -m grahamcraft.main

server:
	uv run python -m grahamcraft.start_server
	# Alternative: uv run python -m grahamcraft.server

# Install in development mode
dev-install:
	uv sync
	uv pip install -e .

# Run using entry points (after dev-install)
run-entry:
	uv run grahamcraft

server-entry:
	uv run grahamcraft-server

# Development and Testing
test-install:
	uv sync --extra test

dev-full-install:
	uv sync --extra dev

# Testing
test:
	uv sync --extra test
	uv run pytest

test-verbose:
	uv sync --extra test
	uv run pytest -v

test-coverage:
	uv sync --extra test
	uv run pytest --cov=src/grahamcraft --cov-report=html --cov-report=term

test-unit:
	uv sync --extra test
	uv run pytest -m "unit" -v

test-integration:
	uv sync --extra test
	uv run pytest -m "integration" -v

test-fast:
	uv sync --extra test
	uv run pytest -m "not slow" -v

# Code Quality
lint:
	uv run pyright src

format:
	uv run black src tests
	uv run isort src tests

format-check:
	uv run black --check src tests
	uv run isort --check-only src tests

type-check:
	uv run mypy src

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development workflow
check: format-check lint type-check test

fix: format lint



