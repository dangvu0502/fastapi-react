import secrets
import string
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from src.config import settings
from src.database.core import EduBase
from src.models import TimeStampMixin


def generate_password() -> str:
    """Generate a random, strong password with at least one lowercase, one uppercase, and three digits."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        # Ensure password meets complexity requirements
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)

class EduUser(EduBase, TimeStampMixin):
    __tablename__ = "edu_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    def verify_password(self, password: str) -> bool:
        """ Verify the password against the stored hash. """
        if not self.password:
            raise ValueError("Password cannot be empty")
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """ Set the password for the user. """
        if not password:
            raise ValueError("Password cannot be empty")

        self.password = hash_password(password)

    @property
    def token(self) -> str:
        """Generate a JWT token for the user."""
        now = datetime.now(timezone.utc)
        exp = (now + timedelta(seconds=settings.JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


