from typing import Annotated

from fastapi import APIRouter, HTTPException, Header, status

from app.models.auth import TokenResponse
from app.security import (
    authentication_is_configured,
    create_access_token,
    credentials_are_valid,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=TokenResponse)
def issue_token(
    username: Annotated[str | None, Header(alias="AUTH_USERNAME")] = None,
    password: Annotated[str | None, Header(alias="AUTH_PASSWORD")] = None,
) -> TokenResponse:
    if not authentication_is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configure AUTH_USERNAME, AUTH_PASSWORD, and a 32-character JWT_SECRET",
        )
    if not username or not password or not credentials_are_valid(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(access_token=create_access_token(username))