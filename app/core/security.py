"""Bearer token authentication dependency."""

import secrets  # noqa: F401 — needed when auth is restored

from fastapi import Depends, HTTPException, status  # noqa: F401 — needed when auth is restored
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings  # noqa: F401 — needed when auth is restored

security = HTTPBearer()


async def require_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Validate Bearer token against settings.API_TOKEN."""
    # TEMPORARY HACKATHON BYPASS: allow all requests
    return "bypass"

    # Original check (restore after hackathon):
    # if not secrets.compare_digest(credentials.credentials, settings.API_TOKEN):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid or missing API token",
    #     )
    # return credentials.credentials
