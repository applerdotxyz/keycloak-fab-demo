Flask-AppBuilder With Keycloak and JWT
=======================================
--------------------------------------------------------------

- Clone the project::

	git clone https://github.com/applerdotxyz/keycloak-fab-demo.git

- Build the docker image::

    	docker compose up --build

  This will run the keycloak at localhost:8000

- Run the fab app::

	flask run --host=0.0.0.0 --port=5000  # --debug --reload (if running on dubug mode add this)

  This will run the FAB app at localhost:5000

That's it!!


