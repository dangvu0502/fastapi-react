from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from src.auth.schemas import (
    UserLogin,
    UserLoginResponse,
    UserRegister,
    UserRegisterResponse,
)
from src.auth.services import create, get_by_email
from src.config import settings
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
    response: Response,
):
    user = await get_by_email(db_session=db_session, email=user_in.email)
    if user and user.verify_password(user_in.password):
        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=user.token,
            httponly=True,
            secure=settings.ENVIRONMENT != "LOCAL",  # Use secure cookies in production
            samesite="lax",
            max_age=settings.JWT_EXP * 60,  # Convert minutes to seconds
        )
        return UserLoginResponse(
            email=user.email,
            message="Login successful"
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


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@auth_router.get("/me")
async def get_current_user(
    db_session: DBSession,
    # We'll add cookie authentication dependency later
):
    # TODO: Implement cookie-based authentication
    return {"message": "Not implemented yet"}
