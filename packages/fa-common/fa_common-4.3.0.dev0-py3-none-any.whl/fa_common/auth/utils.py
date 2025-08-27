import json
import time

from fastapi import Depends, Security
from fastapi.openapi.models import OAuthFlowImplicit, OAuthFlows
from fastapi.security import APIKeyHeader, APIKeyQuery, OAuth2, SecurityScopes
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from pydantic import ValidationError

from fa_common import (
    AuthType,
    ForbiddenError,
    InternalServerError,
    UnauthorizedError,
    async_get,
    get_settings,
)
from fa_common import logger as LOG
from fa_common.auth.enums import AccessLevel
from fa_common.routes.user.types import PermissionDef

from .models import AuthUser

# COOKIE_DOMAIN = "localtest.me"

api_key_query = APIKeyQuery(name=get_settings().API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=get_settings().API_KEY_NAME, auto_error=False)
# api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        implicit=OAuthFlowImplicit(
            authorizationUrl=get_settings().OAUTH2_AUTH_URL,
            scopes=json.loads(get_settings().OAUTH2_SCOPES),
        )
    ),
    auto_error=False,
)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    # api_key_cookie: str = Security(api_key_cookie),
) -> str | None:
    if api_key_query is not None:
        return api_key_query
    elif api_key_header is not None:
        return api_key_header

    return None


async def get_user_profile(url: str, auth: str) -> AuthUser:
    data = await async_get(url, auth, json_only=True)
    return AuthUser(**data)  # type: ignore FIXME


def get_token_auth_header(auth: str) -> str:
    """Obtains the Access Token from the Authorization Header."""
    if not auth:
        raise UnauthorizedError(
            detail="Authorization header is expected",
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise UnauthorizedError(
            detail="Authorization header must start with Bearer",
        )
    elif len(parts) == 1:
        raise UnauthorizedError(
            detail="Token not found",
        )
    elif len(parts) > 2:
        raise UnauthorizedError(
            detail="Authorization header must be Bearer token",
        )

    token = parts[1]
    return token


_JWKS_CACHE: dict[str, dict] = {}
_JWKS_CACHE_EXPIRES_AT: float | None = None
_JWKS_TTL_SECONDS = 60 * 10  # 10 minutes


async def _get_jwks(settings):
    global _JWKS_CACHE_EXPIRES_AT
    # Refresh cache if empty or expired
    if not _JWKS_CACHE or (_JWKS_CACHE_EXPIRES_AT and time.time() > _JWKS_CACHE_EXPIRES_AT):
        jwks = await async_get(url=settings.OAUTH2_JWKS_URI, json_only=True)
        if not isinstance(jwks, dict):
            raise ValueError("JWKS is not a valid JSON object")
        # Rebuild cache keyed by kid for fast lookup
        _JWKS_CACHE.clear()
        for key in jwks.get("keys", []):
            if "kid" in key:
                _JWKS_CACHE[key["kid"]] = key
        _JWKS_CACHE_EXPIRES_AT = time.time() + _JWKS_TTL_SECONDS
    return _JWKS_CACHE


async def decode_token(auth: str):
    settings = get_settings()
    token = get_token_auth_header(auth)
    jwks_cache = await _get_jwks(settings)

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise UnauthorizedError(detail="Malformed token header") from e

    kid = unverified_header.get("kid")
    key = jwks_cache.get(kid) if isinstance(kid, str) else None
    if not key:
        raise UnauthorizedError(detail="Unable to find appropriate key")

    rsa_key = {k: key.get(k) for k in ("kty", "kid", "use", "n", "e")}

    # Build accepted client ids (aud for ID tokens, client_id for access tokens)
    primary_client = settings.API_AUDIENCE
    extra_clients_raw = getattr(settings, "OIDC_ACCEPTED_CLIENT_IDS", None)
    accepted_clients: set[str] = set()
    if primary_client:
        accepted_clients.add(primary_client)
    if extra_clients_raw:
        for part in extra_clients_raw.split(","):
            if part.strip():
                accepted_clients.add(part.strip())
    expected_aud = primary_client  # still used for jose audience verification when single

    # First attempt: verify audience if we have one. Disable at_hash verification since we don't supply access token here.
    verify_aud = bool(expected_aud)
    base_options = {"verify_aud": verify_aud, "verify_at_hash": False}
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=settings.JWT_ALGORITHMS,
            audience=expected_aud if verify_aud else None,
            issuer=settings.OAUTH2_ISSUER,
            options=base_options,
        )
    except JWTClaimsError as e1:
        try:
            # Retry without aud verification (covers Cognito access tokens w/out aud)
            retry_options = {"verify_aud": False, "verify_at_hash": False}
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=settings.JWT_ALGORITHMS,
                issuer=settings.OAUTH2_ISSUER,
                options=retry_options,
            )
            if expected_aud:
                aud_or_client = payload.get("aud") or payload.get("client_id")
                if aud_or_client != expected_aud:
                    raise UnauthorizedError(detail="Audience / client_id mismatch") from None
        except JWTError as e2:
            msg = str(e2)
            if "at_hash" in msg:
                # Fallback: ID token contains at_hash but we don't have the access token; perform minimal manual validation
                unverified_claims = jwt.get_unverified_claims(token)
                # Basic time/issuer/audience checks
                iss = unverified_claims.get("iss")
                if iss != settings.OAUTH2_ISSUER:
                    raise UnauthorizedError(detail="Invalid issuer") from None
                if expected_aud:
                    aud_val = unverified_claims.get("aud") or unverified_claims.get("client_id")
                    if aud_val != expected_aud:
                        raise UnauthorizedError(detail="Audience / client_id mismatch") from None
                exp = unverified_claims.get("exp")
                if exp and exp < int(time.time()):
                    raise UnauthorizedError(detail="token is expired") from None
                payload = unverified_claims
            else:
                raise e1 from None
    except ExpiredSignatureError as e:
        raise UnauthorizedError(detail="token is expired") from e
    except Exception as e:
        raise UnauthorizedError(detail="Unable to parse authentication token.") from e

    token_use = payload.get("token_use")
    if token_use and token_use not in ("id", "access"):
        raise UnauthorizedError(detail="Unsupported token_use")

    # Client id / audience enforcement using consolidated list
    if accepted_clients:
        aud_claim = payload.get("aud")
        client_id_claim = payload.get("client_id")
        client_val = None
        if token_use == "id":
            client_val = aud_claim
        elif token_use == "access":
            client_val = client_id_claim or aud_claim
        else:
            client_val = aud_claim or client_id_claim
        if client_val not in accepted_clients:
            raise UnauthorizedError(detail="Audience / client_id not accepted")

    return payload


async def get_user(payload: dict, token: str, get_profile: bool = True) -> AuthUser | None:
    settings = get_settings()
    user: AuthUser | None = None
    token_scopes: list[str] = []
    roles: list[str] = []

    if "permissions" in payload and payload.get("permissions") is not None:
        token_scopes = payload["permissions"]

    if settings.ROLES_NAMESPACE in payload and payload.get(settings.ROLES_NAMESPACE) is not None:
        roles = payload[settings.ROLES_NAMESPACE]

    if "sub" in payload:
        token_use = payload.get("token_use")
        userinfo_url = settings.OAUTH2_USERINFO_URL

        # For access tokens (token_use == 'access') try userinfo endpoint if available; otherwise use claims.
        if get_profile and token_use != "id" and userinfo_url:
            try:
                user = await get_user_profile(userinfo_url, token)
            except Exception as err:
                LOG.warning("UserInfo request failed, falling back to token claims. Error: %s", err)
                user = AuthUser(**payload)
        else:
            user = AuthUser(**payload)

        if len(token_scopes) > 0:
            user.scopes = token_scopes

        if len(roles) > 0:
            user.roles = roles

    return user


async def get_standalone_user() -> AuthUser:
    """
    Manage user authentication and identity management using a
    standalone licence (instead of OAuth2).

    To use simply change your import for get_current_user():

        if get_settings().AUTH_TYPE is AuthType.STANDALONE:
            from fa_common.auth import get_standalone_user as get_current_user
        else:
            from fa_common.auth import get_current_user

    returns:
        user (AuthUser): The standalone instance user

    raises:
        InternalServerError
    """
    settings = get_settings()
    if settings.AUTH_TYPE is not AuthType.STANDALONE:
        LOG.error(f"AUTH_TYPE must be STANDALONE not {settings.AUTH_TYPE}")
        raise InternalServerError(
            detail="Standalone authentication not enabled",
        )

    return AuthUser(sub="standalone", name="Default User", scopes=["read:me"], email_verified=False, updated_at=None)


async def get_api_key_user(api_key=Depends(get_api_key)) -> AuthUser | None:
    """Simple API Key function that can be overwritten by apps that have user databases."""

    if api_key is not None and api_key != "" and get_settings().MASTER_API_KEY is not None and api_key == get_settings().MASTER_API_KEY:
        # FIXME this might need to be configurable in the future
        return AuthUser(
            sub="standalone",
            name="Default User",
            email="default-user@app.au",
            email_verified=False,
            updated_at=None,
            scopes=["read:me"],
        )
    return None


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    api_key_user=Depends(get_api_key_user),
) -> AuthUser:
    settings = get_settings()
    get_profile = settings.USE_EXTERNAL_PROFILE

    user = None

    try:
        if token is not None and token != "":
            payload = await decode_token(token)
            user = await get_user(payload, token, get_profile)

        elif api_key_user is not None:
            user = api_key_user

    except (JWTError, ValidationError) as e:
        LOG.error("Could not validate credentials. {}", str(e))
        raise UnauthorizedError(
            detail="Could not validate credentials.",
        ) from e

    if not user:
        raise UnauthorizedError(
            detail="Invalid authentication credentials.",
        )

    if settings.ENABLE_SCOPES:
        for scope in security_scopes.scopes:
            if scope not in user.scopes and scope not in user.roles:
                raise ForbiddenError(
                    detail="Not enough permissions",
                )
    return user


async def get_optional_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    api_key_user=Depends(get_api_key_user),
) -> AuthUser | None:
    """
    Identical to get_current_user except returns None when the user
    is not logged in rather than throwing an error.

    Useful for routes that still function for anonymous users but may return different
    results.
    """
    settings = get_settings()
    get_profile = settings.USE_EXTERNAL_PROFILE

    user = None

    try:
        if token is not None and token != "":
            payload = await decode_token(token)
            user = await get_user(payload, token, get_profile)

        elif api_key_user is not None:
            user = api_key_user

    except (JWTError, ValidationError) as e:
        LOG.error("Could not validate credentials. {}", str(e))
        raise UnauthorizedError(
            detail="Could not validate credentials.",
        ) from e

    if not user:
        return None

    if settings.ENABLE_SCOPES:
        for scope in security_scopes.scopes:
            if scope not in user.scopes and scope not in user.roles:
                raise ForbiddenError(
                    detail="Not enough permissions",
                )
    return user


async def get_auth_simple(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), api_key=Depends(get_api_key), get_profile=False
) -> AuthUser:
    return await get_current_user(security_scopes, token, False)


def get_admin_scope() -> str:
    if get_settings().USE_APP_ROLES:
        return PermissionDef.access_scope_name(get_settings().ROOT_APP_SLUG, AccessLevel.ADMIN)

    return get_settings().ADMIN_ROLE
