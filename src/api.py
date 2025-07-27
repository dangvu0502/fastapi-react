from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.auth.routes import auth_router


class ErrorMessage(BaseModel):
    """Represents a single error message."""

    msg: str

class ErrorResponse(BaseModel):
    """Defines the structure for API error responses."""

    detail: list[ErrorMessage] | None = None


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

@api_router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
