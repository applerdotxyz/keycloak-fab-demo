import requests
import jwt
from flask import request, jsonify, g
from functools import wraps

KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "my-realm"
CLIENT_ID = "my-fab-app"
PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

'''
session = requests.Session()  # Reuse session for better performance
def get_public_key():
    """Fetches the public RSA key from Keycloak with better error handling."""
    print("Fetching public key")
    try:
        response = session.get(PUBLIC_KEY_URL, timeout=15)
        response.raise_for_status()  # Raises HTTPError if the request fails
        
        jwks = response.json()
        keys = jwks.get("keys", [])

        if not keys:
            raise ValueError("No public keys found in JWKS response")

        # Extract and convert key
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(keys[0])
        return public_key

    except requests.exceptions.Timeout:
        print("Error: Request timed out while fetching public key.")
    except requests.exceptions.ConnectionError:
        pdb.set_trace()
        print("Error: Could not connect to Keycloak server.")
    except requests.exceptions.HTTPError as e:
        pdb.set_trace()
        print(f"HTTP Error: {e}")
    except (ValueError, KeyError) as e:
        pdb.set_trace()
        print(f"Error processing JWKS response: {e}")

    return None  # Return None on failure
'''
'''
def get_public_key():
   #Fetches the public RSA key from Keycloak.
    try:
        response = requests.get(PUBLIC_KEY_URL, timeout=15)  # Add timeout for robustness
        response.raise_for_status()
        jwks = response.json()

        if 'keys' not in jwks or not jwks['keys']:
            raise ValueError("No public keys found in JWKS response")

        return jwt.algorithms.RSAAlgorithm.from_jwk(jwks['keys'][0])

    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching public key: {e}")
        return None  # Handle in token_required
'''

#Hardcoded public key for testing.


def get_public_key():
    
    public_key_pem = """
   -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnDjQ4+Za9sENWDrL5IEy
yAygejAqqN5CKVCo2fbye1aYKlaCKw5drGPpXNxmt6OU0a5jPcoyfw9tsQfr7z5g
TE00oJ17QGqntxYfy3h0aGpMQj8OMqYk/zaz5UzClznllK5vc5JdUygHK55WeGZ9
CuiCUPuWCUIWzuaAsj/QXhue/QoG1GTbBrH+44cJVTfp3saCFEYQm1MTWENvw621
PG+OWdGj8dh1cNRyN8lGNhqjY7mpOpoM04DAqxw4iCWJHW5tDKTB/tICyLoHFZcO
1/zlpIDYibsfa4KP/MPxWVk8tO6t8SOchgML/yhg3VU/yG2bwMPXDbp3xlNAJeIl
3wIDAQAB
-----END PUBLIC KEY-----
    """
    return public_key_pem

def token_required(f):
    """Decorator to validate JWT tokens from the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.headers.get("Authorization"):
            return jsonify({"message": "Authorization header missing!"}), 401

        auth_header = request.headers["Authorization"].strip()

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Invalid authorization header format!"}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else None

        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            public_key = get_public_key()
            if not public_key:
                return jsonify({"message": "Failed to fetch public key!"}), 500

            data = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})

            # Manually check audience (Keycloak may use azp instead of aud)
            if data.get("aud") != CLIENT_ID and data.get("azp") != CLIENT_ID:
                return jsonify({"message": "Invalid audience!"}), 401

            g.user_data = data  # Store token data in Flask's global context

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated
