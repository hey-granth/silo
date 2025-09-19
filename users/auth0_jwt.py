import requests
from typing import Any
from jose import jwk, jwt
from jose.utils import base64url_decode
from config import Config


JWKS_URL = f"https://{Config.AUTH0_DOMAIN}/.well-known/jwks.json"


def get_jwks() -> requests.Response:
    return requests.get(JWKS_URL).json()


def verify_jwt(token) -> dict[str, Any]:
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    if not rsa_key:
        raise Exception("Unable to find appropriate key")

    public_key = jwk.construct(rsa_key)
    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise Exception("Signature verification failed")

    payload = jwt.decode(
        token,
        public_key,
        algorithms=Config.AUTH0_ALGORITHMS,
        audience=Config.AUTH0_AUDIENCE,
        issuer=f"https://{Config.AUTH0_DOMAIN}/",
    )
    return payload
