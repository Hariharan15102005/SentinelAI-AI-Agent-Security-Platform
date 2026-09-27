import hmac
from typing import Optional
from fastapi import Header, HTTPException, status
from app.config.settings import settings

async def verify_internal_token(
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Validates that the incoming request contains the valid shared secret using constant-time comparison.
    Supports either X-Internal-Token header or Authorization: Bearer <secret>.
    """
    token_candidate = x_internal_token
    if not token_candidate and authorization:
        if authorization.startswith("Bearer "):
            token_candidate = authorization[7:].strip()
        else:
            token_candidate = authorization.strip()

    if not token_candidate or not settings.INTERNAL_SERVICE_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal service authorization secret."
        )

    # Constant-time comparison prevents timing attacks
    is_valid = hmac.compare_digest(token_candidate.encode('utf-8'), settings.INTERNAL_SERVICE_SECRET.encode('utf-8'))
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal service authorization secret."
        )
    return token_candidate



