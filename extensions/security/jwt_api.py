"""Optional local JWT exercise; not an OAuth/OIDC authorisation server.

Reuses the trusted accounts and business service. Only the credential mechanism
changes. PyJWT signs/verifies; the application still checks current permissions.
"""
import secrets
import time
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from .auth import Principal

ISSUER = "station-bar-classroom"
AUDIENCE = "station-bar-api"
ALGORITHM = "HS256"
TOKEN_SECONDS = 300


class JWTService:
    """One process holds the signing key; a restart invalidates its earlier JWTs.

    HS256 is suitable for showing a single trusted issuer/verifier. Independent
    services/providers need their own key-distribution and rotation design.
    """
    def __init__(self, key=None):
        self.key = secrets.token_bytes(32) if key is None else key
        if not isinstance(self.key, bytes) or len(self.key) < 32:
            raise ValueError("JWT key must contain at least 32 random bytes.")

    def issue(self, user: Principal):
        now = int(time.time())
        claims = {"iss": ISSUER, "aud": AUDIENCE, "sub": user.username,
                  "iat": now, "nbf": now, "exp": now + TOKEN_SECONDS,
                  "scope": " ".join(sorted(user.permissions))}
        return jwt.encode(claims, self.key, algorithm=ALGORITHM,
                          headers={"typ": "at+jwt"})

    def verify(self, token):
        # The algorithm, issuer and audience are OUR configuration, never taken
        # from unverified claims or a client-selected key URL.
        claims = jwt.decode(token, self.key, algorithms=[ALGORITHM],
                            issuer=ISSUER, audience=AUDIENCE,
                            options={"require": ["iss", "aud", "sub", "iat", "nbf", "exp", "scope"],
                                     "strict_aud": True})
        if jwt.get_unverified_header(token).get("typ") != "at+jwt":
            raise jwt.InvalidTokenError("Wrong token type.")
        if not isinstance(claims["sub"], str) or not claims["sub"]:
            raise jwt.InvalidTokenError("Invalid subject.")
        if not isinstance(claims["scope"], str):
            raise jwt.InvalidTokenError("Invalid scope.")
        for name in ("iat", "nbf", "exp"):
            if type(claims[name]) is not int:
                raise jwt.InvalidTokenError("Invalid timestamp.")
        return claims


bearer = HTTPBearer(auto_error=False, scheme_name="JWT access token (optional)",
    bearerFormat="JWT", description="Get access_token from POST /jwt/token; paste ONLY its value here.")
Credential = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


def unauthorised():
    return HTTPException(401, "Missing, invalid or expired JWT.",
                         headers={"WWW-Authenticate": "Bearer"})


def jwt_user(request: Request, credential: Credential) -> Principal:
    if credential is None:
        raise unauthorised()
    try:
        claims = request.app.state.jwt_tokens.verify(credential.credentials)
    except jwt.InvalidTokenError:
        raise unauthorised() from None
    current = request.app.state.accounts.principal(claims["sub"])
    if current is None:
        raise unauthorised()
    # A valid signed scope is still bounded by current trusted account policy.
    # Removing a permission takes effect even while an older token is valid.
    return Principal(current.username, current.permissions & frozenset(claims["scope"].split()))


JWTUser = Annotated[Principal, Depends(jwt_user)]


def jwt_staff(user: JWTUser) -> Principal:
    if "menu:write" not in user.permissions:
        raise HTTPException(403, "This identity cannot change the menu.")
    return user


JWTStaff = Annotated[Principal, Depends(jwt_staff)]


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64)
    password: SecretStr = Field(min_length=1, max_length=256)


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = TOKEN_SECONDS


def install_jwt_api(app, service: JWTService):
    # Imported here after create_app has connected the existing solution package.
    from bar_api.models import MenuItem, MenuItemInput
    app.state.jwt_tokens = service
    router = APIRouter(prefix="/jwt", tags=["Optional JWT exercise"])

    @router.post("/token", response_model=TokenOutput,
                 description="Local JSON credential exchange for this exercise; not an OAuth token endpoint.")
    def issue_token(body: LoginInput, response: Response):
        attempts = app.state.login_attempts
        if attempts.blocked(body.username):
            raise HTTPException(429, "Too many attempts. Please wait one minute.")
        account = app.state.accounts.authenticate(body.username, body.password.get_secret_value())
        if account is None:
            attempts.failure(body.username)
            raise HTTPException(401, "Username or password not recognised.")
        attempts.clear(body.username)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        user = app.state.accounts.principal(account.username)
        return TokenOutput(access_token=service.issue(user))

    @router.get("/whoami", responses={401: {"description": "No valid JWT"}})
    def whoami(user: JWTUser):
        return {"username": user.username, "permissions": sorted(user.permissions)}

    @router.post("/menu-items", response_model=MenuItem, status_code=201,
                 responses={401: {"description": "No valid JWT"},
                            403: {"description": "Identity lacks menu:write"}})
    def create_menu_item(body: MenuItemInput, response: Response, user: JWTStaff):
        item = app.state.service.create_menu_item(body.model_dump())
        response.headers["Location"] = f"/menu-items/{item['id']}"
        return item

    app.include_router(router)
