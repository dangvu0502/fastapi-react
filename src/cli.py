import click
import logging
import sys
import asyncio
from functools import wraps

from src.database.core import session_manager
from src.database.manage import drop_database, init_database

logger = logging.getLogger(__name__)

def make_sync(func):
    """Decorator to run the function synchronously."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

@click.group()
def edu_cli():
    """CLI for the edu project."""
    pass

@edu_cli.group("database")
def edu_database():
    """Container for all edu database commands."""
    pass

@edu_database.command("init")
@make_sync
async def init_db():
    """Initialize the database."""
    click.echo("Initializing database...")
    await init_database(session_manager=session_manager)
    click.secho("Database initialized successfully", fg="green")
    
@edu_database.command("drop")
@make_sync
async def drop_db():
    """Drop the database."""
    click.echo("Dropping database...")
    await drop_database(session_manager=session_manager)
    click.secho("Database dropped successfully", fg="green")
    
def main():
    """Main entry point for the CLI."""
    try:
        edu_cli()
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)
        
if __name__ == "__main__":
    main()
    
    
    