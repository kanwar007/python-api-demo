import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

JWT_ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)


def authentication_is_configured() -> bool:
    return bool(
        settings.auth_username
        and settings.auth_password.get_secret_value()
        and len(settings.jwt_secret.get_secret_value()) >= 32
    )


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "iat": now, "exp": expires_at},
        settings.jwt_secret.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


def require_bearer_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if len(settings.jwt_secret.get_secret_value()) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication is not configured",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return subject


def credentials_are_valid(username: str, password: str) -> bool:
    configured_password = settings.auth_password.get_secret_value()
    return secrets.compare_digest(
        username.encode("utf-8"), settings.auth_username.encode("utf-8")
    ) and secrets.compare_digest(
        password.encode("utf-8"), configured_password.encode("utf-8")
    )