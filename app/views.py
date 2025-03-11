from flask import render_template, g
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi
from app.auth import token_required
from flask import jsonify, request,g
from . import appbuilder, db, app
from app.util import has_role, has_permission
import os
from dotenv import load_dotenv
# Get the parent directory of the current file (views.py)
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load .env file from the parent directory
load_dotenv(dotenv_path=os.path.join(PARENT_DIR, ".env"))
"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

"""
    Application wide 404 error handler
"""
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({
        "message": "This is a protected endpoint!", 
        "user": g.user_data  # Fix here
    })


@app.route('/oauth-authorized/keycloak', methods=['GET'])
# @token_required
def callback():
    import requests
    # Keycloak server details
    keycloak_url = os.getenv("KEYCLOAK_BASE_URL")
    realm = os.getenv("KEYCLOAK_REALM")
    client_id = os.getenv("KEYCLOAK_CLIENT_ID")
    client_secret = os.getenv("KEYCLOAK_CLIENT_SECERT")  # Required for confidential clients
    fab_url = os.getenv("FAB_URL") 
    redirect_uri = f"{fab_url}/oauth-authorized/keycloak"  # Must match the redirect URI used in the initial request

    # Token endpoint
    token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"

    # Authorization code received from Keycloak
    code = request.args['code']

    # Request payload
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    # Send POST request to get the tokens
    response = requests.post(token_url, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)
        return jsonify({"message": "This is a redirected endpoint!", "token_data": token_data})
    else:
        print("Failed to fetch tokens")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        response_dict = {
            "status_code": response.status_code,
            "reason": response.reason,
            "headers": dict(response.headers),
            "text": response.text,
        }
        return jsonify({"message": "This is a redirected endpoint!", "response": response_dict})
    

@app.route('/unprotected', methods=['GET'])
def unprotected():
    return jsonify({"message": "This is an unprotected endpoint!"})


@app.route('/admin', methods=['GET'])
@token_required
@has_permission("account",["manage-account"])
#@has_role("default-roles-my-realm")
def admin_only():
    return jsonify({
        "message": "Welcome, Admin!",
        "user": g.user_data
    })


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()
