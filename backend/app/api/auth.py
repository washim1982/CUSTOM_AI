from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
import os
import logging

router = APIRouter()

# -----------------------------------------------------------------------------
# Auth0 config from env
# -----------------------------------------------------------------------------
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

if not AUTH0_DOMAIN:
    logging.warning("⚠ AUTH0_DOMAIN is not set. Auth will treat all users as anonymous.")
if not AUTH0_AUDIENCE:
    logging.warning("⚠ AUTH0_AUDIENCE is not set. Token audience will not be enforced.")

bearer_scheme = HTTPBearer(auto_error=False)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _get_jwks():
    """
    Fetch JWKs from Auth0. We cache them to avoid hitting Auth0 all the time.
    """
    # Lazy import to avoid doing requests on module import
    import requests
    global _CACHED_JWKS
    if "_CACHED_JWKS" in globals() and _CACHED_JWKS:
        return _CACHED_JWKS

    if not AUTH0_DOMAIN:
        raise RuntimeError("AUTH0_DOMAIN not configured")

    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    resp = requests.get(jwks_url, timeout=5)
    resp.raise_for_status()
    _CACHED_JWKS = resp.json()
    return _CACHED_JWKS


def _verify_jwt(token: str) -> Dict[str, Any]:
    """
    Verify the Auth0 JWT using the JWKs and return decoded claims.
    """
    if not AUTH0_DOMAIN:
        raise HTTPException(status_code=401, detail="Auth0 not configured")

    jwks = _get_jwks()
    unverified_header = jwt.get_unverified_header(token)

    kid = unverified_header.get("kid")
    key = None
    for jwk in jwks["keys"]:
        if jwk["kid"] == kid:
            key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
            break
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token header (kid not found)")

    options = {
        "verify_aud": bool(AUTH0_AUDIENCE),
        "verify_signature": True,
        "verify_iss": True,
        "verify_exp": True,
    }

    decoded = jwt.decode(
        token,
        key=key,
        algorithms=["RS256"],
        audience=AUTH0_AUDIENCE if AUTH0_AUDIENCE else None,
        issuer=f"https://{AUTH0_DOMAIN}/",
        options=options,
    )
    return decoded


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """
    - If no Authorization header: return None (anonymous user).
    - If we DO get a token: validate and return claims.
    """
    if creds is None:
        # anonymous access allowed in some endpoints
        return None

    token = creds.credentials
    try:
        userinfo = _verify_jwt(token)
        return userinfo
    except Exception as e:
        logging.warning(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/me")
async def get_user_profile(user = Depends(get_current_user)):
    """
    Used by frontend to know if user is logged in.
    Returns { authenticated: bool, name/email/... }
    """
    if not user:
        return {"authenticated": False}

    # Prefer name, then email, then sub.
    display_name = user.get("name") or user.get("email") or user.get("sub")
    return {
        "authenticated": True,
        "name": display_name,
        "raw": user,
    }
