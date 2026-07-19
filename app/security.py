"""JWT validation dependency for incoming requests.

Mirrors the contract implemented by
nestjs-meetworld-backend/src/auth/strategies/jwt.strategy.ts: HS256 signature
verification using a shared JWT_SECRET, no DB lookup, claims reduced to
{ id: sub, email }. Failure mode is a 401 with detail="Unauthorized" to match
passport-jwt's default error string so the frontend's error handling stays
uniform across both backends.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: str
    email: str


def verify_jwt(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    settings = get_settings()
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": True},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        ) from exc

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return CurrentUser(id=sub, email=email)


CurrentUserDep = Annotated[CurrentUser, Depends(verify_jwt)]