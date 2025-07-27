from pydantic import EmailStr, field_validator

from src.auth.models import generate_password, hash_password
from src.schemas import EduBase


class UserBase(EduBase):
    """Pydantic model for user base data."""
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def email_required(cls, v: EmailStr) -> EmailStr:
        """Ensure the email field is not empty."""
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserLogin(UserBase):
    """Pydantic model for user login data."""

    password: str

    @field_validator("password")
    @classmethod
    def password_required(cls, v: str) -> str:
        """Ensure the password field is not empty."""
        if not v:
            raise ValueError("Must not be empty string")
        return v

class UserRegister(UserBase):
    """Pydantic model for user registration data."""

    password: str = ""

    @field_validator("password", mode="before")
    @classmethod
    def generate_or_hash_password(cls, v: str | bytes) -> bytes:
        """Generate and hash a password if not provided."""
        if isinstance(v, bytes):
            return v
        password = v or generate_password()
        return hash_password(password)

class UserCreate(UserBase):
    """Pydantic model for user creation data."""
    password: str | None = None

    @field_validator("password", mode="before")
    @classmethod
    def hash(cls, v: str | None) -> bytes:
        """Hash the password before storing."""
        if v is None:
            raise ValueError("Password cannot be None")
        return hash_password(str(v))


class UserLoginResponse(UserBase):
    """Pydantic model for user login response data."""
    message: str
    

class UserRegisterResponse(UserBase):
    """Pydantic model for user registration response data."""
    access_token: str | None = None
