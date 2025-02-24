from functools import wraps
import jwt
from flask import request, jsonify
import requests

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "my-realm"
CLIENT_ID = "my-fab-app"
# URL to fetch the public key from Keycloak
PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

# Fetch the public key from Keycloak
def get_public_key():
    response = requests.get(PUBLIC_KEY_URL)
    # response.raise_for_status()
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
            # public_key = {
            #     "kid": "8_VhKcQMNa2nnxlrUrUKfAa1RtHOb8XlUEcmywYm060",
            #     "kty": "RSA",
            #     "alg": "RSA-OAEP",
            #     "use": "enc",
            #     "n": "5R4k6vcL51M30q7isN8v4OfW8eKYnPPnmr7LkeBYNdVrs_T5yNHgyCPObygfc6v47tFEE7f9P5j1x23t_Uy6EJJUBRpwU6KE1v8J0o0bmFpRW6N9oAaCChdmQY58a_gEMcZmnaQFNZUpumRqvQn1V5JA_aiKtp6VAXG99ZsRKc5wKywqdSbv_k8UOsHVknchr49Hv7soVSrV4p5rxzVW9G1Tm1Uz8kzLUEuW0o2b12hzllaTgz5Pyz3NLINqxTR6kw-epwZAg_o7k9kttAcxZ4oTQ0CKc_7aAgUst1U7TlkWyq4523RQHeoHZFF7qssIDULFrOAxqfOeaWqD9T2FIQ",
            #     "e": "AQAB",
            #     "x5c": [
            #         "MIICnzCCAYcCBgGVKZZ5QzANBgkqhkiG9w0BAQsFADATMREwDwYDVQQDDAhteS1yZWFsbTAeFw0yNTAyMjExNzM2MjJaFw0zNTAyMjExNzM4MDJaMBMxETAPBgNVBAMMCG15LXJlYWxtMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5R4k6vcL51M30q7isN8v4OfW8eKYnPPnmr7LkeBYNdVrs/T5yNHgyCPObygfc6v47tFEE7f9P5j1x23t/Uy6EJJUBRpwU6KE1v8J0o0bmFpRW6N9oAaCChdmQY58a/gEMcZmnaQFNZUpumRqvQn1V5JA/aiKtp6VAXG99ZsRKc5wKywqdSbv/k8UOsHVknchr49Hv7soVSrV4p5rxzVW9G1Tm1Uz8kzLUEuW0o2b12hzllaTgz5Pyz3NLINqxTR6kw+epwZAg/o7k9kttAcxZ4oTQ0CKc/7aAgUst1U7TlkWyq4523RQHeoHZFF7qssIDULFrOAxqfOeaWqD9T2FIQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQDSeUGxYX4nK1F9s1W453w6qGuX/mQ0zTFkPFmCM1uLOTAcsrHB9gIesHEJvyOMNeH1Pz8sPPb4+izF8DPPrusmsrNtLLqzcBFaZf7DLflxQnGQdYB6VOzp2Urz2yIgGkl7wdhjAk1v9l1Yf8FBWIk8Wu3ST7qLMnjAymLkuOWJj6tCozHR1h79Ft2Vemlch1KQEIia28YRBRYpnWs7vOQiOqN59PGEgpK22xUzT+BvLefCUtdajGhWZr12mY9kmmUP4dEYteNxtZ5kpuqKh1C0mW6DS8KCEk7CrEpHbrmkrQEV7JEiEBY1WSbUlADW4KPSfUVkgLDMJirk2uGlWWtJ"
            #     ],
            #     "x5t": "0A7SH-YurP21gb80ENAiCgdWY-I",
            #     "x5t#S256": "0RJS_k3cHtDwmfEpgXPxq82B5nQQI7270mmZSCgNwxc"
            #     }    
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