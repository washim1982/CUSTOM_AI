# backend/app/core/auth0.py
import json
from functools import lru_cache
from typing import Dict
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import requests
import os

# --- Security scheme ---
auth_scheme = HTTPBearer()

# --- Auth0 Configuration ---
@lru_cache()
def get_auth0_settings() -> Dict[str, str]:
    return {
        "domain": os.getenv("AUTH0_DOMAIN"),
        "api_audience": os.getenv("AUTH0_AUDIENCE"),
        "issuer": f"https://{os.getenv('AUTH0_DOMAIN')}/",
        "algorithms": ["RS256"],
    }

# --- Fetch and cache JWKS (public keys) from Auth0 ---
@lru_cache()
def get_jwks() -> Dict:
    domain = os.getenv("AUTH0_DOMAIN")
    jwks_url = f"https://{domain}/.well-known/jwks.json"
    response = requests.get(jwks_url, timeout=10)
    response.raise_for_status()
    return response.json()

# --- Token Verification ---
def verify_jwt_token(token: str) -> Dict:
    settings = get_auth0_settings()
    jwks = get_jwks()

    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break

    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
        )

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=settings["algorithms"],
            audience=settings["api_audience"],
            issuer=settings["issuer"],
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token validation error: {str(e)}")

# --- Dependency for FastAPI routes ---
async def get_current_user(request: Request, credentials=Depends(auth_scheme)):
    token = credentials.credentials
    return verify_jwt_token(token)
