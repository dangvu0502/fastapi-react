import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.config import settings
from src.database.core import session_manager

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
logging.basicConfig(level=logging.DEBUG if settings.LOG_LEVEL == "DEBUG" else logging.INFO, format=LOG_FORMAT_DEBUG)

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    await session_manager.startup()
    yield
    # Shutdown
    if session_manager._async_engine is not None:
        await session_manager.close()

app = FastAPI(
    openapi_url="",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

api = FastAPI(
    title="SaaS01 API",
    version=settings.APP_VERSION,
    root_path=settings.API_V1_STR,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/docs/openapi.json",
)

api.include_router(api_router)
app.mount(settings.API_V1_STR, api)
