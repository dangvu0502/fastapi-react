from sqlalchemy import Table, select
from sqlalchemy.schema import CreateSchema, DropSchema
import logging

from src.auth.models import EduUser, hash_password
from src.config import settings
from src.database.core import DatabaseSessionManager, EduBase
from src.database.utils import database_exists, create_database

logger = logging.getLogger(__name__)

def get_core_tables() -> list[Table]:
    """Fetches tables that belong to the 'edu_core' schema."""
    core_tables: list[Table] = []
    for _, table in EduBase.metadata.tables.items():
        if table.schema == settings.DATABASE_SCHEMA:
            core_tables.append(table)
    return core_tables


async def init_database(*, session_manager: DatabaseSessionManager):
    """
    Initialize the database.
    """
    if not await database_exists(str(settings.DATABASE_ASYNC_URL)):
        await create_database(str(settings.DATABASE_ASYNC_URL))
       
    schema_name = settings.DATABASE_SCHEMA
    tables = get_core_tables()

    # Create schema (in separate transaction to handle if it already exists)
    try:
        async with session_manager.connect() as conn:
            await conn.execute(CreateSchema(schema_name))
            logger.info(f"Created schema: {schema_name}")
    except Exception:
        logger.debug(f"Schema {schema_name} already exists")
    
    # Create tables in a new transaction
    async with session_manager.connect() as conn:
        await conn.run_sync(EduBase.metadata.create_all, tables=tables)
        logger.info("Database tables created successfully")
    
    # Create default user
    async with session_manager.session() as session:
        result = await session.execute(select(EduUser).filter(EduUser.email == "admin@edu.com"))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user = EduUser(email="admin@edu.com", password=hash_password("admin"))
            session.add(user)
            await session.commit()
            logger.info("Created default admin user: admin@edu.com")
        else:
            logger.debug("Admin user admin@edu.com already exists")
        
async def drop_database(*, session_manager: DatabaseSessionManager):
    """
    Drop the database.
    """
    async with session_manager.connect() as conn:
        await conn.run_sync(EduBase.metadata.drop_all)
        await conn.execute(DropSchema(settings.DATABASE_SCHEMA))
        logger.info("Database cleanup completed")
