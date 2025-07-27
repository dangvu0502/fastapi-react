import contextlib
import logging
from collections.abc import AsyncGenerator
from typing import Annotated, Any, ClassVar

from fastapi import Depends
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

logger = logging.getLogger(__name__)

class EduBase(DeclarativeBase):
    metadata: ClassVar[MetaData] = MetaData(naming_convention=settings.DATABASE_NAMING_CONVENTION, schema=settings.DATABASE_SCHEMA)
    __table_args__: dict[str, Any] = {"schema": settings.DATABASE_SCHEMA}

class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any]) -> None:
        self._async_engine: AsyncEngine | None = create_async_engine(
            url = host,
            **engine_kwargs,
        )
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(
            autocommit=False,
            bind=self._async_engine,
            expire_on_commit=False,
        )

    async def startup(self) -> None:
        if self._async_engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            logger.debug("Connect database successfully")

    async def close(self) -> None:
        if self._async_engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        await self._async_engine.dispose()
        self._async_engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        if self._async_engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._async_engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

session_manager: DatabaseSessionManager = DatabaseSessionManager(
        host=str(settings.DATABASE_ASYNC_URL),
        engine_kwargs={
            "pool_size": settings.DATABASE_POOL_SIZE,
            "pool_recycle": settings.DATABASE_POOL_TTL,
            "pool_pre_ping": settings.DATABASE_POOL_PRE_PING,
            "echo": settings.DATABASE_ECHO,
        },
    )

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.session() as session:
        yield session

DBSession = Annotated[AsyncSession, Depends(get_db_session)]


