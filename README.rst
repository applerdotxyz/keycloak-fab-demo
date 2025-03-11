Flask-AppBuilder With Keycloak and JWT
=======================================
--------------------------------------------------------------

- Clone the project::
    git clone https://github.com/Ashutoshgkp/FlaskAppBuilder.git

- Build the docker image::
    $ docker compose up --build

  This will run the keycloak at localhost:8000
- Go to localhost:8000
- Create a Realm
- Create a client
- Create a User
  - give that User a Password. Set Temporary to off.
----------------------------------------------------------------

- Create a .env file in your project folder.

- add client id, client secret, realm-name and keycloak base url (in this case localhost:8080) from the Keycloak console in this format::

	KEYCLOAK_BASE_URL=<Your-Keycloak-url>

	KEYCLOAK_REALM=<Your-realm-name>  

	KEYCLOAK_CLIENT_ID=<Your-client-id>  

	KEYCLOAK_CLIENT_SECRET=<Your-client-secret>  


- Make a virtual enviroment::

	virtaulenv env
- Launch the virtual enviroment::

	./env/Scripts/activate.ps1
- Install dependencies::

	pip install -r Requirement.txt

- Run the fab app::

	flask run --host=0.0.0.0 --port=5000  # --debug --reload (if running on dubug mode add this)

  This will run the FAB app at localhost:5000

That's it!!


