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



