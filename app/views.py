from flask import render_template, g
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi
from app.auth import token_required
from flask import jsonify, request
from . import appbuilder, db, app

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
    return jsonify({"message": "This is a protected endpoint!", "user": request.user_data})


@app.route('/oauth-authorized/keycloak', methods=['GET'])
# @token_required
def callback():
    import requests

    # Keycloak server details
    keycloak_url = "http://host.docker.internal:8080"
    realm = "my-realm"
    client_id = "my-fab-app"
    client_secret = "BO1El7S5k0maN5D4Nh20bgN1CS4qsDSA"  # Required for confidential clients
    redirect_uri = "http://localhost:5000/oauth-authorized/keycloak"  # Must match the redirect URI used in the initial request

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
        return jsonify({"message": "This is a redirected endpoint!", "response": response.__dict__})
    

@app.route('/unprotected', methods=['GET'])
def unprotected():
    return jsonify({"message": "This is an unprotected endpoint!"})


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()
