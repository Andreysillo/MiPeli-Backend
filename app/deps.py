from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import Verifier, firebase_verifier
from app.config import settings

bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_verifier() -> Verifier:
    return firebase_verifier(settings.firebase_project_id)


async def current_user(
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    verify: Annotated[Verifier, Depends(get_verifier)],
) -> str:
    """El uid del token verificado (nunca de lo que diga el cliente). 401 si falta, es inválido o venció."""
    if cred is None:
        raise HTTPException(401, "Falta el token", headers={"WWW-Authenticate": "Bearer"})
    try:
        return await run_in_threadpool(verify, cred.credentials)
    except Exception:
        raise HTTPException(401, "Token inválido o vencido", headers={"WWW-Authenticate": "Bearer"}) from None
