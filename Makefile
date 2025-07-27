.PHONY: install dev-backend dev-frontend

install:
	@echo "Installing backend and frontend dependencies..."
	uv sync && cd web && npm install

dev-backend:
	@echo "Starting backend development server..."
	uv run fastapi dev src/main.py

dev-frontend:
	@echo "Starting frontend development server..."
	cd web && npm run dev
