"""Extract credentials, verify identity, then check permission.

Opaque random teaching tokens, not JWTs or an OAuth flow. This API path uses opaque tokens. Browser login and its server-side sessions
are implemented separately in pages.py and sessions.py.
"""
from dataclasses import dataclass
from hashlib import sha256
import secrets
import time
from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


@dataclass(frozen=True)
class Principal:
    username: str
    permissions: frozenset[str]


class TokenRegistry:
    """In-memory lookup: restart invalidates old tokens, not saved menu data."""
    def __init__(self, clock=time.time):
        self.clock = clock
        self.records = {}

    def issue(self, principal: Principal, lifetime=4 * 60 * 60):
        token = secrets.token_urlsafe(32)
        expires = self.clock() + lifetime
        self.records[sha256(token.encode()).hexdigest()] = (principal, expires)
        return token, expires

    def verify(self, token: str):
        record = self.records.get(sha256(token.encode()).hexdigest())
        if record is None or self.clock() >= record[1]:
            return None
        return record[0]


bearer = HTTPBearer(auto_error=False, scheme_name="Classroom bearer token",
    description="Paste a current token from .classroom/security-credentials.json")
Credential = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


def current_user(request: Request, credential: Credential) -> Principal:
    # HTTPBearer only extracts the credential. The registry verifies it.
    user = request.app.state.tokens.verify(credential.credentials) if credential else None
    if user is None:
        raise HTTPException(status_code=401, detail="Missing, invalid or expired credential.",
                            headers={"WWW-Authenticate": "Bearer"})
    return user


User = Annotated[Principal, Depends(current_user)]


def require_staff(user: User) -> Principal:
    # Permissions come from trusted server data, not the request body.
    if "menu:write" not in user.permissions:
        raise HTTPException(status_code=403, detail="This identity cannot change the menu.")
    return user
