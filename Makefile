install:
	uv sync

run:
	uv run python main.py

server:
	uv run python start_server.py
	#uv run python server.py



