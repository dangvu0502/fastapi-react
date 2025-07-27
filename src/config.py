from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import DB_NAMING_CONVENTION, Environment


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(CustomBaseSettings):
    DATABASE_ASYNC_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 16
    DATABASE_POOL_TTL: int = 60 * 20  # 20 minutes
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_NAMING_CONVENTION: dict[str, str] = DB_NAMING_CONVENTION
    DATABASE_ECHO: bool = False
    DATABASE_SCHEMA: str = "edu_core"
    ENVIRONMENT: Environment = Environment.LOCAL

    JWT_SECRET: str
    JWT_ALG: str
    JWT_EXP: int

    # @field_validator("JWT_SECRET")
    # def validate_jwt_secret(cls, v: str) -> str:
    #     if len(v) < 32:
    #         raise ValueError("JWT_SECRET must be at least 32 characters long")
    #     if not re.search(r"[a-z]", v) or not re.search(r"[A-Z]", v) or not re.search(r"[0-9]", v):
    #         raise ValueError("JWT_SECRET must contain a mix of lowercase, uppercase, and numeric characters")
    #     return v

    # @field_validator("JWT_ALG")
    # def validate_jwt_alg(cls, v: str) -> str:
    #     allowed_algs = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"}
    #     if v.lower() == "none":
    #         raise ValueError("Algorithm 'none' is not allowed for JWT_ALG")
    #     if v not in allowed_algs:
    #         raise ValueError(f"JWT_ALG must be one of {allowed_algs}")
    #     return v

    # @field_validator("JWT_EXP")
    # def validate_jwt_exp(cls, v: int) -> int:
    #     min_exp = 5 * 60  # 5 minutes
    #     max_exp = 24 * 60 * 60  # 24 hours
    #     if not (min_exp <= v <= max_exp):
    #         raise ValueError(f"JWT_EXP must be between {min_exp} and {max_exp} seconds")
    #     return v

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_HEADERS: list[str] = ["*"]

    API_V1_STR: str = "/api/v1"
    APP_VERSION: str = "0.1"

    LOG_LEVEL: str = "DEBUG"


settings = Config()
