.PHONY: dev install
dev:
	uv run fastapi dev src/main.py

install:
	uv sync
