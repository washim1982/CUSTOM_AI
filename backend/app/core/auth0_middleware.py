from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt
import requests
import os

security = HTTPBearer()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

def get_jwk():
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    return requests.get(jwks_url).json()

def verify_jwt(token: str):
    jwks = get_jwk()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = next(
        (
            {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            for key in jwks["keys"]
            if key["kid"] == unverified_header["kid"]
        ),
        None,
    )

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
            return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
    raise HTTPException(status_code=401, detail="Invalid token header")


async def auth0_guard(request: Request):
    token = request.headers.get("Authorization", None)
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = token.split(" ")[1]
    return verify_jwt(token)
