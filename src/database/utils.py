import os

import sqlalchemy as sa
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import _set_url_database, _sqlite_file_exists, make_url
from sqlalchemy_utils.functions.orm import quote

async def _get_scalar_result(engine, sql):
    try:
        async with engine.connect() as conn:
            return await conn.scalar(sql)
    except Exception:
        return False


async def database_exists(url):
        url = make_url(url)
        database = url.database
        dialect_name = url.get_dialect().name
        engine = None
        try:
            if dialect_name == "postgresql":
                text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
                for db in (database, "postgres", "template1", "template0", None):
                    url = _set_url_database(url, database=db)
                    engine = create_async_engine(url)
                    try:
                        return bool(await _get_scalar_result(engine, sa.text(text)))
                    except (ProgrammingError, OperationalError):
                        pass
                return False

            elif dialect_name == "mysql":
                url = _set_url_database(url, database=None)
                engine = create_async_engine(url)
                text = (
                    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                    "WHERE SCHEMA_NAME = '%s'" % database
                )
                return bool(await _get_scalar_result(engine, sa.text(text)))

            elif dialect_name == "sqlite":
                url = _set_url_database(url, database=None)
                engine = create_async_engine(url)
                if database:
                    return database == ":memory:" or _sqlite_file_exists(database)
                else:
                    # The default SQLAlchemy database is in memory, and :memory: is
                    # not required, thus we should support that use case.
                    return True
            else:
                text = "SELECT 1"
                try:
                    engine = create_async_engine(url)
                    return bool(await _get_scalar_result(engine, sa.text(text)))
                except (ProgrammingError, OperationalError):
                    return False
        finally:
            if engine:
                await engine.dispose()
                

async def create_database(url, encoding="utf8", template=None):
        url = make_url(url)
        database = url.database
        dialect_name = url.get_dialect().name
        dialect_driver = url.get_dialect().driver

        if dialect_name == "postgresql":
            url = _set_url_database(url, database="postgres")
        elif dialect_name == "mssql":
            url = _set_url_database(url, database="master")
        elif dialect_name == "cockroachdb":
            url = _set_url_database(url, database="defaultdb")
        elif not dialect_name == "sqlite":
            url = _set_url_database(url, database=None)

        if (dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}) or (
            dialect_name == "postgresql"
            and dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}
        ):
            engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
        else:
            engine = create_async_engine(url)

        if dialect_name == "postgresql":
            if not template:
                template = "template1"

            async with engine.begin() as conn:
                text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
                    quote(conn, database), encoding, quote(conn, template)
                )
                await conn.execute(sa.text(text))

        elif dialect_name == "mysql":
            async with engine.begin() as conn:
                text = "CREATE DATABASE {} CHARACTER SET = '{}'".format(
                    quote(conn, database), encoding
                )
                await conn.execute(sa.text(text))

        elif dialect_name == "sqlite" and database != ":memory:":
            if database:
                async with engine.begin() as conn:
                    await conn.execute(sa.text("CREATE TABLE DB(id int)"))
                    await conn.execute(sa.text("DROP TABLE DB"))

        else:
            async with engine.begin() as conn:
                text = f"CREATE DATABASE {quote(conn, database)}"
                await conn.execute(sa.text(text))

        await engine.dispose()


async def drop_database(url):
        url = make_url(url)
        database = url.database
        dialect_name = url.get_dialect().name
        dialect_driver = url.get_dialect().driver

        if dialect_name == "postgresql":
            url = _set_url_database(url, database="postgres")
        elif dialect_name == "mssql":
            url = _set_url_database(url, database="master")
        elif dialect_name == "cockroachdb":
            url = _set_url_database(url, database="defaultdb")
        elif not dialect_name == "sqlite":
            url = _set_url_database(url, database=None)

        if dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}:
            engine = create_async_engine(url, connect_args={"autocommit": True})
        elif dialect_name == "postgresql" and dialect_driver in {
            "asyncpg",
            "pg8000",
            "psycopg2",
            "psycopg2cffi",
        }:
            engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
        else:
            engine = create_async_engine(url)

        if dialect_name == "sqlite" and database != ":memory:":
            if database:
                os.remove(database)
        elif dialect_name == "postgresql":
            async with engine.begin() as conn:
                # Disconnect all users from the database we are dropping.
                version = conn.dialect.server_version_info
                pid_column = "pid" if (version >= (9, 2)) else "procpid"
                text = """
                SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database}'
                AND {pid_column} <> pg_backend_pid();
                """.format(
                    pid_column=pid_column, database=database
                )
                await conn.execute(sa.text(text))

                # Drop the database.
                text = f"DROP DATABASE {quote(conn, database)}"
                await conn.execute(sa.text(text))
        else:
            async with engine.begin() as conn:
                text = f"DROP DATABASE {quote(conn, database)}"
                await conn.execute(sa.text(text))

        await engine.dispose()