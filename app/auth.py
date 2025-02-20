from functools import wraps
import jwt
from flask import request, jsonify
import requests

# Keycloak configuration
KEYCLOAK_URL = "http://127.0.0.1:8080/auth"
REALM_NAME = "myrealm"
CLIENT_ID = "my-fab-app"
# URL to fetch the public key from Keycloak
PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

# Fetch the public key from Keycloak
def get_public_key():
    response = requests.get(PUBLIC_KEY_URL)
    response.raise_for_status()
    jwks = response.json()
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks['keys'][0])
    return public_key

# Decorator to validate JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get the token from the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Decode and validate the token
            public_key = get_public_key()
            data = jwt.decode(token, public_key, algorithms=["RS256"], audience=CLIENT_ID)
            # Optionally, you can add more checks here (e.g., roles, expiration, etc.)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        # Attach the decoded token data to the request object
        request.user_data = data
        return f(*args, **kwargs)

    return decorated