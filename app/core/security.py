"""Bearer token authentication dependency."""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security = HTTPBearer()


async def require_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Validate Bearer token against settings.API_TOKEN."""
    if not secrets.compare_digest(credentials.credentials, settings.API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )
    return credentials.credentials
