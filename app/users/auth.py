from fastapi_clerk_auth import (
    ClerkConfig,
    ClerkHTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.config import get_settings
from app.errors import InvalidCredentials, NoBearerToken

config = get_settings()

clerk_config = ClerkConfig(jwks_url=config.clerk_jwks_url)

clerk_auth_guard = ClerkHTTPBearer(config=clerk_config, auto_error=False)

def get_user_id_from_auth(credentials: HTTPAuthorizationCredentials | None):
    if credentials is None:
        raise NoBearerToken
    if credentials.decoded is None:
        print(credentials)
        raise InvalidCredentials
    else:
        return credentials.decoded["sub"] # type: ignore

def get_role_from_auth(credentials: HTTPAuthorizationCredentials | None):
    if credentials is None:
        raise NoBearerToken
    if (credentials.decoded or credentials.decoded["clerk_role"]) is None: # type: ignore
        raise InvalidCredentials
    else:
        return credentials.decoded["clerk_role"] # type: ignore

