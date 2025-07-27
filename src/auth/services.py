# Service for auth module
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import EduUser
from src.auth.schemas import UserCreate, UserRegister

async def get_by_email(*, db_session: AsyncSession, email: str) -> EduUser | None:
    """Returns a user object based on user email."""
    return (
        await db_session.execute(select(EduUser).where(EduUser.email == email))
    ).scalar_one_or_none()


async def create(*, db_session: AsyncSession, user_in: (UserRegister | UserCreate)) -> EduUser:
    """Creates a new edu user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")

    # create the user data dictionary
    user = {
        **user_in.model_dump(exclude={"password"}),
        "password": password,
    }

    result = await db_session.execute(insert(EduUser).values(user).returning(EduUser))
    await db_session.commit()
    return result.scalar_one()
