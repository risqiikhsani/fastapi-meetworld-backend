from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env."""

    openai_api_key: str

    # JWT_SECRET must match the value used by nestjs-meetworld-backend so the
    # NestJS-issued access tokens validate here. JWT_ALGORITHM defaults to
    # HS256 to mirror the @nestjs/jwt default (no algorithm is set in
    # nestjs-meetworld-backend/src/auth/auth.module.ts).
    jwt_secret: str = Field(..., min_length=1)
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Build Settings, raising fast if required env vars are missing."""
    return Settings()  # type: ignore[call-arg]