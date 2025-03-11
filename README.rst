Flask-AppBuilder With Keycloak and JWT
=======================================

Clone the Project
-----------------

- Clone the project:

  .. code-block:: bash

     git clone https://github.com/applerdotxyz/keycloak-fab-demo.git

Install Virtual Environment
----------------------------

- Install virtual environment:

  .. code-block:: bash

     pip install virtualenv

- Create a virtual environment:

  .. code-block:: bash

     virtualenv env

- Activate the virtual environment:

  .. code-block:: powershell

     ./env/Scripts/activate.ps1

- Install dependencies:

  .. code-block:: bash

     pip install -r requirements.txt

Run Tests with SeleniumBase
----------------------------

- Run the project through pytest with SeleniumBase:

  .. code-block:: bash

     pytest pytest-Keycloak.py --html=report.html

- Open a browser and go to `http://localhost:8080/`, then log in with the credentials:

  **Username:** admin  
  **Password:** admin  

- Click the dropdown menu next to the realm name and select the realm:

  **Realm Name:** `myrealm` (or whatever realm name you choose)

- Click on **Realm Settings** in the left menu, then go to the **Keys** tab.

- Click on the **Public Key** for **Algorithm RS256**, copy the key, and paste it into `.env` under the `PUBLIC_KEY` variable.

Run the Flask AppBuilder (FAB) App
-----------------------------------

- Run the FAB app:

  .. code-block:: bash

     pytest pytest-fab.py --html=report.html

- Run API tests:

  .. code-block:: bash

     pytest pytest-api.py -v

**Note:** SeleniumBase may have timing errors. If a test fails, try running it again.  
If you want to change the realm, user, or client name, update the `.env` file.

Debugging Keycloak and FAB App
-------------------------------

- To run Keycloak and the FAB app for debugging:

  1. Start the Keycloak server:

     .. code-block:: bash

        docker compose up --build

  2. Run the FAB app:

     .. code-block:: bash

        flask run --host=0.0.0.0 --port=5000

That's it!
