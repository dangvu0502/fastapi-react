from fastapi import APIRouter, HTTPException, status

from src.auth.schemas import (
    UserLogin,
    UserLoginResponse,
    UserRegister,
    UserRegisterResponse,
)
from src.auth.services import create, get_by_email
from src.database.core import DBSession

auth_router = APIRouter()

@auth_router.post("/register", response_model=UserRegisterResponse)
async def register_user(
    user_in: UserRegister,
    db_session: DBSession,
):
    user = await get_by_email(db_session=db_session, email=user_in.email)
    if user:
        # Pydantic v2 compatible error handling
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "A user with this email already exists.",
                    "loc": ["email"],
                    "type": "value_error",
                }
            ],
        )

    user = await create(db_session=db_session, user_in=user_in)
    return user


@auth_router.post("/login", response_model=UserLoginResponse)
async def login(
    user_in: UserLogin,
    db_session: DBSession,
):
    user = await get_by_email(db_session=db_session, email=user_in.email)
    if user and user.verify_password(user_in.password):
        return UserLoginResponse(
            email=user.email,
            access_token=user.token,
        )
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[
            {
                "msg": "Invalid credentials",
                "loc": ["email", "password"],
                "type": "value_error",
            }
        ],
    )
