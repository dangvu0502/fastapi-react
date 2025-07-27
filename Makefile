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

dev:
	@echo "Starting development server..."
	make dev-backend & make dev-frontend

generate-client:
	@echo "Generating TypeScript client from OpenAPI schema..."
	cd web && npm run generate-client

type-check:
	@echo "Running TypeScript type check..."
	cd web && npx tsc --noEmit


