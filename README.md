# FastAPI + React Full-Stack Template

A modern, production-ready full-stack web application template using FastAPI (backend) and React with TypeScript (frontend).

##  Features

### Backend (FastAPI)
- **FastAPI** with async/await support
- **SQLAlchemy** with async PostgreSQL (asyncpg)
- **Alembic** for database migrations
- **JWT Authentication** with httpOnly cookies 
- **Pydantic** for data validation
- **Custom CLI** for database management
- **Docker Compose** for PostgreSQL
- **Type-safe** OpenAPI schema generation

### Frontend (React + TypeScript)
- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** with shadcn/ui components
- **OpenAPI TypeScript** client generation
- **Secure Authentication** with httpOnly cookies
- **Type-safe** API calls with generated types

## Prerequisites

- Python 3.12+
- Node.js 22+
- PostgreSQL (or use Docker Compose)
- [uv](https://github.com/astral-sh/uv) (Python package manager)

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd fastapi-react
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Install dependencies
```bash
make install
# or manually:
uv sync
cd web && npm install
```

### 4. Start PostgreSQL
```bash
docker-compose up -d
```

### 5. Initialize the database
```bash
# Using CLI
uv run cli database init

# Or using Alembic
uv run alembic upgrade head
```

## Development

### Start both frontend and backend
```bash
make dev
```

### Start backend only
```bash
make dev-backend
# or
uv run fastapi dev src/main.py
```

### Start frontend only
```bash
make dev-frontend
# or
cd web && npm run dev
```

### Generate TypeScript types from OpenAPI
```bash
# Backend must be running
make generate-client
# or
cd web && npm run generate-client
```