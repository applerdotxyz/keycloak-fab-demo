import os
import requests
import jwt
from flask import request, jsonify, g
from functools import wraps
from dotenv import load_dotenv

# Load .env file from the parent directory
load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_BASE_URL")
REALM_NAME = os.getenv("KEYCLOAK_REALM")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

if not PUBLIC_KEY:
    raise ValueError("Public key not found in .env file")

# Ensure the newlines are properly interpreted
PUBLIC_KEY = PUBLIC_KEY.replace("\\n", "\n")

PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

session = requests.Session()  # Reuse session for better performance

# Commented out the get_public_key function, using hardcoded key instead
# def get_public_key():
#     try:
#         response = session.get(PUBLIC_KEY_URL, timeout=15)
#         response.raise_for_status()
#         jwks = response.json()
#         if 'keys' not in jwks or not jwks['keys']:
#             raise ValueError("No public keys found in JWKS response")
#         return jwt.algorithms.RSAAlgorithm.from_jwk(jwks['keys'][0])
#     except (requests.RequestException, ValueError, KeyError) as e:
#         return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid authorization header!"}), 401

        token = auth_header.split(" ")[1]

        try:
            decoded_token = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=["RS256"],
                options={"verify_aud": False},
                issuer=f"{KEYCLOAK_URL}/realms/{REALM_NAME}"
            )

            if decoded_token.get("aud") != CLIENT_ID and decoded_token.get("azp") != CLIENT_ID:
                return jsonify({"message": "Invalid audience!"}), 401

            g.user_data = decoded_token
            g.user_identity = decoded_token.get("sub")

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"message": "Invalid token!", "Error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated
